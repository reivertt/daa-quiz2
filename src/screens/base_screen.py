import pygame

class BaseScreen:
    def __init__(self):
        self.manager = None 
        self.screen_width = pygame.display.get_surface().get_width() if pygame.display.get_init() else 800
        self.screen_height = pygame.display.get_surface().get_height() if pygame.display.get_init() else 600

    def on_enter(self, **kwargs):
        # print(f"Entering {self.__class__.__name__} with args: {kwargs}")
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        raise NotImplementedError("Subclasses must implement handle_event.")

    def update(self, dt):
        raise NotImplementedError("Subclasses must implement update.")

    def render(self, surface):
        raise NotImplementedError("Subclasses must implement render.")