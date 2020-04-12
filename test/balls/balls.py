import sys
import os
import math
import random
from datetime import timedelta
import Telex
from Telex_utils import resource


class Number:
    def __init__(self, images):
        self.images = images

    def draw(self, g, x, y, width, height, value):
        #g.extend(["drawImageClip", self.images, x, y, width, height, self.n_width * value, 0, self.n_width, self.height])
        g.extend(
            ["drawImageClip", self.images, 13 * value, 0, 13, 25, x, y, width, height])


class Monster:
    def __init__(self, x, y, width, height, endurance, numbers):
        self.speed = 1.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.numbers = numbers
        self.endurance = endurance

    def step(self):
        self.y += self.speed

    def test_inside(self, x, y, width, height):
        return self.y + self.height > y + height

    def draw(self, g, image):
        g.extend(["drawImageRect", image, self.x, self.y, self.width, self.height])
        f1 = int(self.endurance / 10)
        f2 = self.endurance - (f1 * 10)
        self.numbers.draw(g, self.x + 6, self.y + 6, 10, 10, f1)
        self.numbers.draw(g, self.x + 24, self.y + 6, 10, 10, f2)


class Bullet:
    def __init__(self, direction, x, y, width, height):
        self.speed = 2.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.step_x = math.sin(direction) * self.speed
        self.step_y = math.cos(direction) * self.speed
        self.hit_in = False

    def step(self):
        self.x += self.step_x
        self.y += self.step_y

    def test_inside(self, x, y, width, height):
        if self.x < x:
            self.step_x *= -1.0
            self.x = x
        elif self.x + self.width > x + width:
            self.step_x *= -1.0
            self.x = width - self.width
        elif self.y < y:
            self.step_y *= -1.0
            self.y = y
        elif self.y + self.height > y + height:
            self.step_y *= -1.0
            self.y = height - self.height
            return True
        return False

    def test_hit(self, other):
        ox = other.x + other.width
        oy = other.y + other.height
        sx = self.x + self.width
        sy = self.y + self.height

        mx = self.x + self.step_x < ox and sx + self.step_x > other.x and (self.y < oy and sy > other.y)
        my = self.y + self.step_y < oy and sy + self.step_y > other.y and (self.x < ox and sx > other.x)

        has_hit = False

        if mx and my and not self.hit_in:
            dx = min(sx, ox) - max(other.x, self.x)
            dy = min(sy, oy) - max(other.y, self.y)
            if dx < dy:
                my = False
            else:
                mx = False
        if mx and not self.hit_in:
            self.step_x *= -1.0
            has_hit = True
        if my and not self.hit_in:
            self.step_y *= -1.0
            has_hit = True

        self.hit_in = mx or my
        return has_hit

    def draw(self, g, image):
        g.extend(["drawImageRect", image, self.x, self.y, self.width, self.height])


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
        self.numberDrawer = None

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
        self.numberDrawer = Number(self.numbers)

    def create_monster(self, x_pos):
        self.monsters.append(Monster(x_pos, -40, 40, 40, random.randint(1, 99), self.numberDrawer))

    def start(self):
        self.ui.start_timer(timedelta(milliseconds=50), False, self.game_loop)
        self.create_monster(random.randint(0, self.width - 40))

    def game_loop(self):
        command_list = ["clearRect", 0, 0, self.width, self.height]

        for bullet in self.bullets:
            bullet.step()
            to_delete = bullet.test_inside(0, 0, self.width, self.height)
            if to_delete:
                self.bullets.remove(bullet)
            else:
                bullet.step()
                for monster in self.monsters:
                    if bullet.test_hit(monster):
                        monster.endurance -= 1
                        if monster.endurance <= 0:
                            self.monsters.remove(monster)
                    bullet.step()
                bullet.draw(command_list, self.bullet)

        gaps = []
        for monster in self.monsters:
            monster.step()
            if monster.y < 0:
                gaps.append(monster.x)
            monster.draw(command_list, self.skull)
            to_delete = monster.test_inside(0, 0, self.width, self.height)
            if to_delete:
                self.monsters.remove(monster)

        if random.randint(0, 50) == 5:
            x_pos = random.randint(0, self.width - 40)
            is_ok = True
            for x in gaps:
                if (x_pos > x) and (x_pos < x + 40):
                    is_ok = False
                    break
            if is_ok:
                self.create_monster(x_pos)

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

