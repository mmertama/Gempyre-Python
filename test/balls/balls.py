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
        g.draw_image_clip(self.images, Telex.Rect(13 * value, 0, 13, 25), Telex.Rect(x, y, width, height))


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
        g.draw_image_rect(image, Telex.Rect(self.x, self.y, self.width, self.height))
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
        g.draw_image_rect(image, Telex.Rect(self.x, self.y, self.width, self.height))


class Gun:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.width = 100

    def draw(self, g, dome_image, barrel_image):
        g.draw_image_rect(dome_image, Telex.Rect(self.x - 50, self.y - 50, 100, 50))
        g.save()
        g.translate(self.x, self.y - 20)
        g.rotate(self.angle)
        g.translate(-self.x, -(self.y - 20))
        g.draw_image_rect(barrel_image, Telex.Rect(self.x - 5, self.y - 90, 10, 40))
        g.restore()


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
        self.numberDrawer = None
        self.gun = None

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
        self.gun = Gun(self.width / 2, self.height - 10)

    def create_monster(self, x_pos):
        self.monsters.append(Monster(x_pos, -40, 40, 40, random.randint(1, 99), self.numberDrawer))

    def start(self):
        self.ui.start_timer(timedelta(milliseconds=50), False, self.game_loop)
        self.create_monster(random.randint(0, self.width - 40))

    def game_loop(self):
        fc = Telex.FrameComposer()
        fc.clear_rect(Telex.Rect(0, 0, self.width, self.height))

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
                bullet.draw(fc, self.bullet)

        gaps = []
        for monster in self.monsters:
            monster.step()
            if monster.y < 0:
                gaps.append(monster.x)
            monster.draw(fc, self.skull)
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
        self.gun.draw(fc, self.dome, self.barrel)
        self.canvas.draw_frame(fc)

    def shoot(self):
        start_x = (self.gun.x - 10) + 110 * math.sin(self.gun.angle)
        start_y = (self.width - 30 - 10) - 110 * math.cos(self.gun.angle)
        self.bullets.append(Bullet(math.pi - self.gun.angle, start_x, start_y, 20, 20))

    def turret(self, angle):
        self.gun.angle = angle

    def gun_move(self, x):
        if (self.gun.x - (self.gun.width / 2) + x > 0) and (self.gun.x + (self.gun.width / 2) + x < self.width):
            self.gun.x += x


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

    canvas.subscribe('mousemove', lambda e: game.turret(get_property(e)),
                     ["clientX", "clientY"], timedelta(milliseconds=100))

    def key_listen(e):
        code = int(float((e.properties['keyCode'])))
        if code == ord('Z') or code == 37: #left arrow
            game.gun_move(-2)
        if code == ord('X') or code == 39: #right arrow
            game.gun_move(2)

    # canvas is not focusable therefore we listen whole app
    ui.root().subscribe('keydown', key_listen, ['keyCode'])
    ui.run()


if __name__ == "__main__":
    #Telex.set_debug()
    main()

