import pygame

pygame.font.init() 

class Button:
    def __init__(self, x, y, width, height, text='',
                 font_name=None, font_size=30,
                 text_color=(255, 255, 255),
                 normal_color=(100, 100, 100),
                 hover_color=(150, 150, 150),
                 pressed_color=(50, 50, 50),
                 disabled_color=(70, 70, 70),
                 callback=None,
                 image_normal=None, image_hover=None, image_pressed=None,
                 is_enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(font_name, font_size)
        self.text_color = text_color
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.disabled_color = disabled_color
        self.callback = callback
        self.is_enabled = is_enabled

        # Image handling
        self.image_normal = image_normal
        self.image_hover = image_hover if image_hover else image_normal
        self.image_pressed = image_pressed if image_pressed else image_normal
        # Ensure images are scaled to button size if provided
        if self.image_normal:
            self.image_normal = pygame.transform.scale(self.image_normal, (width, height))
        if self.image_hover:
            self.image_hover = pygame.transform.scale(self.image_hover, (width, height))
        if self.image_pressed:
            self.image_pressed = pygame.transform.scale(self.image_pressed, (width, height))

        self.current_image = self.image_normal
        self.current_color = self.normal_color

        self.is_hovered = False
        self.is_pressed = False

        self._update_appearance()

    def _update_appearance(self):
        if not self.is_enabled:
            self.current_color = self.disabled_color
            self.current_image = self.image_normal 
        elif self.is_pressed:
            self.current_color = self.pressed_color
            self.current_image = self.image_pressed
        elif self.is_hovered:
            self.current_color = self.hover_color
            self.current_image = self.image_hover
        else:
            self.current_color = self.normal_color
            self.current_image = self.image_normal

    def handle_event(self, event):
        if not self.is_enabled:
            return False 

        action_triggered = False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.is_hovered:
                if self.callback:
                    self.callback()
                action_triggered = True
            self.is_pressed = False 

        self._update_appearance()
        return action_triggered


    def draw(self, surface):
        if self.current_image:
            surface.blit(self.current_image, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.current_color, self.rect)
            pygame.draw.rect(surface, (0,0,0), self.rect, 2) 

        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def set_enabled(self, enabled_status):
        self.is_enabled = enabled_status
        if not self.is_enabled:
            self.is_hovered = False
            self.is_pressed = False
        self._update_appearance()