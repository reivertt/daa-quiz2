import pygame

class ScreenManager:
    def __init__(self):
        self.screens = {}  
        self.current_screen_name = None
        self.current_screen = None

    def add_screen(self, screen_name, screen_instance):
        self.screens[screen_name] = screen_instance
        screen_instance.manager = self 

    def go_to_screen(self, screen_name, **kwargs):
        if self.current_screen:
            self.current_screen.on_exit()

        if screen_name in self.screens:
            self.current_screen_name = screen_name
            self.current_screen = self.screens[screen_name]
            self.current_screen.on_enter(**kwargs) 
            print(f"[ScreenManager] Transitioned to {screen_name}")
        else:
            print(f"[ScreenManager] Error: Screen '{screen_name}' not found.")

    def handle_event(self, event):
        """Passes events to the current active screen."""
        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, dt):
        """Updates the logic of the current active screen."""
        if self.current_screen:
            self.current_screen.update(dt)

    def render(self, surface):
        """Renders the current active screen."""
        if self.current_screen:
            self.current_screen.render(surface)
        else:
            surface.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text_surf = font.render("No active screen", True, (255, 0, 0))
            text_rect = text_surf.get_rect(center=(surface.get_width()//2, surface.get_height()//2))
            surface.blit(text_surf, text_rect)