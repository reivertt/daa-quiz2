class Configurations:
    def __init__(self):
        self.levels = 5
        self.start_level = 1
        self.max_level_unlocked = 1
        self.hint_provider = None
        self.FPS = 60
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        self.tile_size = 40

        self.START_TILE = 'S'
        self.WALL_TILE = '#'
        self.DESTINATION_TILE = 'D'

        self.DEFAULT_FUEL_CONSUMPTION_PER_MOVE = 1
        self.HINT_BATTERY_COST_PER_USE = 1

        self.GAME_STATE_PLAYING = "playing"
        self.GAME_STATE_CONFIRM_HINT = "confirm_hint"
        self.GAME_STATE_PAUSED = "paused"
        self.GAME_STATE_LEVEL_COMPLETE = "level_complete"
        self.GAME_STATE_GAME_OVER = "game_over"

        self.PLAYER_ACTION_MOVE_UP = 'w'
        self.PLAYER_ACTION_MOVE_DOWN = 's'
        self.PLAYER_ACTION_MOVE_LEFT = 'a'
        self.PLAYER_ACTION_MOVE_RIGHT = 'd'

        self.DIRECTION_INPUT_MAP = {
            'up': self.PLAYER_ACTION_MOVE_UP,
            'down': self.PLAYER_ACTION_MOVE_DOWN,
            'left': self.PLAYER_ACTION_MOVE_LEFT,
            'right': self.PLAYER_ACTION_MOVE_RIGHT,
        }