"""
Configuration file for Chess.com Bot
"""

# Chess.com credentials
CHESS_COM_USERNAME = "your_username"  # Replace with your chess.com username
CHESS_COM_PASSWORD = "your_password"  # Replace with your chess.com password

# Engine settings
ENGINE_PATH = "sunfish.py"  # Path to the Sunfish engine
ENGINE_TIME_LIMIT = 5.0  # Time limit for engine calculation in seconds

# Game settings
DEFAULT_TIME_CONTROL = "10+0"  # Default time control for games
OPPONENT_MOVE_TIMEOUT = 60  # Timeout waiting for opponent move in seconds

# Browser settings
BROWSER_HEADLESS = False  # Set to True to run browser in headless mode
BROWSER_TIMEOUT = 30  # Browser timeout in seconds

# Logging settings
LOG_LEVEL = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_FILE = "chess_bot.log"  # Log file name

# Chess.com selectors (may need updates if website changes)
SELECTORS = {
    "login": {
        "username_field": '[name="username"]',
        "password_field": '[name="password"]',
        "submit_button": '[type="submit"]',
        "user_indicator": '.user-username'
    },
    "game": {
        "board": '.board',
        "piece": '.piece',
        "square": '[data-square]',
        "time_control": '[data-cy="time-control-{time_control}"]',
        "play_button": '[data-cy="play-button"]',
        "game_over": '.game-over, .game-result'
    }
}

# Time controls available on chess.com
TIME_CONTROLS = [
    "1+0",    # Bullet
    "3+0",    # Blitz
    "5+0",    # Blitz
    "10+0",   # Rapid
    "15+10",  # Rapid
    "30+0"    # Classical
]