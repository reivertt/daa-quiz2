# src/screens/main_menu_screen.py
import pygame
from .base_screen import BaseScreen
from ui_elements.button import Button # Ensure this import path is correct for your project

class MainMenuScreen(BaseScreen):
    def __init__(self, game_manager): 
        super().__init__()
        self.game_manager = game_manager
        self.title_font = pygame.font.Font(None, 60)
        self.level_buttons = []
        
        # Get total levels dynamically from GameManager
        self.total_levels = self.game_manager.get_total_defined_levels()
        if self.total_levels == 0: # Fallback if GM method not ready or no levels
            print("[MainMenuScreen] WARNING: GameManager reported 0 total levels. Defaulting to 6 for UI.")
            self.total_levels = 6 

        self.levels_per_row = 3
        self.button_width = 150
        self.button_height = 100
        self.button_padding = 20

        # Initial creation. Buttons will be properly updated in on_enter
        self._create_level_buttons() 

        def back_to_title_action():
            if self.manager: # self.manager is the ScreenManager instance
                self.manager.go_to_screen('title')
        
        self.back_button = Button(
            x=50, y=self.screen_height - 70,
            width=150, height=40, text="Back to Title",
            callback=back_to_title_action
        )

    def _create_level_buttons(self):
        self.level_buttons = []
        
        # Get progress data from GameManager
        max_playable_level = self.game_manager.get_max_level_unlocked()

        grid_width = self.levels_per_row * (self.button_width + self.button_padding) - self.button_padding
        start_x = (self.screen_width - grid_width) // 2
        start_y = 150 # Position below the "Select Level" title

        for i in range(self.total_levels):
            level_num = i + 1 # Levels are usually 1-indexed for display
            row = i // self.levels_per_row
            col = i % self.levels_per_row

            x = start_x + col * (self.button_width + self.button_padding)
            y = start_y + row * (self.button_height + self.button_padding)

            is_unlocked = level_num <= max_playable_level
            is_completed = True if level_num < max_playable_level else False 

            button_text = f"Level {level_num}"
            button_color = (100, 100, 180) # Default button color (e.g., blue-ish for unlocked)

            if not is_unlocked:
                button_text += " - X"
                button_color = (120, 120, 120) # Grey for locked
            elif is_completed:
                button_text += " - V" 
                button_color = (100, 180, 100) # Green for completed
            

            # Define a callback for each button
            def make_level_select_callback(lvl_id_to_play):
                def callback():
                    if self.manager: # self.manager is the ScreenManager
                        print(f"[MainMenuScreen] Level {lvl_id_to_play} selected to play.")
                        # GamePlayScreen.on_enter will tell GameManager to load this level
                        self.manager.go_to_screen('game_play', level_id=lvl_id_to_play)
                return callback

            button = Button(x, y, self.button_width, self.button_height,
                            text=button_text,
                            callback=make_level_select_callback(level_num) if is_unlocked else None,
                            is_enabled=is_unlocked,
                            normal_color=button_color,
                            hover_color=(button_color[0]+30, button_color[1]+30, button_color[2]+30), # Brighter hover
                            font_size=24 if "\n" in button_text else 30 
                           )
            self.level_buttons.append(button)

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        # Re-create/update buttons to reflect current progress when screen is entered
        # This ensures that if progress changes (e.g., after completing a level and returning),
        # the level select screen is up-to-date.
        self.total_levels = self.game_manager.get_total_defined_levels() # Refresh total levels
        self._create_level_buttons()
        print("[MainMenuScreen] Entered. Level buttons updated based on current progress.")

    def handle_event(self, event):
        for button in self.level_buttons:
            button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self, dt):
        # Usually static, but could have hover effects or minor animations
        pass

    def render(self, surface):
        surface.fill((70, 90, 110))  # A pleasant background color

        title_surface = self.title_font.render("Select Level", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surface, title_rect)

        for button in self.level_buttons:
            button.draw(surface)
        self.back_button.draw(surface)