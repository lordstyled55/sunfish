"""
Configuration file for the Chess.com Bot
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for the chess bot"""
    
    # Chess.com settings
    CHESS_COM_URL = "https://www.chess.com"
    LOGIN_URL = "https://www.chess.com/login"
    PLAY_URL = "https://www.chess.com/play/online"
    
    # Browser settings
    BROWSER_HEADLESS = False
    BROWSER_WINDOW_SIZE = (1920, 1080)
    BROWSER_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    
    # Game settings
    DEFAULT_TIME_CONTROL = "10+0"
    MOVE_TIME_LIMIT = 2.0  # seconds
    SEARCH_DEPTH = 5
    
    # Engine settings
    ENGINE_NAME = "sunfish"
    ENGINE_VERSION = "2023"
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    # CSS Selectors for Chess.com
    SELECTORS = {
        "username_field": "#username",
        "password_field": "#password",
        "login_button": "button[type='submit']",
        "user_username": ".user-username",
        "play_online_button": "[data-cy='play-online-button']",
        "start_game_button": "[data-cy='start-game-button']",
        "board": ".board",
        "piece": "[data-square='{square}']",
        "last_move": ".last-move",
        "clock_player_turn": ".clock-player-turn",
        "game_over": ".game-over",
        "time_control": "[data-cy='time-control-{time}']"
    }
    
    # Move detection settings
    MOVE_DETECTION_DELAY = 0.5  # seconds
    GAME_CHECK_INTERVAL = 1.0  # seconds
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        config = cls()
        
        # Override with environment variables
        config.BROWSER_HEADLESS = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
        config.DEFAULT_TIME_CONTROL = os.getenv('TIME_CONTROL', config.DEFAULT_TIME_CONTROL)
        config.MOVE_TIME_LIMIT = float(os.getenv('MOVE_TIME_LIMIT', config.MOVE_TIME_LIMIT))
        config.SEARCH_DEPTH = int(os.getenv('SEARCH_DEPTH', config.SEARCH_DEPTH))
        config.LOG_LEVEL = os.getenv('LOG_LEVEL', config.LOG_LEVEL)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'browser_headless': self.BROWSER_HEADLESS,
            'browser_window_size': self.BROWSER_WINDOW_SIZE,
            'default_time_control': self.DEFAULT_TIME_CONTROL,
            'move_time_limit': self.MOVE_TIME_LIMIT,
            'search_depth': self.SEARCH_DEPTH,
            'log_level': self.LOG_LEVEL
        }

# Default configuration instance
config = Config.from_env()