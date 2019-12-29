import pygame
from vecmath import Vec2


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


class Victim(Drawable):

    def __init__(self, position):
        super().__init__(position)

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


class Timer:

    def __init__(self, period):
        self._period = period
        self._time = 0

    def set_period(self, period):
        self._period = period

    def update(self, dt):
        self._time += dt
        if self._time >= self._period:
            self._time = 0
            return True
        return False


class Simulation:

    def __init__(self, canvas):
        self._canvas = canvas

    def loop(self, dt):
        pass

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

    def loop(self):

        while self._running:
            dt = self._clock.tick(Application.FRAME_RATE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

            self._simulation.loop(dt)

    def clear(self):
        self._simulation.clear()
        pygame.quit()


app = Application()
app.loop()
app.clear()
