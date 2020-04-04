import sys
import os
import math
import enum
from datetime import timedelta
import Telex
from Telex_utils import resource


class Wall(enum.Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    BOTTOM = 3
    TOP = 4


class Bullet:
    def __init__(self, image, direction, x, y, width, height):
        self.direction = direction
        self.speed = 10.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.step_x = math.sin(direction) * self.speed
        self.step_y = math.cos(direction) * self.speed

    def step(self):
        self.x += self.step_x
        self.y += self.step_y

    def test_inside(self, x, y, width, height):
        if self.x < x:
            return Wall.LEFT
        if self.x + self.width > x + width:
            return Wall.RIGHT
        if self.y < y:
            return Wall.TOP
        if self.y + self.height > y + height:
            return Wall.BOTTOM
        return Wall.NONE

    def turn(self, wall):
        if wall == Wall.LEFT or wall == Wall.RIGHT:
            self.step_x *= -1.0
        if wall == Wall.TOP or wall == Wall.BOTTOM:
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

    @staticmethod
    def _get(name, images):
        for im in images:
            if im[0].startswith(name):
                return im[1]
        return None

    def start(self):
        rect = self.canvas.rect()
        self.width = rect.width
        self.height = rect.height
        self.ui.start_timer(timedelta(milliseconds=10), False, self.game_loop)

    def game_loop(self):
        self.canvas.erase()
        for bullet in self.bullets:
            bullet.step()
            wall = bullet.test_inside(0, 0, self.width, self.height)
            if wall != Wall.NONE:
                bullet.turn(wall)
                bullet.step()
            self.canvas.paint_image_rect(self.bullet, Telex.Rect(bullet.x, bullet.y, bullet.width, bullet.height))

        #  self.canvas.paint_image(self.barrel, 10, 10)
        #  self.canvas.paint_image(self.barrier, 10, 50)
        #  self.canvas.paint_image(self.bullet, 10, 100)
        #  self.canvas.paint_image(self.dome, 10, 150)
        #  self.canvas.paint_image(self.numbers, 10, 200)
        # self.canvas.paint_image(self.skull, 10, 250)

    def shoot(self):
        self.bullets.append(Bullet(self.bullet, 1.0, 200, 400, 20, 20))


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

    Telex.Element(ui, "shoot").subscribe("click", lambda _: game.shoot())

    ui.run()


if __name__ == "__main__":
    # Telex.set_debug()
    main()

