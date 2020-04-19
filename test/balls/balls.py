import sys
import os
import math
import random
from datetime import timedelta
from datetime import datetime
import Telex
from Telex_utils import resource

TICK_SPEED = 30
MONSTER_SPEED = 0.15
BULLET_SPEED = 1.0
GUN_SPEED = 5.0
NUMBERS_WIDTH = 13
NUMBERS_HEIGHT = 25
BULLET_WIDTH = 20
BULLET_HEIGHT = 20
GUN_HEIGHT = 50
GUN_WIDTH = 100
BARREL_WIDTH = 10
BARREL_HEIGHT = 40
MONSTER_WIDTH = 40
MONSTER_HEIGHT = 40
TURRET_STEP = 0.01
MAX_AMMO = 100
MAX_GAME_SPEED = 50


class Number:
    def __init__(self, images):
        self.images = images

    def draw(self, g, x, y, width, height, value):
        g.draw_image_clip(self.images, Telex.Rect(
            NUMBERS_WIDTH * value, 0, NUMBERS_WIDTH, NUMBERS_HEIGHT), Telex.Rect(x, y, width, height))


class Monster:
    def __init__(self, x, y, width, height, endurance, numbers):
        self.step_y = MONSTER_SPEED
        self.step_x = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.numbers = numbers
        self.endurance = endurance

    def step(self):
        self.y += self.step_y

    def test_inside(self, x, y, width, height):
        return self.y + self.height > y + height

    def draw(self, g, image):
        g.draw_image_rect(image, Telex.Rect(self.x, self.y, self.width, self.height))
        f1 = int(self.endurance / 10)
        f2 = self.endurance - (f1 * 10)
        self.numbers.draw(g, self.x + 6, self.y + 6, 10, 10, f1)
        self.numbers.draw(g, self.x + 24, self.y + 6, 10, 10, f2)


class Bullet:
    def __init__(self, direction, x, y):
        self.speed = BULLET_SPEED
        self.x = x
        self.y = y
        self.step_x = math.sin(direction) * self.speed
        self.step_y = math.cos(direction) * self.speed
        self.hit_in = None
        self.LEFT = 1
        self.TOP = 2
        self.RIGHT = 4
        self.BOTTOM = 8

    def step(self):
        self.x += self.step_x
        self.y += self.step_y

    def test_inside(self, x, y, width, height):
        if self.x < x:
            self.step_x *= -1.0
            self.x = x
        elif self.x + BULLET_WIDTH > x + width:
            self.step_x *= -1.0
            self.x = width - BULLET_WIDTH
        elif self.y < y:
            self.step_y *= -1.0
            self.y = y
        elif self.y + BULLET_HEIGHT > y + height:
            self.step_y *= -1.0
            self.y = height - BULLET_HEIGHT
            return True
        return False

    def is_inside(self, other):
        d_dir = 0
        if self.x <= other.x:
            d_dir |= self.LEFT
        if self.x + BULLET_WIDTH >= other.x + other.width:
            d_dir |= self.RIGHT
        if self.y <= other.y:
            d_dir |= self.TOP
        if self.y + BULLET_HEIGHT >= other.y + other.height:
            d_dir |= self.BOTTOM
        return d_dir

    '''
    def test_hit(self, other):
        ox = other.x + other.width
        oy = other.y + other.height
        sx = self.x + BULLET_WIDTH
        sy = self.y + BULLET_HEIGHT
        '''
    '''
        if (self.x < ox and sx > other.x) and (self.y < oy and sy > other.y): #already in!
            dx1 = ox - self.x
            dx2 = sx - other.x
            dy1 = oy - self.y
            dy2 = sy - other.y

            if self.step_x > self.step_y:
                if dx1 < dx2:
                    self.x += dx1
                else:
                    self.x -= dx2
            else:
                if dy1 < dy2:
                    self.y += dy1
                else:
                    self.y -= dy2
    '''
    '''
        hit_x = self.x + self.step_x < ox + other.step_x and sx + self.step_x > other.x + other.step_x and (self.y < oy and sy > other.y)
        hit_y = self.y + self.step_y < oy + other.step_y and sy + self.step_y > other.y + other.step_y and (self.x < ox and sx > other.x)

        real_hit = False
        if not self.hit_in:
            hit_x_purified = hit_x
            hit_y_purified = hit_x
            dx = None
            dy = None
            if hit_x and hit_y:
                dx = min(sx, ox) - max(other.x, self.x)
                dy = min(sy, oy) - max(other.y, self.y)

                if dx < dy:
                    hit_y_purified = False
                else:
                    hit_x_purified = False

            if hit_x or hit_y:
                print("bouncex", datetime.utcnow().strftime('%S.%f')[:-2], dx, self.step_x, hit_x_purified, hit_x)
                print("bouncey", datetime.utcnow().strftime('%S.%f')[:-2], dy, self.step_y, hit_y_purified, hit_y)

            if hit_x_purified:
                self.step_x *= -1.0
                self.hit_in = True
                real_hit = True
            if hit_y_purified:
                self.step_y *= -1.0
                self.hit_in = True
                real_hit = True
        else:
            self.hit_in = hit_x or hit_y
            if not self.hit_in:
                print ("Bounce change")

        return real_hit
    '''

    def test_hit(self, other):
        ox = other.x + other.width
        oy = other.y + other.height
        sx = self.x + BULLET_WIDTH
        sy = self.y + BULLET_HEIGHT
        if self.x < ox and sx > other.x and self.y < oy and sy > other.y:
            if self.hit_in:
                return False
            l = self.x - other.x
            r = (self.x + BULLET_WIDTH) - (other.x + other.width)
            t = self.y - other.y
            b = (self.y + BULLET_HEIGHT) - (other.y + other.height)
            sx = self.step_x + other.step_x
            sy = self.step_y + other.step_y
            '''
            if l < 0 and sx < 0:
                self.x += l
            elif r > 0 and sx > 0:
                self.x += r

            if t < 0 and sy < 0:
                self.y += t
            elif b > 0 and sy > 0:
                self.y += b
            '''
            inside = self.is_inside(other)

            self.hit_in = other
            if inside == 0:
                return False

            l = math.fabs(l)
            t = math.fabs(t)
            r = math.fabs(r)
            b = math.fabs(b)

            if (inside == self.LEFT) or (inside == self.RIGHT) or (
                    inside == (self.LEFT | self.TOP) and l > t and self.step_x > 0) or (
                    inside == (self.LEFT | self.BOTTOM) and l > b and self.step_x > 0) or (
                    inside == (self.RIGHT | self.TOP) and r > t and self.step_x < 0) or (
                    inside == (self.RIGHT | self.BOTTOM) and r > b and self.step_x < 0):
                self.step_x *= -1.0
            if inside == self.TOP or inside == self.BOTTOM or (
                    inside == (self.LEFT | self.TOP) and l < t and self.step_y > 0) or (
                    inside == (self.LEFT | self.BOTTOM) and l < b and self.step_y < 0) or (
                    inside == (self.RIGHT | self.TOP) and r < t and self.step_y > 0) or (
                    inside == (self.RIGHT | self.BOTTOM) and r < b and self.step_y < 0):
                self.step_y *= -1.0
            return True
        if self.hit_in == other:
            self.hit_in = None
        return False

    def draw(self, g, image):
        g.draw_image_rect(image, Telex.Rect(self.x, self.y, BULLET_WIDTH, BULLET_HEIGHT))


class Gun:
    def __init__(self, mx, my):
        self.mx = mx
        self.my = my
        self.x = self.mx - GUN_WIDTH / 2
        self.y = self.my - GUN_HEIGHT
        self.angle = self.my - GUN_HEIGHT
        self.width = GUN_WIDTH
        self.height = GUN_HEIGHT
        self.step_x = 0
        self.step_y = 0

    def draw(self, g, dome_image, barrel_image):
        g.draw_image_rect(dome_image, Telex.Rect(self.mx - GUN_WIDTH / 2, self.my - GUN_HEIGHT, GUN_WIDTH, GUN_HEIGHT))
        g.save()
        g.translate(self.mx, self.my - 20)
        g.rotate(self.angle)
        g.translate(-self.mx, -(self.my - 20))
        g.draw_image_rect(barrel_image, Telex.Rect(
            self.mx - BARREL_WIDTH / 2, self.my - (GUN_WIDTH * 0.9), BARREL_WIDTH, BARREL_HEIGHT))
        g.restore()

    def move(self, x, x_min, x_max):
        if (x < 0 and self.x > x_min) or (x > 0 and self.x + GUN_WIDTH < x_max):
            self.step_x = x
            self.mx += x
            self.x += x


class Ammo:
    def __init__(self, width, y_pos, count):
        self.width = width
        self.y_pos = y_pos
        self.count = count
        self.max = count
        self.gap = width / count - BULLET_WIDTH

    def draw(self, g, image):
        pos = (self.gap + BULLET_WIDTH) * (self.max - self.count)
        for i in range(0, self.count):
            g.draw_image_rect(image, Telex.Rect(pos, self.y_pos, BULLET_WIDTH, BULLET_HEIGHT))
            pos += self.gap + BULLET_WIDTH


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
        self.ammo = None
        self.tick = None
        self.hits = 0
        self.game_speed = MAX_GAME_SPEED
        self.game_speed_timer = None

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
        self.gun = Gun(self.width / 2, self.height - BULLET_HEIGHT - 4)
        self.ammo = Ammo(self.width, self.height - BULLET_HEIGHT - 2, MAX_AMMO)

    def create_monster(self, x_pos):
        self.monsters.append(Monster(
            x_pos, -MONSTER_HEIGHT, MONSTER_WIDTH, MONSTER_HEIGHT, random.randint(1, 99), self.numberDrawer))

    def start(self):
        self.monsters = []
        self.bullets = []
        self.ammo.count = MAX_AMMO
        self.hits = 0
        Telex.Element(self.ui, "game_over").set_attribute("style", "visibility:hidden")
        Telex.Element(self.ui, "hits").set_html(str(self.hits))
        Telex.Element(self.ui, "instructions").set_attribute("style", "visibility:hidden")
        self.tick = self.ui.start_timer(timedelta(milliseconds=TICK_SPEED), False, self.game_loop)
        #self.create_monster(random.randint(0, self.width - MONSTER_WIDTH))
        #self.create_monster(random.randint(0, self.width - MONSTER_WIDTH))
        self.game_speed = MAX_GAME_SPEED

    #   def dec():
    #       if self.game_speed > 5:
    #           self.game_speed -= 5

    #   self.game_speed_timer = self.ui.start_timer(
    #       timedelta(seconds=3), False, dec)

    def game_over(self):
        self.ui.stop_timer(self.tick);
        #   self.ui.stop_timer(self.game_speed_timer)
        self.game_speed_timer = None
        self.tick = None
        Telex.Element(self.ui, "game_over").set_attribute("style", "visibility:visible")
        Telex.Element(self.ui, "instructions").set_attribute("style", "visibility:visible")

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

                bullet.test_hit(self.gun)

                for monster in self.monsters:
                    if bullet.test_hit(monster):
                        monster.endurance -= 1
                        self.hits += 1
                        Telex.Element(self.ui, "hits").set_html(str(self.hits))
                        if monster.endurance <= 0:
                            bullet.hit_in = None
                            self.monsters.remove(monster)
                            if self.ammo.count < self.ammo.max:
                                self.ammo.count += 1

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
            if (monster.y + monster.height) > (self.height - BULLET_HEIGHT):
                self.game_over()
                return

        if random.randint(0, self.game_speed) == 1:
            x_pos = random.randint(0, self.width - MONSTER_WIDTH)
            is_ok = True
            for x in gaps:
                if (x_pos > x) or (x_pos < x + MONSTER_WIDTH):
                    is_ok = False
                    break
            if is_ok:
                self.create_monster(x_pos)
        self.gun.draw(fc, self.dome, self.barrel)
        self.ammo.draw(fc, self.bullet)
        self.canvas.draw_frame(fc)

    def shoot(self):
        if not self.tick:
            self.start()
            return

        if self.ammo.count > 0:
            start_x = (self.gun.mx - 10) + 110 * math.sin(self.gun.angle)
            start_y = (self.width - 30 - 10) - 110 * math.cos(self.gun.angle)
            self.bullets.append(Bullet(math.pi - self.gun.angle, start_x, start_y))
            self.ammo.count -= 1

    def turret(self, angle):
        if angle > -math.pi and angle - math.pi:
            self.gun.angle = angle

    def turret_turn(self, angle):
        self.turret(self.gun.angle + angle)

    def gun_move(self, x):
        self.gun.move(x, 0, self.width)


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

    Telex.Element(ui, "game_over").set_attribute("style", "visibility:hidden")

    canvas = Telex.CanvasElement(ui, 'canvas')

    images = canvas.add_images(urls, None)
    game = Game(ui, canvas, zip(files[1:], images))

    ui.on_open(lambda: game.init())

    canvas.subscribe("click", lambda _: game.shoot(), [], timedelta(milliseconds=200))

    def get_property(event):
        if event:
            nonlocal game
            x = float(event.properties["clientX"])
            y = float(event.properties["clientY"])
            mid_x = game.gun.x
            return math.atan2((game.rect.height - y), mid_x - x) - math.pi / 2
        return 0

    canvas.subscribe('mousemove', lambda e: game.turret(get_property(e)),
                     ["clientX", "clientY"], timedelta(milliseconds=100))

    def key_listen(e):
        code = int(float((e.properties['keyCode'])))
        if code == 37:  # left arrow
            game.gun_move(-GUN_SPEED)
        elif code == 39:  # right arrow
            game.gun_move(GUN_SPEED)
        elif code == ord('Z'):
            game.turret_turn(-TURRET_STEP)
        elif code == ord('X'):
            game.turret_turn(TURRET_STEP)
        elif code == ord('C'):
            game.shoot()

    # canvas is not focusable therefore we listen whole app
    ui.root().subscribe('keydown', key_listen, ['keyCode'])
    ui.run()


if __name__ == "__main__":
    # Telex.set_debug()
    main()
