import pygame
from screens.base_screen import BaseScreen
from ui_elements.button import Button 
from ui_elements.dialog import Dialog   

# ini tile size amang or not??
TILE_SIZE = 40
ROAD_COLOR = (150, 150, 150)
WALL_COLOR = (80, 80, 80)
START_COLOR = (100, 200, 100)
DEST_UNVISITED_COLOR = (255, 255, 100) # Yellow
DEST_VISITED_COLOR = (100, 255, 100)   # Green
PLAYER_COLOR = (255, 0, 0)
HINT_PATH_COLOR = (50, 200, 255, 150) # Semi-transparent blue

class GamePlayScreen(BaseScreen):
    def __init__(self, game_manager): # GameManager is essential
        super().__init__()
        self.game_manager = game_manager
        self.font_ui = pygame.font.Font(None, 32)
        self.current_level_id = None

        # --- UI Buttons ---
        def hint_action():
            self.game_manager.handle_player_action('request_hint')

        def pause_action(): # Or exit to menu
            self.game_manager.handle_player_action('pause_game') # This would trigger a dialog

        self.hint_button = Button(self.screen_width - 160, 10, 150, 40, "Hint (H)", callback=hint_action)
        self.menu_button = Button(self.screen_width - 160, 60, 150, 40, "Menu (Esc)", callback=pause_action)
        
        # --- Dialogs (initially inactive) ---
        self.dialogs = {
            'confirm_hint': Dialog(self.screen_width//2 - 175, self.screen_height//2 - 75, 350, 150,
                                   "Use Hint? (Consumes Battery)",
                                   button_configs=[{"text": "Yes", "value": "hint_yes"}, {"text": "No", "value": "hint_no"}]),
            'paused': Dialog(self.screen_width//2 - 150, self.screen_height//2 - 100, 300, 200,
                             "Paused",
                             button_configs=[{"text": "Resume", "value": "resume"},
                                             {"text": "Main Menu", "value": "exit_to_main_menu"}]),
            'level_complete': Dialog(self.screen_width//2 - 200, self.screen_height//2 - 100, 400, 200,
                                     "Level Complete!",
                                     button_configs=[{"text": "Next Level", "value": "next_level"},
                                                     {"text": "Retry", "value": "retry"},
                                                     {"text": "Main Menu", "value": "exit_to_main_menu"}]),
            'game_over': Dialog(self.screen_width//2 - 200, self.screen_height//2 - 100, 400, 200,
                                "Out of Fuel!",
                                button_configs=[{"text": "Retry", "value": "retry"},
                                                {"text": "Main Menu", "value": "exit_to_main_menu"}])
        }
        for dialog in self.dialogs.values():
            dialog.is_active = False
        
        self.active_dialog_key = None # To know which dialog is currently up

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        self.current_level_id = kwargs.get('level_id')
        if self.current_level_id is not None:
            self.game_manager.load_and_start_level(self.current_level_id) # Tell GM to load
        else:
            print("[GamePlayScreen] Error: No level_id provided on enter!")
            if self.manager: self.manager.go_to_screen('main_menu') # Go back if no level
        
        self.active_dialog_key = None # Reset active dialog
        for dialog in self.dialogs.values(): # Ensure all dialogs are inactive
            dialog.is_active = False
            dialog.result = None


    def handle_event(self, event):
        if self.active_dialog_key and self.dialogs[self.active_dialog_key].is_active:
            self.dialogs[self.active_dialog_key].handle_event(event)
            return # Dialog handles input exclusively

        # Game specific input (delegated to GameManager)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.game_manager.handle_player_action('move', 'up')
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.game_manager.handle_player_action('move', 'down')
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.game_manager.handle_player_action('move', 'left')
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.game_manager.handle_player_action('move', 'right')
            elif event.key == pygame.K_h: # Hint key
                self.game_manager.handle_player_action('request_hint')
            elif event.key == pygame.K_ESCAPE: # Pause key
                self.game_manager.handle_player_action('pause_game')
        
        # UI Button Events (if no dialog is active)
        self.hint_button.handle_event(event)
        self.menu_button.handle_event(event)


    def update(self, dt):
        current_game_state = self.game_manager.get_game_state()
        if current_game_state == 'playing' and not self.active_dialog_key:
            self.game_manager.update_game_logic(dt) 

        # Handle dialog results if one was just closed
        if self.active_dialog_key and not self.dialogs[self.active_dialog_key].is_active:
            dialog_result = self.dialogs[self.active_dialog_key].result
            if dialog_result:
                if self.active_dialog_key == 'confirm_hint':
                    self.game_manager.confirm_hint_use(dialog_result == 'hint_yes')
                else: # For pause, win, lose dialogs
                    self.game_manager.user_dialog_choice(dialog_result)
            
            self.dialogs[self.active_dialog_key].result = None # Consume result
            self.active_dialog_key = None # Dialog is now closed

        # Update active dialog based on game state from GameManager
        # This logic determines which dialog should pop up
        if current_game_state == 'confirm_hint' and self.active_dialog_key != 'confirm_hint':
            self.active_dialog_key = 'confirm_hint'
            self.dialogs['confirm_hint'].reset()
        elif current_game_state == 'paused' and self.active_dialog_key != 'paused':
            self.active_dialog_key = 'paused'
            self.dialogs['paused'].reset()
        elif current_game_state == 'level_complete' and self.active_dialog_key != 'level_complete':
            self.active_dialog_key = 'level_complete'
            self.dialogs['level_complete'].reset() # Maybe update message with score
        elif current_game_state == 'game_over' and self.active_dialog_key != 'game_over':
            self.active_dialog_key = 'game_over'
            self.dialogs['game_over'].reset()
        elif current_game_state == 'playing' and self.active_dialog_key and self.active_dialog_key != 'confirm_hint': # Clear pause/win/lose dialogs if game somehow resumes to playing
            self.dialogs[self.active_dialog_key].is_active = False
            self.active_dialog_key = None


    def _draw_map(self, surface, map_data, player_pos, destinations_data):
        # Basic map drawing - Person 1 (GameManager) provides map_data
        # map_data: 2D list of tile characters ('S', '.', '#', 'D')
        # destinations_data: list of dicts e.g. [{'pos':(x,y), 'visited':True/False}]
        # This assumes destinations_data is already aligned with 'D' tiles from map_data for status

        if not map_data: return

        # Create a mapping from destination position to its visited status for quick lookup
        dest_status_map = {tuple(d['pos']): d['visited'] for d in destinations_data}

        for r_idx, row in enumerate(map_data):
            for c_idx, tile_char in enumerate(row):
                rect = pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = ROAD_COLOR # Default
                if tile_char == '#': color = WALL_COLOR
                elif tile_char == 'S': color = START_COLOR
                elif tile_char == 'D':
                    is_visited = dest_status_map.get((c_idx, r_idx), False)
                    color = DEST_VISITED_COLOR if is_visited else DEST_UNVISITED_COLOR
                
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (50,50,50), rect, 1) # Grid lines

        # Draw Player
        player_rect = pygame.Rect(player_pos[0] * TILE_SIZE, player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, PLAYER_COLOR, player_rect)

    def _draw_hint_path(self, surface, hint_path):
        if not hint_path: return
        for (x, y) in hint_path:
            rect = pygame.Rect(x * TILE_SIZE + TILE_SIZE // 4, y * TILE_SIZE + TILE_SIZE // 4,
                               TILE_SIZE // 2, TILE_SIZE // 2)
            # Create a semi-transparent surface for the hint
            hint_surface = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)
            hint_surface.fill(HINT_PATH_COLOR)
            surface.blit(hint_surface, rect.topleft)


    def _draw_ui_overlay(self, surface):
        fuel = self.game_manager.get_fuel()
        battery = self.game_manager.get_battery()
        packages = self.game_manager.get_packages_remaining()

        fuel_text = self.font_ui.render(f"Fuel: {fuel}", True, (255, 255, 255))
        battery_text = self.font_ui.render(f"Battery: {battery}", True, (255, 255, 255))
        packages_text = self.font_ui.render(f"Packages: {packages}", True, (255, 255, 255))

        surface.blit(fuel_text, (10, 10))
        surface.blit(battery_text, (10, 40))
        surface.blit(packages_text, (10, 70))

        self.hint_button.draw(surface)
        self.menu_button.draw(surface)


    def render(self, surface):
        surface.fill((30, 30, 40))  # Dark background

        # Get data from GameManager for rendering
        map_data = self.game_manager.get_current_map_data()
        player_pos = self.game_manager.get_player_position()
        destinations_data = self.game_manager.get_destinations_data() # Assumes GM provides this structured data
        hint_path = self.game_manager.get_active_hint_path()

        self._draw_map(surface, map_data, player_pos, destinations_data)
        self._draw_hint_path(surface, hint_path)
        self._draw_ui_overlay(surface)

        # Render active dialog on top
        if self.active_dialog_key and self.dialogs[self.active_dialog_key].is_active:
            self.dialogs[self.active_dialog_key].draw(surface)