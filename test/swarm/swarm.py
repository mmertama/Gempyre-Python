import Gempyre
from Gempyre_utils import resource
import random
import math
from datetime import timedelta  # for time periods
import itertools

import sys


def normalize(r):
    while r < 0:
        r += 2 * math.pi
    while r >= 2 * math.pi:
        r -= 2 * math.pi
    return r


def _towards(r0, r, step):
    delta = r0 - r
    if delta < 0:
        if delta < math.pi:
            return r0 + step
        elif delta > math.pi:
            return r0 - step
        else:
            return r0 + step * random.randint(-1, 1)
    elif delta > 0:
        if delta > math.pi:
            return r0 + step
        elif delta < math.pi:
            return r0 - step
        else:
            return r0 + step * random.randint(-1, 1)


def towards(r0, r, step):
    return normalize(_towards(r0, r, step))


class Bee:
    def __init__(self, swarm):
        self.x = 0
        self.y = 0
        self.width = 10
        self.height = 10
        self.direction = random.random() * math.pi * 2
        self.heading = self.direction
        self.swarm = swarm
        self.speed = 1
        self.min_distance = self.width * self.height

    #def is_in(self, x, y):
    #    return self.x < x < self.x + self.width and self.y < y < self.y + self.height

    @staticmethod
    def average(closests):
        x = 0
        y = 0
        #dx = 0
        #dy = 0
        c_l = len(closests)
        c = 1 / c_l
        for b in closests:
            bee = b[0]
            x += bee.x * c
            y += bee.y * c
            #dx += math.sin(bee.direction)
            #dy += math.cos(bee.direction)

        #x /= c_l
        #y /= c_l
        #dx /= c_l
        #dy /= c_l
        #d = math.atan2(dx, dy)
        return x, y #, d

    def move(self):
        nearests = self.swarm.sample(self)
        #if not self.swarm.is_in(self.x, self.y, self.width):
        #    m_x, m_y = self.swarm.mid_point()
        #    xx = self.x - m_x
        #    yy = self.y - m_y
        #    self.direction = math.atan2(yy, xx) + math.pi
        #el
        #if nearests[0][1] <= self.min_distance:
        #    bee = nearests[0][0]
        #    xx = self.x - bee.x
        #    yy = self.y - bee.y
        #    self.direction = math.atan2(yy, xx)
        #else:
        x, y = self.average(nearests)
        xx = self.x - x
        yy = self.y - y
        self.direction = math.atan2(yy, xx) + math.pi
            #self.direction = d
        #self.heading = self.direction
        #self.direction = normalize(self.direction)

        self.heading = towards(self.heading, self.direction, 0.03)

        #self.heading = normalize(self.heading - delta / 10)
        next_x = math.cos(self.heading) * self.speed
        next_y = math.sin(self.heading) * self.speed
        self.x += next_x
        self.y += next_y

    def draw(self, drawer):
        d = self.heading
        drawer.save()
        drawer.translate(self.x, self.y)
        drawer.rotate(d)
        drawer.translate(-self.x, -self.y)
        drawer.begin_path()
        drawer.move_to(self.x - self.width / 2, self.y - self.height / 2)
        drawer.line_to(self.x + self.width / 2, self.y)
        drawer.line_to(self.x - self.width / 2, self.y + self.height / 2)
        drawer.line_to(self.x - self.width / 4, self.y)
        drawer.fill()
        drawer.restore()
        #drawer.fill_text(str(int(d * 180 / math.pi)), self.x, self.y)


class Swarm:
    def __init__(self, bee_count):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.bees = []
        self.fake_bee = Bee(self)
        for i in range(0, bee_count):
            self.bees.append(Bee(self))

    #def is_in(self, x, y, rad):
    #    return self.x - rad < x < self.x + self.width + rad and self.y + rad < y < self.y + self.height + rad

    def sample(self, bee):
        set_of = []
        sample = random.sample(self.bees, 5)
        for b in sample:
            if b != bee:
                dx = bee.x - b.x
                dy = bee.y - b.y
                dist = dx * dx + dy * dy
                set_of.append((b, dist))

        dx = bee.x - self.fake_bee.x
        dy = bee.y - self.fake_bee.y
        dist = dx * dx + dy * dy
        set_of.append((self.fake_bee, dist))

        set_of.sort(key=lambda r: r[1])
        return set_of

    def closest(self, bee):
        close_set = []
        for b in self.bees:
            if b != bee:
                dx = bee.x - b.x
                dy = bee.y - b.y
                dist = dx * dx + dy * dy
                if len(close_set) < 5:
                    close_set.append((b, dist))
                else:
                    for i, c in enumerate(close_set):
                        if c[1] < dist:
                            close_set[i] = (b, dist)
                            break
        close_set.sort(key=lambda r: r[1])
        return close_set

    def mid_point(self):
        return (self.x + self.width / 2,
                self.y + self.height / 2)

    def set_pos(self, x, y):
        self.fake_bee.x = x
        self.fake_bee.y = y

    def move(self):
        for b in self.bees:
            b.move()

    def draw(self, drawer):
        for b in self.bees:
            b.draw(drawer)
        drawer.fill_rect(Gempyre.Rect(self.fake_bee.x - 5, self.fake_bee.y - 5, 10, 10))


def main():
    print(Gempyre.version())
    Gempyre.set_debug(Gempyre.DebugLevel.Warning)
    file_map, names = resource.from_file("swarm.html")
    ui = Gempyre.Ui(file_map, '/swarm.html', Gempyre.os_browser())
    canvas = Gempyre.CanvasElement(ui, "canvas")
    swarm = Swarm(200)
    canvas_rect = Gempyre.Rect()
    dev_ratio = 1

    def resize_handler(_):
        nonlocal canvas_rect
        nonlocal dev_ratio
        canvas_rect = canvas.rect()
        dev_ratio = ui.device_pixel_ratio()
        swarm.x = 0#canvas_rect.x #* dev_ratio
        swarm.y = 0#canvas_rect.y #* dev_ratio
        swarm.width = canvas_rect.width #* dev_ratio
        swarm.height = canvas_rect.height #* dev_ratio

    ui.root().subscribe("resize", resize_handler)

    def draw():
        frame = Gempyre.FrameComposer()
        frame.clear_rect(Gempyre.Rect(swarm.x, swarm.y, swarm.width, swarm.height))
        swarm.draw(frame)
        frame.fill_rect(Gempyre.Rect(swarm.fake_bee.x - 5, swarm.fake_bee.y - 5, 10, 10))
        canvas.draw_frame(frame)

    def on_start():
        resize_handler(None)
        for b in swarm.bees:
            b.x = random.randint(b.width + swarm.x, swarm.width)
            b.y = random.randint(b.height + swarm.y, swarm.height)
        draw()

    ui.on_open(on_start)

    ui.start_timer(timedelta(milliseconds=80), False, lambda: swarm.move())
    ui.start_timer(timedelta(milliseconds=100), False, lambda: draw())

    def make_move(event):
        mouse_x = float(event.properties['clientX']) - canvas_rect.x
        mouse_y = float(event.properties['clientY']) - canvas_rect.y
        swarm.set_pos(mouse_x, mouse_y)

    canvas.subscribe('mousemove', make_move,
                     ["clientX", "clientY"], timedelta(milliseconds=100))

    ui.run()


if __name__ == "__main__":
    main()
    #d = 0
    #n = 2
    #for i in range(0, 1000):
    #    print(d, n)
    #    n = towards(n, d, 0.01)
