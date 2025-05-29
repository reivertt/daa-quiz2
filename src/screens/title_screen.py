import pygame
from screens.base_screen import BaseScreen
from ui_elements.button import Button

class TitleScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title_font = pygame.font.Font(None, 74)
        self.title_text = "apt-deliver packages" 

        # Button Callbacks
        def start_game_action():
            if self.manager:
                self.manager.go_to_screen('main_menu') 

        def settings_action():
            if self.manager:
                self.manager.go_to_screen('settings')

        def tutorial_action():
            if self.manager:
                self.manager.go_to_screen('tutorial')
        
        def exit_action():
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        try:
            self.title_image = pygame.image.load("assets/images/backgrounds/title.png").convert_alpha()
            self.title_image = pygame.transform.scale(self.title_image, (self.screen_width, self.screen_height))
            self.image_rect = self.title_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        except pygame.error as e:
            print(f"Error loading title image: {e}")
            self.title_image = pygame.Surface((self.screen_width - 100, self.screen_height - 200))
            self.title_image.fill((100, 100, 100))
            error_font = pygame.font.Font(None, 36)
            error_text = error_font.render("Title Image Not Found!", True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(self.title_image.get_width()//2, self.title_image.get_height()//2))
            self.title_image.blit(error_text, error_rect)
            self.image_rect = self.title_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))


        button_width = 250
        button_height = 50
        spacing = 20
        start_y = self.screen_height // 2 - ( (button_height + spacing) * 4 ) // 2

        self.buttons = [
            Button(self.screen_width // 2 - button_width // 2, start_y,
                   button_width, button_height, "Start Game", callback=start_game_action),
            Button(self.screen_width // 2 - button_width // 2, start_y + (button_height + spacing),
                   button_width, button_height, "Tutorial", callback=tutorial_action),
            Button(self.screen_width // 2 - button_width // 2, start_y + 2 * (button_height + spacing),
                   button_width, button_height, "Settings", callback=settings_action),
            Button(self.screen_width // 2 - button_width // 2, start_y + 3 * (button_height + spacing),
                   button_width, button_height, "Exit", callback=exit_action,
                   normal_color=(200, 50, 50), hover_color=(230, 80, 80))
        ]

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((50, 50, 80)) 

        surface.blit(self.title_image, self.image_rect)

        # Render buttons
        for button in self.buttons:
            button.draw(surface)