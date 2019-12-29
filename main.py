import pygame


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
