from player import Player
from level_loader import LevelData, LevelLoader
import config as config

class GameManager:
    def __init__(self):
        self.player: Player | None = None
        self.current_level_data: LevelData | None = None
        
        self.current_fuel: int = 0
        self.current_battery: int = 0
        self.packages_left_to_deliver: int = 0
        self.destination_tiles_coords: list[tuple[int, int]] = []
        self.delivered_packages_coords: set[tuple[int, int]] = set()

        self.is_level_loaded: bool = False
        self.game_over: bool = False
        self.game_result: str | None = None

    def load_level(self, level_data: LevelData):
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

        self.is_level_loaded = True
        self.game_over = False
        self.game_result = None

        print(f"GameManager: Level '{level_data.name}' loaded. Fuel: {self.current_fuel}, Battery: {self.current_battery}, Packages: {self.packages_left_to_deliver}")
        self._check_initial_package_delivery()
        self._update_game_status()
    
    def _check_initial_package_delivery(self):
        if not self.player or not self.current_level_data:
            return
        player_r, player_c = self.player.y, self.player.x
        current_pos_tuple = (player_r, player_c)

        if self.current_level_data.grid[player_r][player_c] == config.DESTINATION_TILE:
            if current_pos_tuple in self.destination_tiles_coords and \
               current_pos_tuple not in self.delivered_packages_coords:
                self._process_package_delivery_at(current_pos_tuple)
    
    def handle_player_move(self, direction_key: str) -> bool:
        if not self.is_level_loaded or self.game_over:
            # print("GM: Cannot move, level not loaded or game over.")
            return False
        
        if self.current_fuel <= 0 and self.packages_left_to_deliver > 0 :
            self.game_over = True
            self.game_result = config.GAME_STATE_LOST_FUEL
            # print("GM: Game Over - Ran out of fuel before moving.")
            return False

        self.player.update_state(self.current_level_data.grid)
        moved = self.player.move(direction_key)
        
        if moved:
            player_r, player_c = self.player.y, self.player.x
            current_pos_tuple = (player_r, player_c)
            tile_char = self.current_level_data.grid[player_r][player_c]
            
            self.current_fuel -= config.FUEL_CONSUMPTION_PER_MOVE

            if tile_char == config.DESTINATION_TILE:
                if current_pos_tuple in self.destination_tiles_coords and \
                   current_pos_tuple not in self.delivered_packages_coords:
                    self._process_package_delivery_at(current_pos_tuple)
            
            self._update_game_status()
            return True
        else:
            self._update_game_status()
            return False

    def _process_package_delivery_at(self, coords: tuple[int, int]):
        self.packages_left_to_deliver -= 1
        self.delivered_packages_coords.add(coords)
        print(f"GM: Package delivered at {coords}! Packages left: {self.packages_left_to_deliver}")

    def _update_game_status(self):
        if self.game_over:
            return

        if self.packages_left_to_deliver == 0:
            self.game_over = True
            self.game_result = config.GAME_STATE_WON
            print("GM: Game Over - You Win! All packages delivered.")
            return

        if self.current_fuel < 0:
            self.game_over = True
            self.game_result = config.GAME_STATE_LOST_FUEL
            print("GM: Game Over - Ran out of fuel.")
            return

    def get_player_location(self) -> tuple[int, int] | None:
        return self.player.get_location() if self.player else None

    def get_current_map_grid(self) -> list[str] | None:
        return self.current_level_data.grid if self.current_level_data else None

    def get_current_fuel(self) -> int:
        return self.current_fuel

    def get_current_battery(self) -> int:
        return self.current_battery

    def get_packages_left(self) -> int:
        return self.packages_left_to_deliver

    def get_total_packages_for_level(self) -> int:
        return self.current_level_data.num_packages_to_deliver if self.current_level_data else 0

    def get_destination_locations(self) -> list[tuple[int, int]]:
        return self.destination_tiles_coords if self.is_level_loaded else []

    def get_delivered_package_locations(self) -> set[tuple[int, int]]:
        return self.delivered_packages_coords

    def is_game_over(self) -> bool:
        return self.game_over

    def get_game_result(self) -> str | None:
        return self.game_result
    
    def can_use_hint(self) -> bool:
        return self.current_battery > 0 and not self.game_over
    
    def use_hint(self) -> list[tuple[int, int]] | None:
        if not self.can_use_hint() or not self.player or not self.current_level_data:
            return None

        self.current_battery -= 1 # Assuming HINT_BATTERY_COST_PER_USE is 1
        print(f"GM: Hint used. Battery left: {self.current_battery}")

        # To-Do: Implement the logic to provide hints based on the current game state.

        print("GM: HintProvider not integrated yet. No path provided.")
        return None
    
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
    from level_loader import LevelLoader # For test data
    import os
    import json

    if not os.path.exists("config.py"):
        with open("config.py", "w") as f:
            f.write("START_TILE = 'S'\n")
            f.write("ROAD_TILE = '0'\n")
            f.write("WALL_TILE = '1'\n")
            f.write("DESTINATION_TILE = 'D'\n")
            f.write("FUEL_CONSUMPTION_PER_MOVE = 1\n")
            f.write("GAME_STATE_WON = 'won'\n")
            f.write("GAME_STATE_LOST_FUEL = 'lost_fuel'\n")
            f.write("GAME_STATE_LOST_STUCK = 'lost_stuck'\n")
    
    LEVELS_DIR = "temp_levels_gm_test"
    os.makedirs(LEVELS_DIR, exist_ok=True)
    test_level_path = os.path.join(LEVELS_DIR, "level_1.json")

    sample_level_data_1 = {
        "level_name": "GM Test Level",
        "initial_fuel": 5,
        "hint_battery": 2,
        "map_grid": [
            "S01D",
            "0000",
            "1D10",
            "0000"
        ]
    }
    with open(test_level_path, 'w') as f:
        json.dump(sample_level_data_1, f, indent=2)

    loader = LevelLoader(levels_directory=LEVELS_DIR)
    level_data_obj = loader.load_level_from_file(test_level_path)

    if not level_data_obj:
        print("Test Error: Could not load test level data.")
        exit()

    print("--- GameManager Test ---")
    gm = GameManager()
    gm.load_level(level_data_obj)

    def print_status():
        print(f"\nStatus: Fuel={gm.get_current_fuel()}, Bat={gm.get_current_battery()}, PkgLeft={gm.get_packages_left()}")
        p_loc = gm.get_player_location()
        if p_loc:
            print(f"Player at: (col={p_loc[0]}, row={p_loc[1]})")
        print(f"Delivered at: {gm.get_delivered_package_locations()}")
        if gm.is_game_over():
            print(f"Game Over! Result: {gm.get_game_result()}")
        possible_moves = gm.get_player_possible_moves()
        print(f"Possible moves: {possible_moves}")


    print_status()

    sample_level_start_on_d = {
        "level_name": "Start on D Test",
        "initial_fuel": 5, "hint_battery": 1,
        "map_grid": ["S"] 
    }
    start_on_d_path = os.path.join(LEVELS_DIR, "level_start_on_d.json")
    with open(start_on_d_path, 'w') as f: json.dump(sample_level_start_on_d, f)
    level_start_on_d_obj = loader.load_level_from_file(start_on_d_path)
    if level_start_on_d_obj:
        print("\n--- Test Starting on Destination ---")
        gm_sod = GameManager()
        gm_sod.load_level(level_start_on_d_obj)
        print_status()
        assert gm_sod.get_packages_left() == 0
        assert gm_sod.is_game_over() and gm_sod.get_game_result() == config.GAME_STATE_WON
        print("Start on D test passed.")
    
    print("\n--- Interactive Test with GM Test Level ---")
    gm.load_level(level_data_obj)
    print_status()

    moves = [
        ('d', "Move Right"),      # to (1,0)
        ('d', "Move Right"),      # to (2,0) - Wall, should fail
        ('s', "Move Down"),       # to (1,1)
        ('d', "Move Right"),      # to (2,1)
        ('d', "Move Right"),      # to (3,1) - D at (0,3) not (3,1)
                                  # map: D is (0,3) and (2,1)
                                  # S(0,0) D(0,3)
                                  # 0000
                                  # 1D10   D(2,1)
                                  # 0000
        # My player moves:
        # Start (0,0)
        # d -> (1,0), fuel 4
        # s -> (1,1), fuel 3
        # d -> (2,1) -> This is a D! Package delivered. PkgLeft=1. fuel 2
        # d -> (3,1), fuel 1
        # w -> (3,0) -> This is a D! Package delivered. PkgLeft=0. fuel 0. WIN!
    ]
    
    test_moves = [
        ("d", True), # (0,0) -> (1,0). Fuel 4.
        ("s", True), # (1,0) -> (1,1). Fuel 3.
        ("d", True), # (1,1) -> (2,1) [D]. PkgLeft=1. Fuel 2. Delivered: {(2,1)}
        ("d", True), # (2,1) -> (3,1). Fuel 1.
        ("w", True), # (3,1) -> (3,0) [D]. PkgLeft=0. Fuel 0. Delivered: {(2,1),(0,3)}. WIN!
    ]


    input_map = {'w': 'w', 'a': 'a', 's': 's', 'd': 'd'}

    for i, (move_key, expected_moved) in enumerate(test_moves):
        if gm.is_game_over():
            break
        print(f"\nAttempting move: {move_key}")
        moved = gm.handle_player_move(move_key)
        print(f"Move {move_key}: Player moved = {moved} (Expected: {expected_moved})")
        assert moved == expected_moved, f"Move {i+1} ({move_key}) failed. Expected moved={expected_moved}, got {moved}"
        print_status()

    if gm.is_game_over():
        print(f"\nFinal Game Status: {gm.get_game_result()}")
    else:
        print("\nGame not over yet after test moves.")

    # Test fuel run out
    print("\n--- Test Fuel Run Out ---")
    sample_level_fuel_test = {
        "level_name": "Fuel Test", "initial_fuel": 1, "hint_battery": 0, "map_grid": ["S0D"]
    }
    fuel_test_path = os.path.join(LEVELS_DIR, "level_fuel.json")
    with open(fuel_test_path, 'w') as f: json.dump(sample_level_fuel_test, f)
    level_fuel_obj = loader.load_level_from_file(fuel_test_path)
    if level_fuel_obj:
        gm.load_level(level_fuel_obj)
        print_status()
        gm.handle_player_move('d') # Move to (1,0), Fuel becomes 0
        print_status()
        assert gm.get_current_fuel() == 0
        assert not gm.is_game_over() # Not over yet, can be on 0 fuel
        
        gm.handle_player_move('d') # Attempt move to (2,0) [D] with 0 fuel
        print_status()
        # If rule is "must have >0 fuel to initiate move", then this move fails and game over fuel.
        # If rule is "can move on 0 fuel, then fuel goes <0 and game over", then it moves and wins.
        # My current logic: consume fuel AFTER move. If fuel becomes <=0, game over if not won.
        # My current handle_player_move checks fuel BEFORE move.
        # "if self.current_fuel <= 0 and self.packages_left_to_deliver > 0 :"
        # So, the second 'd' should make it lose.
        assert gm.is_game_over() and gm.get_game_result() == config.GAME_STATE_LOST_FUEL, f"Fuel test failed. Result: {gm.get_game_result()}"
        print("Fuel run out test passed.")

    # Test hint usage
    print("\n--- Test Hint Usage ---")
    gm.load_level(level_data_obj) # Reload original level with 2 battery
    print(f"Initial battery: {gm.get_current_battery()}")
    assert gm.can_use_hint()
    path = gm.use_hint()
    assert path is None # Placeholder returns None
    assert gm.get_current_battery() == 1
    print(f"Battery after 1 hint: {gm.get_current_battery()}")
    path = gm.use_hint()
    assert gm.get_current_battery() == 0
    print(f"Battery after 2 hints: {gm.get_current_battery()}")
    assert not gm.can_use_hint()
    path = gm.use_hint() # Try to use with 0 battery
    assert gm.get_current_battery() == 0 # Should not change
    print("Hint usage test passed (placeholder functionality).")


    # Cleanup dummy files and directory
    os.remove(test_level_path)
    os.remove(start_on_d_path)
    os.remove(fuel_test_path)
    os.rmdir(LEVELS_DIR)
    # if os.path.exists("src/config.py"): os.remove("src/config.py") # If you created it just for this test
    print("\n--- GameManager Test Complete ---")