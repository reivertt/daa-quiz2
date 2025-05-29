from player import Player
from level_loader import LevelData, LevelLoader
from ..config import Configurations
from progress_manager import ProgressManager

config = Configurations()

class GameManager:
    def __init__(self, level_loader: LevelLoader, progress_manager: ProgressManager, hint_provider_instance=None):
        self.level_loader = level_loader
        self.progress_manager = progress_manager
        self.player: Player | None = None
        self.current_level_data: LevelData | None = None
        self.current_level_id: int | None = None

        self.current_fuel: int = 0
        self.current_battery: int = 0
        self.packages_left_to_deliver: int = 0
        self.destination_tiles_coords: list[tuple[int, int]] = []
        self.delivered_packages_coords: set[tuple[int, int]] = set()

        # Game status & UI interaction
        self.current_game_state: str = config.GAME_STATE_PLAYING
        self.is_level_loaded: bool = False

        self.active_hint_path: list[tuple[int, int]] | None = None
        self.hint_provider = hint_provider_instance

    def load_and_start_level(self, level_id: int):
        print(f"GM: Attempting to load level ID: {level_id}")
        self.current_level_id = level_id
        level_data = self.level_loader.load_level_by_number(level_id)
        if level_data:
            self._initialize_level_state(level_data)
            self.current_game_state = config.GAME_STATE_PLAYING
        else:
            print(f"GM: Failed to load level ID: {level_id}")
            self.is_level_loaded = False
            self.current_game_state = config.GAME_STATE_GAME_OVER
    
    def _initialize_level_state(self, level_data: LevelData):
        self.current_level_data = level_data
        
        start_row, start_col = self.current_level_data.player_start_pos
        if self.player is None:
            self.player = Player(x=start_col, y=start_row)
        else:
            self.player.set_location(x=start_col, y=start_row)

        self.current_fuel = self.current_level_data.initial_fuel
        self.current_battery = self.current_level_data.hint_battery
        self.packages_left_to_deliver = self.current_level_data.num_packages_to_deliver
        
        self.destination_tiles_coords = list(self.current_level_data.destination_coords)
        self.delivered_packages_coords = set()
        self.active_hint_path = None

        self.is_level_loaded = True

        print(f"GM: Level '{level_data.name}' loaded. Fuel: {self.current_fuel}, Battery: {self.current_battery}, Packages: {self.packages_left_to_deliver}")
        self._check_initial_package_delivery()
        self._update_game_rules_and_status()
    
    def _check_initial_package_delivery(self):
        if not self.player or not self.current_level_data: return
        player_r, player_c = self.player.y, self.player.x
        current_pos_tuple = (player_r, player_c)

        if current_pos_tuple in self.destination_tiles_coords and \
           current_pos_tuple not in self.delivered_packages_coords:
            self._process_package_delivery_at(current_pos_tuple)
    
    def _calculate_fuel_cost(self, tile_char: str) -> int:
        if tile_char.isdigit():
            cost = int(tile_char)
            return cost if cost > 0 else config.DEFAULT_FUEL_CONSUMPTION_PER_MOVE
        return config.DEFAULT_FUEL_CONSUMPTION_PER_MOVE
    
    def _handle_player_move_action(self, direction_key: str) -> bool:
        if not self.is_level_loaded or self.current_game_state != config.GAME_STATE_PLAYING:
            return False
        
        if self.current_fuel <= 0 and self.packages_left_to_deliver > 0:
            self.current_game_state = config.GAME_STATE_GAME_OVER
            print("GM: Game Over - Ran out of fuel before attempting move.")
            self._update_game_rules_and_status()
            return False

        self.player.update_state(self.current_level_data.grid)
        moved = self.player.move(direction_key)
        
        if moved:
            player_r, player_c = self.player.y, self.player.x
            tile_player_is_on = self.current_level_data.grid[player_r][player_c]
            
            fuel_cost = self._calculate_fuel_cost(tile_player_is_on)
            self.current_fuel -= fuel_cost
            
            current_pos_tuple = (player_r, player_c)

            if tile_player_is_on == config.DESTINATION_TILE:
                if current_pos_tuple in self.destination_tiles_coords and \
                   current_pos_tuple not in self.delivered_packages_coords:
                    self._process_package_delivery_at(current_pos_tuple)
            
            self._update_game_rules_and_status()
            return True
        else:
            self._update_game_rules_and_status()
            return False

    def _process_package_delivery_at(self, coords: tuple[int, int]):
        self.packages_left_to_deliver -= 1
        self.delivered_packages_coords.add(coords)
        print(f"GM: Package delivered at {coords}! Packages left: {self.packages_left_to_deliver}")

    def _update_game_rules_and_status(self):
        if self.current_game_state not in [config.GAME_STATE_PLAYING, config.GAME_STATE_CONFIRM_HINT]:
            return

        if self.packages_left_to_deliver == 0:
            self.current_game_state = config.GAME_STATE_LEVEL_COMPLETE
            print("GM: Game Over - You Win! All packages delivered.")
            if self.current_level_id is not None:
                level_just_completed = self.current_level_id
                potential_new_max_unlocked = level_just_completed + 1
                current_max_saved = self.progress_manager.load_progress()
                
                if potential_new_max_unlocked > current_max_saved:
                    total_designed_levels = self.level_loader.get_available_levels_count()
                    if potential_new_max_unlocked <= total_designed_levels +1:
                        self.progress_manager.save_progress(potential_new_max_unlocked)
                        print(f"GM: ProgressManager updated. Max level unlocked is now potentially {potential_new_max_unlocked}")
                    else:
                        print(f"GM: All levels completed or next level {potential_new_max_unlocked} exceeds total levels {total_designed_levels}.")
                else:
                    print(f"GM: Level {level_just_completed} completed, but {potential_new_max_unlocked} does not exceed current max unlocked {current_max_saved}.")
            return

        if self.current_fuel < 0:
            self.current_game_state = config.GAME_STATE_GAME_OVER
            print("GM: Game Over - Ran out of fuel.")
            return
    
    def handle_player_action(self, action_type: str, **kwargs):
        if not self.is_level_loaded and action_type not in ['pause_game', 'dialog_choice']:
             print(f"GM: Level not loaded, cannot handle action: {action_type}")
             return

        if self.current_game_state == config.GAME_STATE_LEVEL_COMPLETE or \
           self.current_game_state == config.GAME_STATE_GAME_OVER:
            # If game is won or lost, only dialog choices should be processed
            if action_type == 'dialog_choice':
                choice = kwargs.get('choice')
                self.user_dialog_choice(choice)
            return

        if action_type == 'move':
            if self.current_game_state == config.GAME_STATE_PLAYING:
                direction_name = kwargs.get('direction') # 'up', 'down', 'left', 'right'
                if direction_name in config.DIRECTION_MAP:
                    self._handle_player_move_action(config.DIRECTION_MAP[direction_name])
        
        elif action_type == 'request_hint':
            if self.current_game_state == config.GAME_STATE_PLAYING and self.can_use_hint():
                self.current_game_state = config.GAME_STATE_CONFIRM_HINT
            else:
                print("GM: Cannot use hint (no battery, game not playing, or already confirming).")

        elif action_type == 'pause_game':
            if self.current_game_state == config.GAME_STATE_PLAYING:
                self.current_game_state = config.GAME_STATE_PAUSED
            elif self.current_game_state == config.GAME_STATE_PAUSED:
                 self.current_game_state = config.GAME_STATE_PLAYING


        elif action_type == 'dialog_choice':
            choice = kwargs.get('choice')
            print(f"GM: Received generic dialog choice: {choice} - to be handled by specific methods.")
    
    def confirm_hint_use(self, confirmed: bool):
        if self.current_game_state != config.GAME_STATE_CONFIRM_HINT:
            return

        if confirmed and self.can_use_hint():
            self.current_battery -= config.HINT_BATTERY_COST_PER_USE
            self.active_hint_path = None
            if self.hint_provider and self.player and self.current_level_data:
                player_pos_cr = (self.player.x, self.player.y)
                 
                pending_dest_cr = []
                for r,c in self.current_level_data.destination_coords:
                    if (r,c) not in self.delivered_packages_coords:
                        pending_dest_cr.append((c,r)) 

                self.active_hint_path = self.hint_provider.get_hint_path(
                    grid=self.current_level_data.grid,
                    start_node=player_pos_cr,
                    undelivered_destinations=pending_dest_cr 
                )
            else:
                print("GM: HintProvider not available or player/level data missing.")
            print(f"GM: Hint used. Battery left: {self.current_battery}. Path: {self.active_hint_path}")
        else:
            self.active_hint_path = None

        self.current_game_state = config.GAME_STATE_PLAYING
    
    def user_dialog_choice(self, choice: str):
        print(f"GM: User dialog choice: {choice}, current state: {self.current_game_state}")
        
        if choice == 'resume':
            if self.current_game_state == config.GAME_STATE_PAUSED:
                self.current_game_state = config.GAME_STATE_PLAYING
        
        elif choice == 'retry':
            if self.current_level_id is not None:
                self.load_and_start_level(self.current_level_id)
            else:
                 print("GM: Cannot retry, no current_level_id known.")
        
        elif choice == 'next_level':
            if self.current_game_state == config.GAME_STATE_LEVEL_COMPLETE:
                if self.current_level_id is not None:
                    next_level_to_play = self.current_level_id + 1
                    max_unlocked = self.progress_manager.load_progress()
                    num_available_levels = self.level_loader.get_available_levels_count()

                    if next_level_to_play < max_unlocked and next_level_to_play <= num_available_levels :
                        self.load_and_start_level(next_level_to_play)
                    elif next_level_to_play == max_unlocked and next_level_to_play <= num_available_levels:
                        self.load_and_start_level(next_level_to_play)
                    else:
                        print(f"GM: Cannot go to next level. Next: {next_level_to_play}, Max Unlocked: {max_unlocked}, Total Levels: {num_available_levels}")
                        self.is_level_loaded = False
                else:
                    print("GM: Cannot go to next level, current_level_id is unknown.")
        
        elif choice == 'exit_to_main_menu':
            self.is_level_loaded = False
            self.current_game_state = config.GAME_STATE_PLAYING
            print("GM: Requesting exit to main menu (handled by ScreenManager).")

    def get_game_state(self) -> str:
        return self.current_game_state

    def get_fuel(self) -> int:
        return self.current_fuel

    def get_battery(self) -> int:
        return self.current_battery

    def get_packages_remaining(self) -> int:
        return self.packages_left_to_deliver

    def get_total_packages_for_level(self) -> int:
        return self.current_level_data.num_packages_to_deliver if self.current_level_data else 0
    
    def get_current_map_data(self) -> list[str] | None:
        return self.current_level_data.grid if self.current_level_data else None

    def get_player_position(self) -> tuple[int, int] | None:
        return self.player.get_location() if self.player else None

    def get_destinations_data(self) -> list[dict]:
        dest_data_for_ui = []
        if not self.current_level_data:
            return dest_data_for_ui
        
        for r_coord, c_coord in self.current_level_data.destination_coords:
            pos_xy = (c_coord, r_coord)
            is_visited = (r_coord, c_coord) in self.delivered_packages_coords
            dest_data_for_ui.append({'pos': pos_xy, 'visited': is_visited})
        return dest_data_for_ui

    def get_active_hint_path(self) -> list[tuple[int, int]] | None:
        return self.active_hint_path
    
    def can_use_hint(self) -> bool:
        return self.current_battery >= config.HINT_BATTERY_COST_PER_USE and \
               self.is_level_loaded and \
               self.current_game_state == config.GAME_STATE_PLAYING
    
    def get_player_possible_moves(self) -> dict[str, bool]:
        if not self.player or not self.current_level_data or self.game_over:
            return {"up": False, "down": False, "left": False, "right": False}
        
        self.player.update_state(self.current_level_data.grid)
        return {
            "up": self.player.move_up,
            "down": self.player.move_down,
            "left": self.player.move_left,
            "right": self.player.move_right,
        }

if __name__ == "__main__":
    import os
    if not os.path.exists("config.py"):
        print("Creating dummy config.py for GameManager test")
        with open("config.py", "w") as f:
            f.write("START_TILE = 'S'\n")
            f.write("ROAD_TILE = '0'\n")
            f.write("WALL_TILE = '1'\n")
            f.write("DESTINATION_TILE = 'D'\n")
            f.write("FUEL_CONSUMPTION_PER_MOVE = 1\n")
            f.write("GAME_STATE_WON = 'won'\n")
            f.write("GAME_STATE_LOST_FUEL = 'lost_fuel'\n")
            f.write("GAME_STATE_LOST_STUCK = 'lost_stuck'\n")
    import config # Now import it

    print("--- GameManager Internal Test ---")

    # 1. Create a simple LevelData object
    # Old way might have passed map_grid directly to load_level
    test_map = ["S0D"]
    level_data_simple = LevelData(
        grid=test_map,
        fuel=3,
        destinations=[(2,0)], # D is at col 2, row 0
        start_pos=(0,0)       # S is at col 0, row 0
    )

    gm = GameManager()
    gm.load_level(level_data_simple)

    def print_gm_status():
        print(f"Player: {gm.player_pos}, Fuel: {gm.current_fuel}, Pkgs Left: {gm.packages_left_to_deliver}, Over: {gm.is_game_over()}, Result: {gm.get_game_result()}")

    print_gm_status()

    # OLD TEST LOOP MIGHT HAVE BEEN:
    # moves = ['d', 'd']
    # for move in moves:
    #     print(f"Attempting move: {move}")
    #     # OLD: gm.do_move(move) or gm.player_move(move)
    #     # NEW:
    #     success = gm.handle_player_move(move)
    #     print(f"Move success: {success}")
    #     print_gm_status()
    #     if gm.is_game_over():
    #         break

    # Example of a potential refactor break:
    # If `load_level` previously didn't auto-decrement packages for starting on 'D',
    # but now it does (via `_initial_setup_packages`), the expected `packages_left_to_deliver`
    # at the start of the test loop would be different.

    print("\nTest 1: Move to D and win")
    # "S0D", fuel 3. Start (0,0). D at (2,0)
    # Expect: S -> (0,0) fuel 3, pkgs 1
    # 'd' -> (1,0) fuel 2, pkgs 1
    # 'd' -> (2,0) [D] fuel 1, pkgs 0 -> WIN
    
    if gm.handle_player_move('d'): print_gm_status() # Move to (1,0)
    if gm.handle_player_move('d'): print_gm_status() # Move to (2,0) - D
    
    assert gm.is_game_over() and gm.get_game_result() == config.GAME_STATE_WON
    assert gm.get_current_fuel() == 1 # 3 - 1 - 1 = 1
    assert gm.get_packages_left() == 0
    print("Test 1 Passed!")

    print("\nTest 2: Run out of fuel")
    level_data_fuel = LevelData(grid=["S00D"], fuel=1, destinations=[(3,0)], start_pos=(0,0))
    gm.load_level(level_data_fuel)
    print_gm_status()
    # S(0,0) fuel 1, pkgs 1
    # 'd' -> (1,0) fuel 0, pkgs 1. Game not over.
    gm.handle_player_move('d')
    print_gm_status()
    assert gm.get_current_fuel() == 0
    assert not gm.is_game_over()

    # 'd' -> attempt to move to (2,0). Should fail due to no fuel.
    # The game over for fuel might be set here.
    moved = gm.handle_player_move('d')
    print_gm_status()
    assert not moved # Expect move to fail
    # The exact point GAME_STATE_LOST_FUEL is set depends on your _check_game_over
    # and handle_player_move logic. If handle_player_move sets it when fuel < consumption:
    assert gm.is_game_over()
    assert gm.get_game_result() == config.GAME_STATE_LOST_FUEL # This might fail if logic changed
    print("Test 2 Passed (or needs check on GAME_STATE_LOST_FUEL point)!")

    print("--- GameManager Internal Test Complete ---")