"""
Configuration file for the Chess.com Bot
Enhanced with comprehensive settings and advanced features
"""

import os
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

class GameType(Enum):
    """Types of chess games"""
    RAPID = "rapid"
    BLITZ = "blitz"
    BULLET = "bullet"
    DAILY = "daily"
    CUSTOM = "custom"

class EngineType(Enum):
    """Types of chess engines"""
    SUNFISH = "sunfish"
    STOCKFISH = "stockfish"
    CUSTOM = "custom"

class DifficultyLevel(Enum):
    """Difficulty levels for playing against computer"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class EngineSettings:
    """Settings for chess engine"""
    engine_type: EngineType = EngineType.SUNFISH
    search_depth: int = 5
    move_time_limit: float = 2.0
    nodes_limit: int = 1000000
    multi_pv: int = 1
    contempt: int = 0
    skill_level: int = 20
    custom_engine_path: str = ""
    engine_options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GameSettings:
    """Settings for game play"""
    game_type: GameType = GameType.RAPID
    time_control: str = "10+0"
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    auto_accept_draws: bool = False
    auto_resign: bool = True
    resign_threshold: int = -1000
    draw_threshold: int = 50
    max_game_length: int = 200  # moves
    opening_book: bool = True
    book_depth: int = 10

@dataclass
class BrowserSettings:
    """Settings for browser automation"""
    headless: bool = False
    window_size: Tuple[int, int] = (1920, 1080)
    user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    disable_images: bool = True
    disable_css: bool = False
    disable_javascript: bool = False
    proxy: str = ""
    user_data_dir: str = ""
    incognito: bool = True
    disable_extensions: bool = True
    disable_plugins: bool = True
    disable_popup_blocking: bool = True
    disable_notifications: bool = True
    disable_geolocation: bool = True
    disable_media_stream: bool = True
    disable_automatic_downloads: bool = True

@dataclass
class MoveSettings:
    """Settings for move detection and execution"""
    move_detection_delay: float = 0.5
    move_execution_delay: float = 0.2
    retry_attempts: int = 3
    retry_delay: float = 1.0
    validate_moves: bool = True
    log_all_moves: bool = True
    save_game_pgn: bool = True
    save_game_analysis: bool = True

@dataclass
class LoggingSettings:
    """Settings for logging and monitoring"""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    log_file: str = "chess_bot.log"
    log_to_file: bool = True
    log_to_console: bool = True
    log_moves: bool = True
    log_engine_analysis: bool = True
    log_browser_actions: bool = False
    log_performance: bool = True

@dataclass
class SafetySettings:
    """Settings for safety and fair play"""
    max_games_per_session: int = 10
    session_duration_limit: int = 3600  # seconds
    cooldown_between_games: int = 30  # seconds
    random_move_delay: Tuple[float, float] = (0.5, 2.0)
    human_like_behavior: bool = True
    avoid_suspicious_patterns: bool = True
    max_consecutive_wins: int = 5
    max_consecutive_losses: int = 3
    auto_pause_on_suspicion: bool = True

@dataclass
class AnalysisSettings:
    """Settings for game analysis"""
    analyze_games: bool = True
    save_analysis: bool = True
    analysis_depth: int = 15
    analysis_time_limit: float = 5.0
    generate_report: bool = True
    include_opening_analysis: bool = True
    include_middlegame_analysis: bool = True
    include_endgame_analysis: bool = True
    save_analysis_format: str = "json"  # json, pgn, txt

@dataclass
class NotificationSettings:
    """Settings for notifications"""
    enable_notifications: bool = False
    notify_on_game_start: bool = True
    notify_on_game_end: bool = True
    notify_on_move: bool = False
    notify_on_error: bool = True
    notification_method: str = "console"  # console, email, webhook
    email_settings: Dict[str, str] = field(default_factory=dict)
    webhook_url: str = ""

class Config:
    """Enhanced configuration class for the chess bot"""
    
    # Chess.com settings
    CHESS_COM_URL = "https://www.chess.com"
    LOGIN_URL = "https://www.chess.com/login"
    PLAY_URL = "https://www.chess.com/play/online"
    COMPUTER_URL = "https://www.chess.com/play/computer"
    PUZZLES_URL = "https://www.chess.com/puzzles"
    ANALYSIS_URL = "https://www.chess.com/analysis"
    
    # Engine settings
    engine = EngineSettings()
    
    # Game settings
    game = GameSettings()
    
    # Browser settings
    browser = BrowserSettings()
    
    # Move settings
    move = MoveSettings()
    
    # Logging settings
    logging = LoggingSettings()
    
    # Safety settings
    safety = SafetySettings()
    
    # Analysis settings
    analysis = AnalysisSettings()
    
    # Notification settings
    notification = NotificationSettings()
    
    # CSS Selectors for Chess.com (enhanced)
    SELECTORS = {
        # Login
        "username_field": "#username",
        "password_field": "#password",
        "login_button": "button[type='submit']",
        "user_username": ".user-username",
        "login_error": ".login-error",
        
        # Game navigation
        "play_online_button": "[data-cy='play-online-button']",
        "play_computer_button": "[data-cy='play-computer-button']",
        "start_game_button": "[data-cy='start-game-button']",
        "accept_challenge_button": "[data-cy='accept-challenge-button']",
        "decline_challenge_button": "[data-cy='decline-challenge-button']",
        
        # Game board
        "board": ".board",
        "piece": "[data-square='{square}']",
        "square": "[data-square='{square}']",
        "last_move": ".last-move",
        "move_list": ".move-list",
        "game_info": ".game-info",
        
        # Game controls
        "resign_button": "[data-cy='resign-button']",
        "draw_button": "[data-cy='draw-button']",
        "abort_button": "[data-cy='abort-button']",
        "flip_board_button": "[data-cy='flip-board-button']",
        
        # Clocks and turn indicators
        "clock_player_turn": ".clock-player-turn",
        "clock_opponent_turn": ".clock-opponent-turn",
        "white_clock": ".clock-white",
        "black_clock": ".clock-black",
        
        # Game status
        "game_over": ".game-over",
        "check_indicator": ".check-indicator",
        "checkmate_indicator": ".checkmate-indicator",
        "stalemate_indicator": ".stalemate-indicator",
        "draw_indicator": ".draw-indicator",
        
        # Time controls
        "time_control": "[data-cy='time-control-{time}']",
        "custom_time_control": "[data-cy='custom-time-control']",
        
        # Difficulty settings (for computer games)
        "difficulty_beginner": "[data-cy='difficulty-beginner']",
        "difficulty_intermediate": "[data-cy='difficulty-intermediate']",
        "difficulty_advanced": "[data-cy='difficulty-advanced']",
        "difficulty_expert": "[data-cy='difficulty-expert']",
        
        # Chat and communication
        "chat_input": ".chat-input",
        "chat_messages": ".chat-messages",
        "mute_chat_button": "[data-cy='mute-chat-button']",
        
        # Analysis and review
        "analysis_button": "[data-cy='analysis-button']",
        "review_button": "[data-cy='review-button']",
        "share_button": "[data-cy='share-button']",
        
        # Notifications
        "notification_popup": ".notification-popup",
        "notification_close": ".notification-close",
        
        # Error handling
        "error_message": ".error-message",
        "loading_indicator": ".loading-indicator",
        "connection_lost": ".connection-lost",
    }
    
    # Move detection settings
    MOVE_DETECTION_DELAY = 0.5  # seconds
    GAME_CHECK_INTERVAL = 1.0  # seconds
    
    # Performance settings
    PERFORMANCE_MONITORING = True
    MEMORY_LIMIT_MB = 512
    CPU_LIMIT_PERCENT = 80
    
    # Database settings (for storing games and analysis)
    DATABASE_ENABLED = False
    DATABASE_TYPE = "sqlite"  # sqlite, postgresql, mysql
    DATABASE_URL = "sqlite:///chess_bot.db"
    
    # API settings (for external integrations)
    API_ENABLED = False
    API_PORT = 8080
    API_HOST = "localhost"
    API_KEY = ""
    
    # Machine learning settings
    ML_ENABLED = False
    ML_MODEL_PATH = ""
    ML_PREDICTION_THRESHOLD = 0.7
    
    # Opening book settings
    OPENING_BOOK_ENABLED = True
    OPENING_BOOK_PATH = "openings.pgn"
    OPENING_BOOK_DEPTH = 10
    OPENING_BOOK_VARIANCE = 0.1
    
    # Endgame tablebase settings
    ENDGAME_TABLEBASE_ENABLED = False
    ENDGAME_TABLEBASE_PATH = ""
    ENDGAME_TABLEBASE_PIECES = 5  # max pieces for tablebase
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        config = cls()
        
        # Engine settings
        config.engine.engine_type = EngineType(os.getenv('ENGINE_TYPE', 'sunfish'))
        config.engine.search_depth = int(os.getenv('SEARCH_DEPTH', config.engine.search_depth))
        config.engine.move_time_limit = float(os.getenv('MOVE_TIME_LIMIT', config.engine.move_time_limit))
        config.engine.nodes_limit = int(os.getenv('NODES_LIMIT', config.engine.nodes_limit))
        config.engine.skill_level = int(os.getenv('SKILL_LEVEL', config.engine.skill_level))
        
        # Game settings
        config.game.game_type = GameType(os.getenv('GAME_TYPE', 'rapid'))
        config.game.time_control = os.getenv('TIME_CONTROL', config.game.time_control)
        config.game.difficulty = DifficultyLevel(os.getenv('DIFFICULTY', 'intermediate'))
        config.game.auto_accept_draws = os.getenv('AUTO_ACCEPT_DRAWS', 'false').lower() == 'true'
        config.game.auto_resign = os.getenv('AUTO_RESIGN', 'true').lower() == 'true'
        config.game.resign_threshold = int(os.getenv('RESIGN_THRESHOLD', config.game.resign_threshold))
        
        # Browser settings
        config.browser.headless = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
        config.browser.disable_images = os.getenv('DISABLE_IMAGES', 'true').lower() == 'true'
        config.browser.incognito = os.getenv('INCOGNITO', 'true').lower() == 'true'
        
        # Logging settings
        config.logging.log_level = os.getenv('LOG_LEVEL', config.logging.log_level)
        config.logging.log_file = os.getenv('LOG_FILE', config.logging.log_file)
        config.logging.log_to_file = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
        
        # Safety settings
        config.safety.max_games_per_session = int(os.getenv('MAX_GAMES_PER_SESSION', config.safety.max_games_per_session))
        config.safety.session_duration_limit = int(os.getenv('SESSION_DURATION_LIMIT', config.safety.session_duration_limit))
        config.safety.human_like_behavior = os.getenv('HUMAN_LIKE_BEHAVIOR', 'true').lower() == 'true'
        
        # Analysis settings
        config.analysis.analyze_games = os.getenv('ANALYZE_GAMES', 'true').lower() == 'true'
        config.analysis.analysis_depth = int(os.getenv('ANALYSIS_DEPTH', config.analysis.analysis_depth))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'engine': {
                'engine_type': self.engine.engine_type.value,
                'search_depth': self.engine.search_depth,
                'move_time_limit': self.engine.move_time_limit,
                'nodes_limit': self.engine.nodes_limit,
                'skill_level': self.engine.skill_level,
            },
            'game': {
                'game_type': self.game.game_type.value,
                'time_control': self.game.time_control,
                'difficulty': self.game.difficulty.value,
                'auto_accept_draws': self.game.auto_accept_draws,
                'auto_resign': self.game.auto_resign,
                'resign_threshold': self.game.resign_threshold,
            },
            'browser': {
                'headless': self.browser.headless,
                'window_size': self.browser.window_size,
                'disable_images': self.browser.disable_images,
                'incognito': self.browser.incognito,
            },
            'logging': {
                'log_level': self.logging.log_level,
                'log_file': self.logging.log_file,
                'log_to_file': self.logging.log_to_file,
            },
            'safety': {
                'max_games_per_session': self.safety.max_games_per_session,
                'session_duration_limit': self.safety.session_duration_limit,
                'human_like_behavior': self.safety.human_like_behavior,
            },
            'analysis': {
                'analyze_games': self.analysis.analyze_games,
                'analysis_depth': self.analysis.analysis_depth,
            }
        }
    
    def save_to_file(self, filename: str = "bot_config.json"):
        """Save configuration to file"""
        import json
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load_from_file(self, filename: str = "bot_config.json"):
        """Load configuration from file"""
        import json
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self._update_from_dict(data)
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        if 'engine' in data:
            for key, value in data['engine'].items():
                if hasattr(self.engine, key):
                    setattr(self.engine, key, value)
        
        if 'game' in data:
            for key, value in data['game'].items():
                if hasattr(self.game, key):
                    setattr(self.game, key, value)
        
        if 'browser' in data:
            for key, value in data['browser'].items():
                if hasattr(self.browser, key):
                    setattr(self.browser, key, value)
        
        if 'logging' in data:
            for key, value in data['logging'].items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)
        
        if 'safety' in data:
            for key, value in data['safety'].items():
                if hasattr(self.safety, key):
                    setattr(self.safety, key, value)
        
        if 'analysis' in data:
            for key, value in data['analysis'].items():
                if hasattr(self.analysis, key):
                    setattr(self.analysis, key, value)

# Default configuration instance
config = Config.from_env()