# Constants for the game

# Game settings
CELL_SIZE = 40
CELL_NUMBER = 25
SCREEN_WIDTH = CELL_NUMBER * CELL_SIZE
SCREEN_HEIGHT = CELL_NUMBER * CELL_SIZE

# Colors
GRASS_COLOR = (167, 209, 61)
GRASS_COLOR_ALT = (175, 215, 70)
TEXT_COLOR = (56, 74, 12)

# Font settings
FONT_SIZE = 25

# Game speed (milliseconds between updates)
GAME_SPEED = 150

# Network settings
DEFAULT_PORT = 5555
MAX_PLAYERS = 2
BUFFER_SIZE = 4096
SERVER_TIMEOUT = 30

# Game modes
MODE_SINGLE_PLAYER = "single_player"
MODE_TWO_PLAYER = "two_player"
MODE_MULTIPLAYER_HOST = "multiplayer_host"
MODE_MULTIPLAYER_CLIENT = "multiplayer_client"