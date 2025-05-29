import pygame
from screens.base_screen import BaseScreen
from ui_elements.button import Button 
from ui_elements.dialog import Dialog   

class SettingsScreen(BaseScreen):
    def __init__(self, game_manager_ref=None): 
        super().__init__()
        self.game_manager = game_manager_ref 
        self.font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 28)
        self.reset_feedback_message = ""

        # --- Callbacks ---
        def reset_progress_action():
            self.confirmation_dialog.message = "Really reset all progress? This cannot be undone."
            self.confirmation_dialog.reset() 
            print("[SettingsScreen] Reset progress button clicked, showing dialog.")

        def back_action():
            if self.manager:
                self.manager.go_to_screen('title_screen') 

        # --- Buttons ---
        button_width = 300
        button_height = 50
        self.reset_button = Button(self.screen_width // 2 - button_width // 2, self.screen_height // 2 - 60,
                                   button_width, button_height, "Reset All Progress",
                                   callback=reset_progress_action,
                                   normal_color=(220, 100, 100), hover_color=(250, 130, 130))
        
        self.back_button = Button(self.screen_width // 2 - 100, self.screen_height - 100,
                                  200, 50, "Back", callback=back_action)
        
        self.buttons = [self.reset_button, self.back_button]

        # --- Confirmation Dialog (initially inactive) ---
        dialog_button_configs = [
            {"text": "Yes, Reset", "value": "confirm_reset"},
            {"text": "No, Cancel", "value": "cancel_reset"}
        ]
        self.confirmation_dialog = Dialog(
            x=self.screen_width // 2 - 200, y=self.screen_height // 2 - 100,
            width=400, height=200,
            message="Really reset all progress?", 
            button_configs=dialog_button_configs
        )
        self.confirmation_dialog.is_active = False 

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        self.reset_feedback_message = "" 

    def handle_event(self, event):
        if self.confirmation_dialog.is_active:
            self.confirmation_dialog.handle_event(event)
        else:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        if not self.confirmation_dialog.is_active and self.confirmation_dialog.result is not None:
            if self.confirmation_dialog.result == "confirm_reset":
                print("[SettingsScreen] Confirmed reset progress!")
                self.reset_feedback_message = "Progress reset (simulated)." 
                
            elif self.confirmation_dialog.result == "cancel_reset":
                print("[SettingsScreen] Cancelled reset progress.")
                self.reset_feedback_message = "Reset cancelled."
            
            self.confirmation_dialog.result = None 

    def render(self, surface):
        surface.fill((70, 70, 100))  

        # Screen Title
        title_surf = self.font.render("Settings", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 100))
        surface.blit(title_surf, title_rect)

        # Render buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Render feedback message
        if self.reset_feedback_message:
            feedback_surf = self.info_font.render(self.reset_feedback_message, True, (200, 255, 200))
            feedback_rect = feedback_surf.get_rect(center=(self.screen_width // 2, self.reset_button.rect.bottom + 40))
            surface.blit(feedback_surf, feedback_rect)

        # Render dialog if active
        if self.confirmation_dialog.is_active:
            self.confirmation_dialog.draw(surface)