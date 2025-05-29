import pygame
from ui_elements.button import Button 

pygame.font.init()

class Dialog:
    def __init__(self, x, y, width, height, message,
                 font_name=None, font_size=28, text_color=(0, 0, 0),
                 bg_color=(200, 200, 200), border_color=(50, 50, 50),
                 button_configs=None, 
                 button_height=40, button_padding=10,
                 button_font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.message = message
        self.font = pygame.font.Font(font_name, font_size)
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color

        self.buttons = []
        self.result = None 
        self.is_active = True 

        if button_configs is None:
            button_configs = [{"text": "OK", "value": "ok"}]

        self._create_buttons(button_configs, button_height, button_padding, button_font_size, font_name)

    def _create_buttons(self, button_configs, button_height, button_padding, button_font_size, font_name):
        num_buttons = len(button_configs)
        if num_buttons == 0:
            return

        total_button_width = self.rect.width - (num_buttons + 1) * button_padding
        button_width = total_button_width / num_buttons

        current_x = self.rect.left + button_padding
        button_y = self.rect.bottom - button_height - button_padding

        for config in button_configs:
            def make_callback(value):
                def callback():
                    self.result = value
                    self.is_active = False
                return callback

            btn = Button(x=current_x, y=button_y,
                         width=button_width, height=button_height,
                         text=config.get("text", "Button"),
                         font_name=font_name, font_size=button_font_size,
                         callback=make_callback(config.get("value", config.get("text"))))
            self.buttons.append(btn)
            current_x += button_width + button_padding

    def handle_event(self, event):
        if not self.is_active:
            return

        for button in self.buttons:
            button.handle_event(event)
            if not self.is_active: 
                break

    def draw(self, surface):
        if not self.is_active:
            return

        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 3) 

        text_surface = self.font.render(self.message, True, self.text_color)
        message_rect_center_y = self.rect.top + (self.rect.height - (self.buttons[0].rect.height if self.buttons else 0) - 20) / 2
        text_rect = text_surface.get_rect(center=(self.rect.centerx, message_rect_center_y))
        surface.blit(text_surface, text_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

    def reset(self):
        self.is_active = True
        self.result = None