import pygame
from vecmath import Vec2
from math import pi, sin, cos

import random


APPLICATION_DISPLAY_SIZE = (640, 480)
APPLICATION_FRAME_RATE = 60

SIMULATION_METER = 8
SIMULATION_SECOND = 1000
SIMULATION_TIME_FACTOR = 25

VICTIM_FIND_FOOD_STATE = 0
VICTIM_FIND_PARTNER_STATE = 1
VICTIM_NORMAL_STATE = 2
VICTIM_DEAD_BODY_STATE = 3
VICTIM_ROTTEN_BODY_STATE = 4
VICTIM_SCARY_STATE = 5

VICTIM_HUNGER_WANT_EAT_THRESHOLD = 1000
VICTIM_HUNGER_WANT_PARTNER_THRESHOLD = 500
VICTIM_HUNGER_DIE_THRESHOLD = 5000
VICTIM_HUNGER_GROWTH_SPEED = 1 / SIMULATION_SECOND
VICTIM_EAT_SPEED = 5 / SIMULATION_SECOND  # hunger units

VICTIM_INIT_HP = 3

VICTIM_BABY_PERIOD = 500 * SIMULATION_SECOND  # sim second
VICTIM_GETS_ROTTEN_PERIOD = 1000 * SIMULATION_SECOND

VICTIM_NORMAL_SPEED = 0.5 * SIMULATION_METER / SIMULATION_SECOND  # per second

VICTIM_VIEW_RADIUS = 10 * SIMULATION_METER
VICTIM_SCARY_RADIUS = 0.5 * VICTIM_VIEW_RADIUS


PREDATOR_FIND_FOOD_STATE = 0
PREDATOR_FIND_PARTNER_STATE = 1
PREDATOR_NORMAL_STATE = 2
PREDATOR_DEAD_STATE = 3

PREDATOR_HUNGER_WANT_EAT_THRESHOLD = 1000
PREDATOR_HUNGER_WANT_PARTNER_THRESHOLD = 500
PREDATOR_HUNGER_DIE_THRESHOLD = 5000
PREDATOR_HUNGER_GROWTH_SPEED = 5 / SIMULATION_SECOND
PREDATOR_EAT_SPEED = 100 / SIMULATION_SECOND  # hunger units
PREDATOR_DAMAGE_SPEED = 0.3 / SIMULATION_SECOND

PREDATOR_BABY_PERIOD = 1000 * SIMULATION_SECOND  # sim second

PREDATOR_NORMAL_SPEED = 0.5 * SIMULATION_METER / SIMULATION_SECOND  # per second

PREDATOR_VIEW_RADIUS = 10 * SIMULATION_METER

VICTIMS_INIT_NUMBER = 200
VICTIM_FOODS_INIT_NUMBER = 100
PREDATORS_INIT_NUMBER = 100


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

    def __init__(self, position, init_hunger=0.0):
        super().__init__(position)
        self._state = PREDATOR_NORMAL_STATE
        self._hunger = init_hunger
        self._go_point = None
        self._go_angle = 0.0
        self._baby_timer = Timer(PREDATOR_BABY_PERIOD)
        self._eating = False

    def get_state(self):
        return self._state

    def has_go_point(self):
        return self._go_point is not None

    def set_go_point(self, point=None):
        if point is None:
            if self._go_point:
                angle = random.gauss(self._go_angle, pi / 4) % (2 * pi)
            else:
                angle = random.uniform(0, 2 * pi)
            self._go_point = Vec2(cos(angle) * VICTIM_VIEW_RADIUS,
                                  sin(angle) * VICTIM_VIEW_RADIUS) + self._position
            self._go_angle = angle
        else:
            self._go_point = point
        new_go_point = Vec2(min(max(self._go_point.get_x(), 0), APPLICATION_DISPLAY_SIZE[0]),
                            min(max(self._go_point.get_y(), 0), APPLICATION_DISPLAY_SIZE[1]))
        if new_go_point != self._go_point:
            self._go_angle = random.uniform(0, 2 * pi)
        self._go_point = new_go_point

    def get_speed(self):
        return PREDATOR_NORMAL_SPEED / max((1, (self._hunger - PREDATOR_HUNGER_WANT_EAT_THRESHOLD) / 1000))

    def get_move_vector(self, sim_dt):
        dist_vec = (self._go_point - self._position)
        if dist_vec.length() <= PREDATOR_NORMAL_SPEED * sim_dt:
            return None
        return dist_vec.normalize() * self.get_speed()

    def get_vec_to_go_point(self):
        if self._go_point:
            return self._go_point - self.get_position()
        return None

    def can_make_baby(self):
        return self._baby_timer.is_elapsed() and not self._eating and self._state == PREDATOR_FIND_PARTNER_STATE

    def baby_made(self):
        self._baby_timer.restart()

    def make_baby(self, other):
        if self.can_make_baby() and other.can_make_baby():
            self.baby_made()
            other.baby_made()
            return Predator((self._position + other.get_position()) / 2)
        return None

    def eat(self, dt, victim):
        self._eating = True
        self._hunger -= PREDATOR_EAT_SPEED * dt
        victim.hurt(PREDATOR_DAMAGE_SPEED * dt)
        if self._hunger <= 0:
            self._hunger = 0
            self._eating = False

    def update(self, dt):
        self._baby_timer.update(dt)
        self._hunger += PREDATOR_HUNGER_GROWTH_SPEED * dt
        # print(self._hunger)
        if self._hunger >= PREDATOR_HUNGER_DIE_THRESHOLD:
            self._state = PREDATOR_DEAD_STATE
        elif self._hunger >= PREDATOR_HUNGER_WANT_EAT_THRESHOLD:
            self._state = PREDATOR_FIND_FOOD_STATE
        elif self._hunger < PREDATOR_HUNGER_WANT_PARTNER_THRESHOLD and self._baby_timer.is_elapsed() and not self._eating:
            self._state = PREDATOR_FIND_PARTNER_STATE
        elif not self._eating:
            self._state = PREDATOR_NORMAL_STATE

    def draw(self, surf):
        pygame.draw.ellipse(surf,
                            (255, 0, 0),
                            (*(self._position - Vec2(SIMULATION_METER / 4, SIMULATION_METER / 4)),
                             SIMULATION_METER / 2, SIMULATION_METER / 2))


class VictimFood(Drawable):

    def __init__(self, position):
        super().__init__(position)

    def draw(self, surf):
        pygame.draw.ellipse(surf,
                            (0, 255, 0),
                            (*(self._position - Vec2(SIMULATION_METER / 4, SIMULATION_METER / 4)),
                             SIMULATION_METER / 2, SIMULATION_METER / 2))


class Victim(Drawable):

    def __init__(self, position, init_hunger=0.0):
        super().__init__(position)
        self._state = VICTIM_NORMAL_STATE
        self._hunger = init_hunger
        self._go_point = None
        self._go_angle = 0.0
        self._baby_timer = Timer(VICTIM_BABY_PERIOD)
        self._rotten_timer = None
        self._eating = False
        self._hp = VICTIM_INIT_HP
        self._rotten_hp = VICTIM_INIT_HP * 2

    def get_state(self):
        return self._state

    def has_go_point(self):
        return self._go_point is not None

    def set_go_point(self, point=None):
        if point is None:
            if self._go_point:
                angle = random.gauss(self._go_angle, pi / 4) % (2 * pi)
            else:
                angle = random.uniform(0, 2 * pi)
            self._go_point = Vec2(cos(angle) * VICTIM_VIEW_RADIUS,
                                  sin(angle) * VICTIM_VIEW_RADIUS) + self._position
            self._go_angle = angle
        else:
            self._go_point = point
        new_go_point = Vec2(min(max(self._go_point.get_x(), 0), APPLICATION_DISPLAY_SIZE[0]),
                            min(max(self._go_point.get_y(), 0), APPLICATION_DISPLAY_SIZE[1]))
        if new_go_point != self._go_point:
            self._go_angle = random.uniform(0, 2 * pi)
        self._go_point = new_go_point

    def get_move_vector(self, sim_dt):
        dist_vec = (self._go_point - self._position)
        if dist_vec.length() <= VICTIM_NORMAL_SPEED * sim_dt:
            return None
        return dist_vec.normalize() * VICTIM_NORMAL_SPEED

    def get_vec_to_go_point(self):
        if self._go_point:
            return self._go_point - self.get_position()
        return None

    def can_make_baby(self):
        return self._baby_timer.is_elapsed() and not self._eating and self._state == VICTIM_FIND_PARTNER_STATE

    def baby_made(self):
        self._baby_timer.restart()

    def make_baby(self, other):
        if self.can_make_baby() and other.can_make_baby():
            self.baby_made()
            other.baby_made()
            return Victim((self._position + other.get_position()) / 2)
        return None

    def hurt(self, damage):
        if self._state != VICTIM_DEAD_BODY_STATE:
            self._hp -= damage
        else:
            self._rotten_hp -= damage

    def eat(self, dt):
        self._eating = True
        self._hunger -= VICTIM_EAT_SPEED * dt
        if self._hunger <= 0:
            self._hunger = 0
            self._eating = False

    def update(self, dt, is_predator_close):
        self._baby_timer.update(dt)
        self._hunger += VICTIM_HUNGER_GROWTH_SPEED * dt
        if self._rotten_timer and self._rotten_timer.is_elapsed() or self._rotten_hp <= 0:
            self._state = VICTIM_ROTTEN_BODY_STATE
        elif self._hunger >= VICTIM_HUNGER_DIE_THRESHOLD or self._hp <= 0:
            self._state = VICTIM_DEAD_BODY_STATE
            self._rotten_timer = Timer(VICTIM_GETS_ROTTEN_PERIOD)
        elif is_predator_close:
            self._state = VICTIM_SCARY_STATE
        elif self._hunger >= VICTIM_HUNGER_WANT_EAT_THRESHOLD:
            self._state = VICTIM_FIND_FOOD_STATE
        elif self._hunger < VICTIM_HUNGER_WANT_PARTNER_THRESHOLD and self._baby_timer.is_elapsed() and not self._eating:
            self._state = VICTIM_FIND_PARTNER_STATE
        elif not self._eating:
            self._state = VICTIM_NORMAL_STATE

    def draw(self, surf):
        pygame.draw.ellipse(surf,
                            (0, 0, 255),
                            (*(self._position - Vec2(SIMULATION_METER / 4, SIMULATION_METER / 4)),
                             SIMULATION_METER / 2, SIMULATION_METER / 2))


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

    def __init__(self, canvas):
        self._canvas = canvas
        self._victims = list()
        self._victim_foods = list()
        self._predators = list()
        self._time_line = TimeLine(SIMULATION_TIME_FACTOR)
        self._victims_died = 0
        self._predators_died = 0

    def add_victim(self, victim):
        if type(victim) != Victim:
            raise TypeError('Argument should be Victim')
        self._victims.append(victim)

    def add_victim_food(self, food):
        if type(food) != VictimFood:
            raise TypeError('Argument should be VictimFood')
        self._victim_foods.append(food)

    def add_predator(self, predator):
        if type(predator) != Predator:
            raise TypeError('Argument should be Predator')
        self._predators.append(predator)

    def setup(self):
        for i in range(VICTIMS_INIT_NUMBER):
            init_hunger = random.uniform(0, 400)
            self.add_victim(Victim(Vec2(random.randint(0, APPLICATION_DISPLAY_SIZE[0]),
                                        random.randint(0, APPLICATION_DISPLAY_SIZE[1])), init_hunger))

        for i in range(PREDATORS_INIT_NUMBER):
            init_hunger = random.uniform(0, 400)
            self.add_predator(Predator(Vec2(random.randint(0, APPLICATION_DISPLAY_SIZE[0]),
                                            random.randint(0, APPLICATION_DISPLAY_SIZE[1])), init_hunger))

        for i in range(VICTIM_FOODS_INIT_NUMBER):
            self.add_victim_food(VictimFood(Vec2(random.randint(0, APPLICATION_DISPLAY_SIZE[0]),
                                                 random.randint(0, APPLICATION_DISPLAY_SIZE[1]))))

    def _process_victims(self, sim_dt):
        for victim in self._victims[:]:
            closest_predators = list()
            for p in self._predators:
                if (p.get_position() - victim.get_position()).length() <= VICTIM_SCARY_RADIUS:
                    closest_predators.append(p)
            victim.update(sim_dt, len(closest_predators) != 0)
            if victim.get_state() == VICTIM_ROTTEN_BODY_STATE:
                self._victims.remove(victim)
                self._victims_died += 1
                continue
            elif victim.get_state() == VICTIM_SCARY_STATE:
                go_point = Vec2()
                for p in closest_predators:
                    go_point = go_point + (victim.get_position() - p.get_position()).normalize()
                if go_point.length() == 0:
                    victim.set_go_point()
                else:
                    go_point = go_point.normalize() * VICTIM_VIEW_RADIUS + victim.get_position()
                    victim.set_go_point(go_point)
            elif victim.get_state() == VICTIM_NORMAL_STATE:
                if not victim.has_go_point() or victim.get_move_vector(sim_dt) is None:
                    victim.set_go_point()
            elif victim.get_state() == VICTIM_FIND_PARTNER_STATE:
                partners = list()
                for v in self._victims:
                    if v == victim:
                        continue
                    if (v.get_position() - victim.get_position()).length() <= VICTIM_VIEW_RADIUS and v.can_make_baby():
                        partners.append(v)
                partner = None
                if partners:
                    partner = min(partners, key=lambda x: (victim.get_position() - x.get_position()).length())
                if partner is not None:
                    victim.set_go_point(partner.get_position())
                    vmv = victim.get_vec_to_go_point()
                    if vmv is None or vmv.length() <= 0.5 * SIMULATION_METER:
                        baby = victim.make_baby(partner)
                        if baby:
                            self.add_victim(baby)
                elif not victim.has_go_point() or victim.get_move_vector(sim_dt) is None:
                    victim.set_go_point()
            elif victim.get_state() == VICTIM_FIND_FOOD_STATE:
                foods = list()
                for f in self._victim_foods:
                    if (f.get_position() - victim.get_position()).length() <= VICTIM_VIEW_RADIUS:
                        foods.append(f)
                food = None
                if foods:
                    food = min(foods, key=lambda x: (victim.get_position() - x.get_position()).length())
                if food is not None:
                    victim.set_go_point(food.get_position())
                    vmv = victim.get_vec_to_go_point()
                    if vmv is None or vmv.length() <= 0.5 * SIMULATION_METER:
                        victim.eat(sim_dt)
                elif not victim.has_go_point() or victim.get_move_vector(sim_dt) is None:
                    victim.set_go_point()
            elif victim.get_state() == VICTIM_DEAD_BODY_STATE:
                pass

            if victim.get_move_vector(sim_dt) is not None:
                victim.move(victim.get_move_vector(sim_dt) * sim_dt)
            victim.draw(self._canvas)

    def _process_predators(self, sim_dt):
        for predator in self._predators[:]:
            predator.update(sim_dt)
            if predator.get_state() == PREDATOR_DEAD_STATE:
                self._predators.remove(predator)
                self._predators_died += 1
                continue
            elif predator.get_state() == PREDATOR_NORMAL_STATE:
                if not predator.has_go_point() or predator.get_move_vector(sim_dt) is None:
                    predator.set_go_point()
            elif predator.get_state() == PREDATOR_FIND_PARTNER_STATE:
                partners = list()
                for p in self._predators:
                    if p == predator:
                        continue
                    if (p.get_position() - predator.get_position()).length() <= PREDATOR_VIEW_RADIUS and p.can_make_baby():
                        partners.append(p)
                partner = None
                if partners:
                    partner = min(partners, key=lambda x: (predator.get_position() - x.get_position()).length())
                if partner is not None:
                    predator.set_go_point(partner.get_position())
                    pmv = predator.get_vec_to_go_point()
                    if pmv is None or pmv.length() <= 0.5 * SIMULATION_METER:
                        baby = predator.make_baby(partner)
                        if baby:
                            self.add_predator(baby)
                elif not predator.has_go_point() or predator.get_move_vector(sim_dt) is None:
                    predator.set_go_point()
            elif predator.get_state() == PREDATOR_FIND_FOOD_STATE:
                foods = list()
                for v in self._victims:
                    if (v.get_position() - predator.get_position()).length() <= PREDATOR_VIEW_RADIUS:
                        foods.append(v)
                food = None
                if foods:
                    food = min(foods, key=lambda x: (predator.get_position() - x.get_position()).length() * (x.get_state() != VICTIM_DEAD_BODY_STATE))
                if food is not None:
                    predator.set_go_point(food.get_position())
                    pmv = predator.get_vec_to_go_point()
                    if pmv is None or pmv.length() <= 0.5 * SIMULATION_METER:
                        predator.eat(sim_dt, food)
                elif not predator.has_go_point() or predator.get_move_vector(sim_dt) is None:
                    predator.set_go_point()

            if predator.get_move_vector(sim_dt) is not None:
                predator.move(predator.get_move_vector(sim_dt) * sim_dt)
            predator.draw(self._canvas)

    def _print_stats(self):
        print(f'Victims: {len(self._victims)}')
        print(f'Victims died: {self._victims_died}')
        print(f'Victims in state VICTIM_FIND_FOOD_STATE: {len(list(filter(lambda x: x.get_state() == VICTIM_FIND_FOOD_STATE, self._victims)))}')
        print(f'Victims in state VICTIM_FIND_PARTNER_STATE: {len(list(filter(lambda x: x.get_state() == VICTIM_FIND_PARTNER_STATE, self._victims)))}')
        print(f'Victims in state VICTIM_NORMAL_STATE: {len(list(filter(lambda x: x.get_state() == VICTIM_NORMAL_STATE, self._victims)))}')
        print(f'Victims in state VICTIM_DEAD_BODY_STATE: {len(list(filter(lambda x: x.get_state() == VICTIM_DEAD_BODY_STATE, self._victims)))}')
        print(f'Victims in state VICTIM_DEAD_BODY_STATE: {len(list(filter(lambda x: x.get_state() == VICTIM_DEAD_BODY_STATE, self._victims)))}')
        print(f'Victims in state VICTIM_ROTTEN_BODY_STATE: {len(list(filter(lambda x: x.get_state() == VICTIM_ROTTEN_BODY_STATE, self._victims)))}')
        print(f'Victims in state VICTIM_SCARY_STATE: {len(list(filter(lambda x: x.get_state() == VICTIM_SCARY_STATE, self._victims)))}')
        print('--------------------------------------------------------------------------------------')
        print(f'Predators: {len(self._predators)}')
        print(f'Predators died: {self._predators_died}')
        print(f'Predators in state PREDATOR_FIND_FOOD_STATE: {len(list(filter(lambda x: x.get_state() == PREDATOR_FIND_FOOD_STATE, self._predators)))}')
        print(f'Predators in state PREDATOR_FIND_PARTNER_STATE: {len(list(filter(lambda x: x.get_state() == PREDATOR_FIND_PARTNER_STATE, self._predators)))}')
        print(f'Predators in state PREDATOR_NORMAL_STATE: {len(list(filter(lambda x: x.get_state() == PREDATOR_NORMAL_STATE, self._predators)))}')
        print(f'Predators in state PREDATOR_DEAD_STATE: {len(list(filter(lambda x: x.get_state() == PREDATOR_DEAD_STATE, self._predators)))}')

    def process_input_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._print_stats()

    def _draw_gui(self, surf):
        font = pygame.font.Font(None, 18)
        time_text = font.render(f'Время: {self._time_line.get_time() / SIMULATION_SECOND}', 1, (255, 255, 255))
        surf.blit(time_text, (0, 0))

    def loop(self, dt):

        self._time_line.update(dt)
        sim_dt = self._time_line.get_delta_time()

        self._process_victims(sim_dt)
        self._process_predators(sim_dt)

        for food in self._victim_foods:
            food.draw(self._canvas)

        self._draw_gui(self._canvas)

    def clear(self):
        pass


class Application:

    def __init__(self):

        pygame.init()
        self._screen = pygame.display.set_mode(APPLICATION_DISPLAY_SIZE)
        self._clock = pygame.time.Clock()

        self._running = True
        self._simulation = Simulation(self._screen)

        self._simulation.setup()

    def loop(self):

        while self._running:
            dt = self._clock.tick(APPLICATION_FRAME_RATE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                self._simulation.process_input_event(event)

            self._screen.fill((0, 0, 0))
            self._simulation.loop(dt)

            pygame.display.flip()

    def clear(self):
        self._simulation.clear()
        pygame.quit()


app = Application()
app.loop()
app.clear()
