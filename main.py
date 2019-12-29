import pygame
from vecmath import Vec2
from math import pi, sin, cos

import random


class Drawable:

    def __init__(self, position):
        self._position = position

    def set_position(self, pos):
        self._position = pos

    def get_position(self):
        return self._position

    def move(self, dp):
        self._position = self._position + dp

    def draw(self, surf):  # should be overridden
        pass


class Predator(Drawable):

    def __init__(self, position):
        super().__init__(position)

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


class VictimFood(Drawable):

    def __init__(self, position):
        super().__init__(position)

    def draw(self, surf):
        pygame.draw.ellipse(surf,
                            (0, 255, 0),
                            (*(self._position - Vec2(5, 5)), 10, 10))


class Victim(Drawable):

    FIND_FOOD_STATE = 0
    FIND_PARTNER_STATE = 1
    NORMAL_STATE = 2
    DEAD_STATE = 3

    HUNGER_WANT_EAT_THRESHOLD = 1000
    HUNGER_WANT_PARTNER_THRESHOLD = 500
    HUNGER_DIE_THRESHOLD = 5000
    HUNGER_GROWTH_SPEED = 1  # units per sim second

    BABY_PERIOD = 10000  # sim second

    NORMAL_SPEED = 0.5  # sim meters per second

    VIEW_RADIUS = 2  # sim meters

    def __init__(self, position):
        super().__init__(position)
        self._state = Victim.NORMAL_STATE
        self._hunger = 0.0
        self._go_point = None
        self._baby_timer = Timer(Victim.BABY_PERIOD * 1000)

    def get_state(self):
        return self._state

    def has_go_point(self):
        return self._go_point is not None

    def set_go_point(self, point=None):
        if point is None:
            angle = random.uniform(0, 2 * pi)
            self._go_point = Vec2(cos(angle) * Victim.VIEW_RADIUS * Simulation.METER,
                                  sin(angle) * Victim.VIEW_RADIUS * Simulation.METER) + self._position
        else:
            self._go_point = point

    def get_move_vector(self):
        dist_vec = (self._go_point - self._position)
        if dist_vec.length() <= 1e-7:
            return None
        return (self._go_point - self._position).normalize() * Victim.NORMAL_SPEED

    def make_baby(self, other):
        self._baby_timer.restart()
        return Victim((self._position + other.get_position()) / 2)

    def update(self, dt):
        self._baby_timer.update(dt)
        self._hunger += Victim.HUNGER_GROWTH_SPEED / 1000 * dt
        if self._hunger >= Victim.HUNGER_DIE_THRESHOLD:
            self._state = Victim.DEAD_STATE
        elif self._hunger >= Victim.HUNGER_WANT_EAT_THRESHOLD:
            self._state = Victim.FIND_FOOD_STATE
        elif self._hunger < Victim.HUNGER_WANT_PARTNER_THRESHOLD and self._baby_timer.is_elapsed():
            self._state = Victim.FIND_PARTNER_STATE
        else:
            self._state = Victim.NORMAL_STATE

    def draw(self, surf):
        pygame.draw.ellipse(surf,
                            (0, 0, 255),
                            (*(self._position - Vec2(5, 5)), 10, 10))


class TimeLine:

    def __init__(self, time_factor):
        self._time = 0
        self._time_factor = time_factor
        self._last_dt_ct = 0

    def get_time(self):
        return self._time

    def get_delta_time(self):
        result = self._time - self._last_dt_ct
        self._last_dt_ct = self._time
        return result

    def update(self, dt):
        self._time += dt * self._time_factor


class Timer:

    def __init__(self, period, periodic=False):
        self._period = period
        self._time = 0
        self._periodic = periodic
        self._elapsed = False

    def set_period(self, period):
        self._period = period

    def restart(self):
        self._time = 0
        self._elapsed = False

    def is_elapsed(self):
        return self._elapsed

    def update(self, dt):
        self._time += dt
        if self._time >= self._period:
            if self._periodic:
                self._time = 0
            else:
                self._elapsed = True
            return True
        return False


class Simulation:

    METER = 32
    TIME_FACTOR = 10

    def __init__(self, canvas):
        self._canvas = canvas
        self._victims = list()
        self._victim_foods = list()
        self._predators = list()
        self._time_line = TimeLine(Simulation.TIME_FACTOR)

    def add_victim(self, victim):
        if type(victim) != Victim:
            raise TypeError('Argument should be Victim')
        self._victims.append(victim)

    def add_victim_food(self, food):
        if type(food) != VictimFood:
            raise TypeError('Argument should be VictimFood')
        self._victim_foods.append(food)

    def setup(self):
        for i in range(100):
            self.add_victim(Victim(Vec2(random.randint(0, Application.DISPLAY_SIZE[0]),
                                        random.randint(0, Application.DISPLAY_SIZE[1]))))
        for i in range(33):
            self.add_victim_food(VictimFood(Vec2(random.randint(0, Application.DISPLAY_SIZE[0]),
                                                 random.randint(0, Application.DISPLAY_SIZE[1]))))

    def _process_victims(self, sim_dt):
        for victim in self._victims[:]:
            victim.update(sim_dt)
            if victim.get_state() == Victim.DEAD_STATE:
                self._victims.remove(victim)
                continue
            elif victim.get_state() == Victim.NORMAL_STATE:
                if not victim.has_go_point() or victim.get_move_vector() is None:
                    victim.set_go_point()
            elif victim.get_state() == Victim.FIND_PARTNER_STATE:
                partners = list()
                for v in self._victims:
                    if v == victim:
                        continue
                    if (v.get_position() - victim.get_position()).length() <= Victim.VIEW_RADIUS * Simulation.METER:
                        partners.append(v)
                partner = None
                if partners:
                    partner = min(partners, key=lambda x: (victim.get_position() - x.get_position()).length())
                if partner is not None:
                    victim.set_go_point(partner.get_position())
                    vmv = victim.get_move_vector()
                    if vmv is None or vmv.length() <= 0.5 * Simulation.METER:
                        self.add_victim(victim.make_baby(partner))
                elif not victim.has_go_point() or victim.get_move_vector() is None:
                    victim.set_go_point()

            victim.move(victim.get_move_vector())
            victim.draw(self._canvas)

    def loop(self, dt):

        self._time_line.update(dt)
        sim_dt = self._time_line.get_delta_time()

        self._process_victims(sim_dt)
        print(len(self._victims))

        for food in self._victim_foods:
            food.draw(self._canvas)

    def clear(self):
        pass


class Application:

    DISPLAY_SIZE = (640, 480)
    FRAME_RATE = 60

    def __init__(self):

        pygame.init()
        self._screen = pygame.display.set_mode(Application.DISPLAY_SIZE)
        self._clock = pygame.time.Clock()

        self._running = True
        self._simulation = Simulation(self._screen)

        self._simulation.setup()

    def loop(self):

        while self._running:
            dt = self._clock.tick(Application.FRAME_RATE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

            self._screen.fill((0, 0, 0))
            self._simulation.loop(dt)

            pygame.display.flip()

    def clear(self):
        self._simulation.clear()
        pygame.quit()


app = Application()
app.loop()
app.clear()
