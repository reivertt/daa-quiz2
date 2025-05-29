import pygame
from screens.base_screen import BaseScreen
from ui_elements.button import Button 

class TutorialScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.background_color = (60, 80, 60) 

        try:
            self.tutorial_image = pygame.image.load("assets/images/tutorial.png").convert_alpha()
            # img_width = self.tutorial_image.get_width()
            # img_height = self.tutorial_image.get_height()
            # scale_ratio = self.screen_width / img_width
            # new_height = int(img_height * scale_ratio)
            # self.tutorial_image = pygame.transform.scale(self.tutorial_image, (self.screen_width, new_height))
            # scale to screen height:
            # scale_ratio = self.screen_height / img_height
            # new_width = int(img_width * scale_ratio)
            # self.tutorial_image = pygame.transform.scale(self.tutorial_image, (new_width, self.screen_height))

            # todo: make the actual tutorial image and resize it
            self.image_rect = self.tutorial_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        except pygame.error as e:
            print(f"Error loading tutorial image: {e}")
            self.tutorial_image = pygame.Surface((self.screen_width - 100, self.screen_height - 200))
            self.tutorial_image.fill((100, 100, 100))
            error_font = pygame.font.Font(None, 36)
            error_text = error_font.render("Tutorial Image Not Found!", True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(self.tutorial_image.get_width()//2, self.tutorial_image.get_height()//2))
            self.tutorial_image.blit(error_text, error_rect)
            self.image_rect = self.tutorial_image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))


        # --- Back Button ---
        def back_action():
            if self.manager:
                self.manager.go_to_screen('title')

        self.back_button = Button(
            x=self.screen_width // 2 - 100,
            y=self.screen_height - 120, 
            width=200,
            height=50,
            text="Back",
            callback=back_action
        )

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill(self.background_color)

        surface.blit(self.tutorial_image, self.image_rect)

        self.back_button.draw(surface)