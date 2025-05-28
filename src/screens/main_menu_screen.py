import pygame
from .base_screen import BaseScreen
from ..ui_elements.button import Button 

class MainMenuScreen(BaseScreen):
    def __init__(self, game_manager): 
        super().__init__()
        self.game_manager = game_manager
        self.title_font = pygame.font.Font(None, 60)
        self.level_buttons = []
        self.total_levels = 6
        self.levels_per_row = 3
        self.button_width = 150
        self.button_height = 100
        self.button_padding = 20

        self._create_level_buttons() 

        def back_to_title_action():
            if self.manager:
                self.manager.go_to_screen('title')
        
        self.back_button = Button(
            x=50, y=self.screen_height - 70,
            width=150, height=40, text="Back to Title",
            callback=back_to_title_action
        )

    def _create_level_buttons(self):
        self.level_buttons = []
        unlocked_levels = self.game_manager.get_unlocked_levels() 

        grid_width = self.levels_per_row * (self.button_width + self.button_padding) - self.button_padding
        start_x = (self.screen_width - grid_width) // 2
        start_y = 150 

        for i in range(self.total_levels):
            level_num = i + 1
            row = i // self.levels_per_row
            col = i % self.levels_per_row

            x = start_x + col * (self.button_width + self.button_padding)
            y = start_y + row * (self.button_height + self.button_padding)

            is_unlocked = level_num <= unlocked_levels
            is_completed = self.game_manager.get_level_completion_status(level_num) 

            button_text = f"Level {level_num}"
            if not is_unlocked:
                button_text += "\n(Locked)"
            elif is_completed:
                button_text += "\n(Done!)" 

            # Define a callback for each button
            def make_level_select_callback(lvl_id):
                def callback():
                    if self.manager:
                        # GameManager loads the level internally, then ScreenManager switches
                        self.game_manager.select_level(lvl_id) 
                        self.manager.go_to_screen('game_play', level_id=lvl_id) # Pass level_id
                return callback

            button = Button(x, y, self.button_width, self.button_height,
                            text=button_text,
                            callback=make_level_select_callback(level_num) if is_unlocked else None,
                            is_enabled=is_unlocked,
                            normal_color=(100, 180, 100) if is_completed else (100, 100, 180),
                            font_size=24 if "\n" in button_text else 30 # Smaller font for multi-line
                           )
            self.level_buttons.append(button)

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        # Re-create buttons to reflect current progress when screen is entered
        self._create_level_buttons()
        print("[MainMenuScreen] Entered. Level buttons updated.")

    def handle_event(self, event):
        for button in self.level_buttons:
            button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self, dt):
        # Potentially animations for buttons or background
        pass

    def render(self, surface):
        surface.fill((70, 90, 110))  # Background color

        title_surface = self.title_font.render("Select Level", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surface, title_rect)

        for button in self.level_buttons:
            button.draw(surface)
        self.back_button.draw(surface)