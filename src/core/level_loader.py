import json
import os

class LevelData:
    def __init__(self, name, initial_fuel, hint_battery, grid, player_start_pos, 
                 destination_coords, num_packages_to_deliver, grid_width, grid_height):
        self.name = name
        self.initial_fuel = initial_fuel
        self.hint_battery = hint_battery
        self.grid = grid
        self.player_start_pos = player_start_pos
        self.destination_coords = destination_coords
        self.num_packages_to_deliver = num_packages_to_deliver
        self.grid_width = grid_width
        self.grid_height = grid_height

    def __str__(self):
        return (f"LevelData(Name: {self.name}, Fuel: {self.initial_fuel}, Battery: {self.hint_battery}, "
                f"Start: {self.player_start_pos}, Destinations: {self.destination_coords}, "
                f"Packages: {self.num_packages_to_deliver}, Grid: {self.grid_width}x{self.grid_height})")

class LevelLoader:
    def __init__(self, levels_directory="assets/levels"):
        self.levels_directory = levels_directory

    def _parse_map_grid(self, map_grid_data):
        if not map_grid_data or not isinstance(map_grid_data, list):
            print("Warning: map_grid_data is empty or not a list.")
            return None, [], 0, 0, 0

        height = len(map_grid_data)
        width = len(map_grid_data[0]) if height > 0 else 0

        player_start_pos = None
        destination_coords = []
        num_packages = 0

        for r, row_str in enumerate(map_grid_data):
            if len(row_str) != width:
                raise ValueError(f"Inconsistent row length in map_grid. Expected {width}, got {len(row_str)} for row {r}.")
            for c, char in enumerate(row_str):
                if char == 'S':
                    if player_start_pos is not None:
                        raise ValueError("Multiple start positions ('S') found in the map grid.")
                    player_start_pos = (r, c)
                elif char == 'D':
                    destination_coords.append((r, c))
                    num_packages += 1
        
        if player_start_pos is None:
            raise ValueError("No start position ('S') found in the map grid.")
        if num_packages == 0:
            print("Warning: No destination points ('D') found in the map grid.")


        return player_start_pos, destination_coords, num_packages, width, height

    def load_level_by_number(self, level_number: int) -> LevelData | None:
        filename = f"level_{level_number}.json"
        filepath = os.path.join(self.levels_directory, filename)
        return self.load_level_from_file(filepath)

    def load_level_from_file(self, filepath: str) -> LevelData | None:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            level_name = data.get("level_name", "Unnamed Level")
            initial_fuel = data.get("initial_fuel")
            hint_battery = data.get("hint_battery")
            map_grid = data.get("map_grid")

            if initial_fuel is None or hint_battery is None or map_grid is None:
                raise ValueError("JSON file is missing one or more required fields: "
                                 "'initial_fuel', 'hint_battery', 'map_grid'.")
            
            if not isinstance(initial_fuel, int) or initial_fuel < 0:
                raise ValueError(f"initial_fuel must be a non-negative integer. Got: {initial_fuel}")
            if not isinstance(hint_battery, int) or hint_battery < 0:
                raise ValueError(f"hint_battery must be a non-negative integer. Got: {hint_battery}")
            if not isinstance(map_grid, list) or not all(isinstance(row, str) for row in map_grid):
                 raise ValueError(f"map_grid must be a list of strings. Got: {type(map_grid)}")


            player_start_pos, destination_coords, num_packages, width, height = self._parse_map_grid(map_grid)
            
            return LevelData(
                name=level_name,
                initial_fuel=initial_fuel,
                hint_battery=hint_battery,
                grid=map_grid,
                player_start_pos=player_start_pos,
                destination_coords=destination_coords,
                num_packages_to_deliver=num_packages,
                grid_width=width,
                grid_height=height
            )

        except FileNotFoundError:
            print(f"Error: Level file not found at {filepath}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {filepath}")
            return None
        except ValueError as e:
            print(f"Error: Data validation failed for {filepath}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while loading {filepath}: {e}")
            return None

    def get_available_levels_count(self) -> int:
        count = 0
        if not os.path.isdir(self.levels_directory):
            print(f"Warning: Levels directory '{self.levels_directory}' not found.")
            return 0
            
        i = 1
        while True:
            filename = f"level_{i}.json"
            filepath = os.path.join(self.levels_directory, filename)
            if os.path.exists(filepath):
                count += 1
                i += 1
            else:
                break
        return count

if __name__ == "__main__":
    LEVELS_DIR = "./"
    os.makedirs(LEVELS_DIR, exist_ok=True)

    sample_level_data_1 = {
        "level_name": "Tutorial Route",
        "initial_fuel": 50,
        "hint_battery": 2,
        "map_grid": [
            "S010",
            "0010",
            "101D",
            "000D"
        ]
    }
    with open(os.path.join(LEVELS_DIR, "level_1.json"), 'w') as f:
        json.dump(sample_level_data_1, f, indent=2)

    sample_level_data_2 = {
        "level_name": "Second Challenge",
        "initial_fuel": 30,
        "hint_battery": 1,
        "map_grid": [
            "S00",
            "01D",
            "000"
        ]
    }
    with open(os.path.join(LEVELS_DIR, "level_2.json"), 'w') as f:
        json.dump(sample_level_data_2, f, indent=2)
    
    # Test bad level (no start position)
    sample_level_data_bad = {
        "level_name": "Bad Level - No Start",
        "initial_fuel": 10,
        "hint_battery": 1,
        "map_grid": [
            "000",
            "01D"
        ]
    }
    with open(os.path.join(LEVELS_DIR, "level_3_bad_start.json"), 'w') as f:
        json.dump(sample_level_data_bad, f, indent=2)

    sample_level_data_bad_field = {
        # "level_name": "Bad Level - Missing Fuel", # Deliberately missing initial_fuel
        "hint_battery": 1,
        "map_grid": [
            "S00",
            "01D"
        ]
    }
    with open(os.path.join(LEVELS_DIR, "level_4_bad_field.json"), 'w') as f:
        json.dump(sample_level_data_bad_field, f, indent=2)


    loader = LevelLoader(levels_directory=LEVELS_DIR)

    print(f"Found {loader.get_available_levels_count()} levels.")

    level1_data = loader.load_level_from_file("level_1.json")
    if level1_data:
        print("\nLoaded Level 1:")
        print(level1_data)

    level2_data = loader.load_level_from_file(os.path.join(LEVELS_DIR, "level_2.json"))
    if level2_data:
        print("\nLoaded Level 2:")
        print(level2_data)

    print("\nAttempting to load non-existent level:")
    level_non_existent = loader.load_level_by_number(99)
    if level_non_existent is None:
        print("Correctly handled non-existent level.")

    print("\nAttempting to load bad level (no start):")
    level_bad_start = loader.load_level_from_file(os.path.join(LEVELS_DIR, "level_3_bad_start.json"))
    if level_bad_start is None:
        print("Correctly handled bad level data (no start).")

    print("\nAttempting to load bad level (missing field):")
    level_bad_field = loader.load_level_from_file(os.path.join(LEVELS_DIR, "level_4_bad_field.json"))
    if level_bad_field is None:
        print("Correctly handled bad level data (missing field).")