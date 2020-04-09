import sys
import os
import math
import enum
import random
from datetime import timedelta
import Telex
from Telex_utils import resource


class Hit(enum.Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    BOTTOM = 3
    TOP = 4


class Monster:
    def __init__(self, x, y, width, height):
        self.speed = 3.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius2 = width * width + height * height

    def step(self):
        self.y += self.speed

    def test_inside(self, x, y, width, height):
        if self.y + self.height > y + height:
            return Hit.BOTTOM
        return Hit.NONE


class Bullet:
    def __init__(self, direction, x, y, width, height):
        self.direction = direction
        self.speed = 3.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.step_x = math.sin(direction) * self.speed
        self.step_y = math.cos(direction) * self.speed
        self.radius2 = width *  width + height * height
        self.hit_in = False

    def step(self):
        self.x += self.step_x
        self.y += self.step_y

    def test_inside(self, x, y, width, height):
        if self.x < x:
            return Hit.LEFT
        if self.x + self.width > x + width:
            return Hit.RIGHT
        if self.y < y:
            return Hit.TOP
        if self.y + self.height > y + height:
            return Hit.BOTTOM
        return Hit.NONE

    def test_outside(self, x, y, radius2):
        dx = self.x - x
        dy = self.y - y
        d = dx * dx + dy * dy
        if d <= self.radius2 + radius2:
            if self.hit_in:
                return Hit.NONE
            self.hit_in = True
            h = self.x - x
            v = self.y - y
            if h < v:
                return Hit.LEFT if h > 0 else Hit.RIGHT
            else:
                return Hit.TOP if v > 0 else Hit.BOTTOM
        if self.hit_in:
            self.hit_in = False
        return Hit.NONE

    def turn(self, wall):
        if wall == Hit.LEFT or wall == Hit.RIGHT:
            self.step_x *= -1.0
        if wall == Hit.TOP or wall == Hit.BOTTOM:
            self.step_y *= -1.0


class Game:
    def __init__(self, ui, canvas, images):
        self.ui = ui
        self.canvas = canvas
        self.barrel = self._get("barrel", images)
        self.barrier = self._get("barrier", images)
        self.bullet = self._get("bullet", images)
        self.dome = self._get("dome", images)
        self.numbers = self._get("numbers", images)
        self.skull = self._get("skull", images)
        self.width = 0
        self.height = 0
        self.bullets = []
        self.monsters = []
        self.rect = None
        self.angle = 0

    @staticmethod
    def _get(name, images):
        for im in images:
            if im[0].startswith(name):
                return im[1]
        return None

    def init(self):
        self.rect = self.canvas.rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def start(self):
        self.ui.start_timer(timedelta(milliseconds=30), False, self.game_loop)
        self.monsters.append(Monster(random.randint(0, self.width - 40), -40, 40, 40))

    def game_loop(self):
        command_list = ["clearRect", 0, 0, self.width, self.height]

        for bullet in self.bullets:
            bullet.step()
            wall = bullet.test_inside(0, 0, self.width, self.height)
            if wall != Hit.NONE:
                bullet.turn(wall)
                bullet.step()
            for monster in self.monsters:
                hit = bullet.test_outside(monster.x, monster.y, monster.radius2)
                if hit != Hit.NONE:
                    bullet.turn(hit)
                    bullet.step()
            command_list.extend(["drawImageRect", self.bullet, bullet.x, bullet.y, bullet.width, bullet.height])

        for monster in self.monsters:
            monster.step()
            command_list.extend(["drawImageRect", self.skull, monster.x, monster.y, monster.width, monster.height])
            wall = monster.test_inside(0, 0, self.width, self.height)
            if wall == Hit.BOTTOM:
                self.monsters.remove(monster)
                self.monsters.append(Monster(random.randint(0, self.width - 40), -40, 40, 40))

        command_list.extend(["drawImageRect", self.dome, self.width / 2 - 50, self.height - 60, 100, 50])
        command_list.extend([
                         "save",
                         "translate", (self.width / 2), (self.width - 30),
                         "rotate", self.angle,
                         "translate", -(self.width / 2), -(self.width - 30),
                         "drawImageRect", self.barrel, self.width / 2 - 5, self.width - 100, 10, 40,
                         "restore"
                        ])
        self.canvas.draw(command_list)

    def shoot(self):
        start_x = (self.width / 2 - 10) + 110 * math.sin(self.angle)
        start_y = (self.width - 30 - 10) - 110 * math.cos(self.angle)
        self.bullets.append(Bullet(math.pi - self.angle, start_x, start_y, 20, 20))

    def turret(self, angle):
        self.angle = angle


def main():
    root = os.path.dirname(sys.argv[0]) + '/assets/'
    files = ["balls.html", "barrel.png", "barrier.png", "bullet.png", "dome.png", "numbers.png", "skull.png"]
    full_paths = list(map(lambda f: root + f, files))
    data_map, names = resource.from_file_list(full_paths)

    # make list of image URIs from names
    urls = []
    for i in range(1, len(full_paths)):
        urls.append(names[full_paths[i]])

    ui = Telex.Ui(data_map, names[full_paths[0]])
    canvas = Telex.CanvasElement(ui, 'canvas')

    images = canvas.add_images(urls, lambda _: game.start())
    game = Game(ui, canvas, zip(files[1:], images))

    canvas.subscribe("click", lambda _: game.shoot())

    ui.on_open(lambda: game.init())

    def get_property(event):
        if event:
            nonlocal game
            x = float(event.properties["clientX"])
            y = float(event.properties["clientY"])
            mid_x = game.rect.width / 2
            return math.atan2((game.rect.height - y), mid_x - x) - math.pi / 2
        return 0

    canvas.subscribe("mousemove", lambda e: game.turret(get_property(e)),
                     ["clientX", "clientY"], timedelta(milliseconds=100))

    ui.run()


if __name__ == "__main__":
    #Telex.set_debug()
    main()

