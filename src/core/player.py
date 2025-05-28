class Player:
    WALL_CHAR = "1"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_up = self.move_down = self.move_left = self.move_right = False

    def set_location(self, x, y):
        self.x = x
        self.y = y

    def get_location(self):
        return self.x, self.y

    def update_state(self, game_map):
        map_height = len(game_map)
        map_width = len(game_map[0])

        # UP
        if self.y > 0 and game_map[self.y - 1][self.x] != self.WALL_CHAR:
            self.move_up = True
        else:
            self.move_up = False

        # DOWN
        if self.y < map_height - 1 and game_map[self.y + 1][self.x] != self.WALL_CHAR:
            self.move_down = True
        else:
            self.move_down = False

        # LEFT
        if self.x > 0 and game_map[self.y][self.x - 1] != self.WALL_CHAR:
            self.move_left = True
        else:
            self.move_left = False

        # RIGHT
        if self.x < map_width - 1 and game_map[self.y][self.x + 1] != self.WALL_CHAR:
            self.move_right = True
        else:
            self.move_right = False

    def move(self, direction_key):
        key = direction_key.lower()
        moved = False

        if self.move_up and key == "w": # Up
            self.y -= 1
            moved = True
        elif self.move_down and key == "s": # Down
            self.y += 1
            moved = True
        elif self.move_left and key == "a": # Left
            self.x -= 1
            moved = True
        elif self.move_right and key == "d": # Right
            self.x += 1
            moved = True
        
        return moved
    
if __name__ == "__main__": # For testing purposes
    map_data = [
        ["S", "0", "1", "0"],
        ["0", "0", "0", "0"],
        ["1", "0", "1", "D"],
        ["0", "0", "0", "0"]
    ]

    def print_map_with_player(current_map, player):
        p_x, p_y = player.get_location()
        print("----- MAP -----")
        for r_idx, row_list in enumerate(current_map):
            row_str = []
            for c_idx, tile in enumerate(row_list):
                if r_idx == p_y and c_idx == p_x:
                    row_str.append("P")
                else:
                    row_str.append(tile)
            print(" ".join(row_str))
        print("---------------")
    
    start_x, start_y = 0, 0
    found_start = False
    for r, row in enumerate(map_data):
        for c, tile in enumerate(row):
            if tile == 'S':
                start_x, start_y = c, r
                found_start = True
                break
        if found_start:
            break
    player = Player(x=start_x, y=start_y)

    print("Welcome to the ████████████ Game Test!")
    print(f"Initial location: {player.get_location()}")
    
    while True:
        player.update_state(map_data)
        
        print_map_with_player(map_data, player)
        px, py = player.get_location()
        print(f"Player at: (col={px}, row={py})")

        possible_moves_str = []
        if player.move_up: possible_moves_str.append("W (Up)")
        if player.move_down: possible_moves_str.append("S (Down)")
        if player.move_left: possible_moves_str.append("A (Left)")
        if player.move_right: possible_moves_str.append("D (Right)")
        print(f"You can move: {', '.join(possible_moves_str) if possible_moves_str else 'Nowhere!'}")

        action = input("Enter your move (w/a/s/d or q to quit): ").strip().lower()

        if action == 'q':
            print("Quitting game. Bye!")
            break
        
        if action in ['w', 'a', 's', 'd']:
            moved = player.move(action)
            if moved:
                print(f"Player moved {action}.")
                new_px, new_py = player.get_location()
                if map_data[new_py][new_px] == 'D':
                    print_map_with_player(map_data, player)
                    print("\n*** Congratulations! You reached the Destination (D)! ***")
                    break
            else:
                print("Cannot move that way (blocked or edge of map).")
        else:
            print(f"Invalid input '{action}'. Please use w, a, s, d, or q.")
        
        print("")