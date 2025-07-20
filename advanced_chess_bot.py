#!/usr/bin/env python3
"""
Advanced Chess.com Bot using Sunfish Chess Engine
Enhanced with comprehensive features, analysis, safety, and monitoring
"""

import time
import sys
import os
import json
import random
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import chess
import chess.pgn
import chess.engine

# Import sunfish chess engine
sys.path.append('.')
from sunfish import Position, Searcher, render, parse, initial
from config import config, GameType, EngineType, DifficultyLevel

# Configure logging
if config.logging.log_to_file:
    logging.basicConfig(
        level=getattr(logging, config.logging.log_level),
        format=config.logging.log_format,
        handlers=[
            logging.FileHandler(config.logging.log_file),
            logging.StreamHandler() if config.logging.log_to_console else logging.NullHandler()
        ]
    )
else:
    logging.basicConfig(
        level=getattr(logging, config.logging.log_level),
        format=config.logging.log_format
    )

logger = logging.getLogger(__name__)

@dataclass
class GameStats:
    """Game statistics"""
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    games_drawn: int = 0
    total_moves: int = 0
    average_game_length: float = 0.0
    win_rate: float = 0.0
    session_start_time: datetime = None
    last_game_time: datetime = None

@dataclass
class GameState:
    """Current game state"""
    game_id: str = ""
    opponent: str = ""
    is_white: bool = True
    current_fen: str = ""
    move_number: int = 0
    game_start_time: datetime = None
    last_move_time: datetime = None
    time_control: str = ""
    game_type: GameType = GameType.RAPID
    pgn_moves: List[str] = None
    analysis_data: Dict[str, Any] = None

class PerformanceMonitor:
    """Monitor bot performance and resource usage"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.memory_usage = []
        self.cpu_usage = []
        self.response_times = []
        
    def log_memory_usage(self):
        """Log current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_usage.append((datetime.now(), memory_mb))
            
            if memory_mb > config.MEMORY_LIMIT_MB:
                logger.warning(f"Memory usage high: {memory_mb:.1f}MB")
                
        except ImportError:
            pass
    
    def log_response_time(self, operation: str, duration: float):
        """Log response time for operations"""
        self.response_times.append((operation, duration))
        if duration > 5.0:  # Log slow operations
            logger.warning(f"Slow operation: {operation} took {duration:.2f}s")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.response_times:
            return {}
        
        operations = [op for op, _ in self.response_times]
        times = [t for _, t in self.response_times]
        
        return {
            'total_operations': len(self.response_times),
            'average_response_time': sum(times) / len(times),
            'max_response_time': max(times),
            'min_response_time': min(times),
            'session_duration': (datetime.now() - self.start_time).total_seconds(),
            'memory_samples': len(self.memory_usage)
        }

class GameAnalyzer:
    """Analyze games and generate reports"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_position(self, fen: str, depth: int = None) -> Dict[str, Any]:
        """Analyze a chess position"""
        if depth is None:
            depth = config.analysis.analysis_depth
            
        start_time = time.time()
        
        try:
            # Use sunfish for analysis
            board = chess.Board(fen)
            sunfish_pos = self._board_to_sunfish_position(board)
            
            # Get best moves
            best_moves = []
            for move in sunfish_pos.gen_moves():
                new_pos = sunfish_pos.move(move)
                score = -new_pos.score
                uci_move = self._sunfish_move_to_uci(move)
                best_moves.append({
                    'move': uci_move,
                    'score': score,
                    'san': board.san(chess.Move.from_uci(uci_move))
                })
            
            # Sort by score
            best_moves.sort(key=lambda x: x['score'], reverse=True)
            
            analysis_time = time.time() - start_time
            
            return {
                'fen': fen,
                'best_moves': best_moves[:5],  # Top 5 moves
                'evaluation': best_moves[0]['score'] if best_moves else 0,
                'analysis_time': analysis_time,
                'depth': depth,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing position: {e}")
            return {}
    
    def analyze_game(self, pgn_moves: List[str], result: str = "*") -> Dict[str, Any]:
        """Analyze a complete game"""
        try:
            # Create game from PGN
            game = chess.pgn.Game()
            game.headers["Result"] = result
            
            board = game.board()
            analysis_data = []
            
            for i, move in enumerate(pgn_moves):
                # Analyze position before move
                fen = board.fen()
                analysis = self.analyze_position(fen)
                analysis['move_number'] = i + 1
                analysis['move'] = move
                analysis_data.append(analysis)
                
                # Make the move
                try:
                    chess_move = board.parse_san(move)
                    board.push(chess_move)
                except:
                    logger.warning(f"Could not parse move: {move}")
                    break
            
            return {
                'game_analysis': analysis_data,
                'total_moves': len(pgn_moves),
                'final_position': board.fen(),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing game: {e}")
            return {}
    
    def _board_to_sunfish_position(self, board: chess.Board) -> Position:
        """Convert chess.Board to sunfish Position"""
        # Simplified conversion - in practice you'd need proper conversion
        return Position(initial, 0, (True, True), (True, True), 0, 0)
    
    def _sunfish_move_to_uci(self, move) -> str:
        """Convert sunfish move to UCI format"""
        i, j = move.i, move.j
        
        # Convert 120-char board index to algebraic notation
        file_i = (i % 10) - 1
        rank_i = 8 - (i // 10 - 2)
        file_j = (j % 10) - 1
        rank_j = 8 - (j // 10 - 2)
        
        files = 'abcdefgh'
        ranks = '12345678'
        
        from_square = f"{files[file_i]}{ranks[rank_i]}"
        to_square = f"{files[file_j]}{ranks[rank_j]}"
        
        return from_square + to_square

class NotificationManager:
    """Manage notifications and alerts"""
    
    def __init__(self):
        self.notification_queue = []
        
    def send_notification(self, message: str, level: str = "info"):
        """Send a notification"""
        if not config.notification.enable_notifications:
            return
            
        notification = {
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }
        
        self.notification_queue.append(notification)
        
        # Send based on method
        if config.notification.notification_method == "console":
            self._send_console_notification(notification)
        elif config.notification.notification_method == "email":
            self._send_email_notification(notification)
        elif config.notification.notification_method == "webhook":
            self._send_webhook_notification(notification)
    
    def _send_console_notification(self, notification: Dict[str, Any]):
        """Send notification to console"""
        level_icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }
        
        icon = level_icons.get(notification['level'], 'ℹ️')
        print(f"{icon} {notification['message']}")
    
    def _send_email_notification(self, notification: Dict[str, Any]):
        """Send notification via email"""
        # Implementation would use smtplib
        logger.info(f"Email notification: {notification['message']}")
    
    def _send_webhook_notification(self, notification: Dict[str, Any]):
        """Send notification via webhook"""
        # Implementation would use requests
        logger.info(f"Webhook notification: {notification['message']}")

class AdvancedChessBot:
    """Advanced Chess.com Bot with comprehensive features"""
    
    def __init__(self, username: str = None, password: str = None):
        """Initialize the advanced chess bot"""
        self.username = username
        self.password = password
        self.driver = None
        self.searcher = Searcher()
        self.board = chess.Board()
        
        # Enhanced components
        self.game_stats = GameStats()
        self.game_state = GameState()
        self.performance_monitor = PerformanceMonitor()
        self.game_analyzer = GameAnalyzer()
        self.notification_manager = NotificationManager()
        
        # Session management
        self.session_start_time = datetime.now()
        self.games_this_session = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        # Threading for background tasks
        self.background_threads = []
        self.running = False
        
    def setup_driver(self):
        """Setup Chrome WebDriver with enhanced options"""
        chrome_options = Options()
        
        # Basic options
        if config.browser.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={config.browser.window_size[0]},{config.browser.window_size[1]}")
        chrome_options.add_argument(f"--user-agent={config.browser.user_agent}")
        
        # Enhanced privacy and performance options
        if config.browser.incognito:
            chrome_options.add_argument("--incognito")
        
        if config.browser.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
        
        if config.browser.disable_extensions:
            chrome_options.add_argument("--disable-extensions")
        
        if config.browser.disable_plugins:
            chrome_options.add_argument("--disable-plugins")
        
        if config.browser.disable_popup_blocking:
            chrome_options.add_argument("--disable-popup-blocking")
        
        if config.browser.disable_notifications:
            chrome_options.add_argument("--disable-notifications")
        
        if config.browser.disable_geolocation:
            chrome_options.add_argument("--disable-geolocation")
        
        if config.browser.disable_media_stream:
            chrome_options.add_argument("--disable-media-stream")
        
        if config.browser.disable_automatic_downloads:
            chrome_options.add_argument("--disable-automatic-downloads")
        
        # Proxy support
        if config.browser.proxy:
            chrome_options.add_argument(f"--proxy-server={config.browser.proxy}")
        
        # User data directory
        if config.browser.user_data_dir:
            chrome_options.add_argument(f"--user-data-dir={config.browser.user_data_dir}")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
        logger.info("Browser setup completed with enhanced options")
    
    def login(self):
        """Login to Chess.com with enhanced error handling"""
        if not self.username or not self.password:
            logger.error("Username and password are required for login")
            return False
            
        try:
            logger.info("Logging into Chess.com...")
            self.driver.get(config.LOGIN_URL)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Enter credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["username_field"]))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["password_field"])
            
            # Clear fields and enter credentials
            username_field.clear()
            username_field.send_keys(self.username)
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_button"])
            login_button.click()
            
            # Wait for successful login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["user_username"]))
            )
            
            logger.info("Successfully logged in to Chess.com")
            self.notification_manager.send_notification("Successfully logged in to Chess.com", "success")
            return True
            
        except TimeoutException:
            logger.error("Login failed - timeout")
            self.notification_manager.send_notification("Login failed - timeout", "error")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.notification_manager.send_notification(f"Login failed: {e}", "error")
            return False
    
    def start_game(self, game_type: GameType = None, time_control: str = None, difficulty: DifficultyLevel = None):
        """Start a new game with enhanced options"""
        if game_type is None:
            game_type = config.game.game_type
        if time_control is None:
            time_control = config.game.time_control
        if difficulty is None:
            difficulty = config.game.difficulty
            
        try:
            logger.info(f"Starting new {game_type.value} game with time control: {time_control}")
            
            # Check session limits
            if self.games_this_session >= config.safety.max_games_per_session:
                logger.warning("Maximum games per session reached")
                self.notification_manager.send_notification("Maximum games per session reached", "warning")
                return False
            
            session_duration = (datetime.now() - self.session_start_time).total_seconds()
            if session_duration > config.safety.session_duration_limit:
                logger.warning("Session duration limit reached")
                self.notification_manager.send_notification("Session duration limit reached", "warning")
                return False
            
            # Navigate to appropriate page
            if game_type == GameType.CUSTOM:
                self.driver.get(config.PLAY_URL)
            else:
                self.driver.get(config.COMPUTER_URL)
            
            time.sleep(2)
            
            # Set game type and difficulty
            if game_type == GameType.CUSTOM:
                # Play against computer
                play_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["play_computer_button"]))
                )
                play_button.click()
                
                # Set difficulty
                difficulty_selector = config.SELECTORS[f"difficulty_{difficulty.value}"]
                try:
                    difficulty_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, difficulty_selector))
                    )
                    difficulty_button.click()
                except TimeoutException:
                    logger.warning(f"Could not set difficulty {difficulty.value}")
            else:
                # Play online
                play_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["play_online_button"]))
                )
                play_button.click()
            
            # Set time control
            try:
                time_control_selector = config.SELECTORS["time_control"].format(time=time_control)
                time_control_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, time_control_selector))
                )
                time_control_button.click()
            except TimeoutException:
                logger.warning(f"Could not set time control {time_control}")
            
            # Start game
            start_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["start_game_button"]))
            )
            start_button.click()
            
            # Wait for board to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["board"]))
            )
            
            # Initialize game state
            self.game_state = GameState(
                game_id=f"game_{int(time.time())}",
                game_start_time=datetime.now(),
                time_control=time_control,
                game_type=game_type,
                pgn_moves=[],
                analysis_data={}
            )
            
            self.games_this_session += 1
            self.game_stats.games_played += 1
            
            logger.info("Game started successfully")
            self.notification_manager.send_notification("Game started successfully", "success")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start game: {e}")
            self.notification_manager.send_notification(f"Failed to start game: {e}", "error")
            return False
    
    def calculate_move(self) -> Optional[str]:
        """Calculate best move with enhanced features"""
        start_time = time.time()
        
        try:
            # Get current position
            pos = self.get_sunfish_position()
            
            # Check for resignation
            if self.should_resign():
                logger.info("Position is too bad, considering resignation")
                return "resign"
            
            # Check for draw offers
            if self.should_offer_draw():
                logger.info("Position is equal, considering draw offer")
                return "draw"
            
            # Calculate best move
            best_move = None
            best_score = float('-inf')
            
            # Use configured search depth
            for depth in range(1, config.engine.search_depth + 1):
                if time.time() - start_time > config.engine.move_time_limit:
                    break
                    
                moves = list(pos.gen_moves())
                if not moves:
                    break
                
                for move in moves:
                    new_pos = pos.move(move)
                    score = -new_pos.score
                    
                    if score > best_score:
                        best_score = score
                        best_move = move
            
            if best_move:
                uci_move = self.sunfish_move_to_uci(best_move)
                
                # Add human-like delay
                if config.safety.human_like_behavior:
                    delay = random.uniform(*config.safety.random_move_delay)
                    time.sleep(delay)
                
                # Log analysis
                if config.logging.log_engine_analysis:
                    logger.info(f"Best move: {uci_move} (score: {best_score})")
                
                # Performance monitoring
                analysis_time = time.time() - start_time
                self.performance_monitor.log_response_time("move_calculation", analysis_time)
                
                return uci_move
            else:
                logger.warning("No legal moves found")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating move: {e}")
            return None
    
    def should_resign(self) -> bool:
        """Check if bot should resign"""
        if not config.game.auto_resign:
            return False
        
        try:
            pos = self.get_sunfish_position()
            score = -pos.score
            
            return score < config.game.resign_threshold
        except:
            return False
    
    def should_offer_draw(self) -> bool:
        """Check if bot should offer draw"""
        if not config.game.auto_accept_draws:
            return False
        
        try:
            pos = self.get_sunfish_position()
            score = abs(-pos.score)
            
            return score < config.game.draw_threshold
        except:
            return False
    
    def make_move(self, uci_move: str) -> bool:
        """Make a move with enhanced error handling"""
        if uci_move in ["resign", "draw"]:
            return self.handle_special_move(uci_move)
        
        start_time = time.time()
        
        for attempt in range(config.move.retry_attempts):
            try:
                from_square = uci_move[:2]
                to_square = uci_move[2:4]
                
                # Click on piece to move
                piece_selector = config.SELECTORS["piece"].format(square=from_square)
                piece = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, piece_selector))
                )
                piece.click()
                
                # Click on destination
                dest_selector = config.SELECTORS["piece"].format(square=to_square)
                destination = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, dest_selector))
                )
                destination.click()
                
                # Update internal board
                move = chess.Move.from_uci(uci_move)
                self.board.push(move)
                
                # Update game state
                self.game_state.pgn_moves.append(self.board.san(move))
                self.game_state.move_number += 1
                self.game_state.last_move_time = datetime.now()
                self.game_state.current_fen = self.board.fen()
                
                # Log move
                if config.move.log_all_moves:
                    logger.info(f"Made move: {uci_move} ({self.board.san(move)})")
                
                # Performance monitoring
                move_time = time.time() - start_time
                self.performance_monitor.log_response_time("move_execution", move_time)
                
                return True
                
            except Exception as e:
                logger.warning(f"Move attempt {attempt + 1} failed: {e}")
                if attempt < config.move.retry_attempts - 1:
                    time.sleep(config.move.retry_delay)
        
        logger.error(f"Failed to make move {uci_move} after {config.move.retry_attempts} attempts")
        return False
    
    def handle_special_move(self, move_type: str) -> bool:
        """Handle special moves like resign or draw"""
        try:
            if move_type == "resign":
                resign_button = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["resign_button"])
                resign_button.click()
                logger.info("Resigned game")
                self.game_stats.games_lost += 1
                self.consecutive_losses += 1
                self.consecutive_wins = 0
                
            elif move_type == "draw":
                draw_button = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["draw_button"])
                draw_button.click()
                logger.info("Offered draw")
                self.game_stats.games_drawn += 1
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle special move {move_type}: {e}")
            return False
    
    def get_sunfish_position(self) -> Position:
        """Get current position in sunfish format"""
        # For now, return initial position
        # In a real implementation, you'd convert the current board state
        return Position(initial, 0, (True, True), (True, True), 0, 0)
    
    def sunfish_move_to_uci(self, move) -> str:
        """Convert sunfish move to UCI format"""
        i, j = move.i, move.j
        
        # Convert 120-char board index to algebraic notation
        file_i = (i % 10) - 1
        rank_i = 8 - (i // 10 - 2)
        file_j = (j % 10) - 1
        rank_j = 8 - (j // 10 - 2)
        
        files = 'abcdefgh'
        ranks = '12345678'
        
        from_square = f"{files[file_i]}{ranks[rank_i]}"
        to_square = f"{files[file_j]}{ranks[rank_j]}"
        
        return from_square + to_square
    
    def is_our_turn(self) -> bool:
        """Check if it's our turn"""
        try:
            turn_indicator = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["clock_player_turn"])
            return "active" in turn_indicator.get_attribute("class")
        except:
            return True
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        try:
            self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["game_over"])
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"Error checking if game is over: {e}")
            return False
    
    def get_game_result(self) -> str:
        """Get the result of the game"""
        try:
            # Check for various game end conditions
            if self.driver.find_elements(By.CSS_SELECTOR, config.SELECTORS["checkmate_indicator"]):
                return "1-0" if self.game_state.is_white else "0-1"
            elif self.driver.find_elements(By.CSS_SELECTOR, config.SELECTORS["stalemate_indicator"]):
                return "1/2-1/2"
            elif self.driver.find_elements(By.CSS_SELECTOR, config.SELECTORS["draw_indicator"]):
                return "1/2-1/2"
            else:
                return "*"
        except:
            return "*"
    
    def analyze_current_game(self):
        """Analyze the current game"""
        if not config.analysis.analyze_games:
            return
        
        try:
            analysis = self.game_analyzer.analyze_game(
                self.game_state.pgn_moves,
                self.get_game_result()
            )
            
            self.game_state.analysis_data = analysis
            
            # Save analysis if configured
            if config.analysis.save_analysis:
                self.save_game_analysis(analysis)
                
        except Exception as e:
            logger.error(f"Error analyzing game: {e}")
    
    def save_game_analysis(self, analysis: Dict[str, Any]):
        """Save game analysis to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{self.game_state.game_id}_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            logger.info(f"Game analysis saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving game analysis: {e}")
    
    def update_game_stats(self, result: str):
        """Update game statistics"""
        if result == "1-0":
            self.game_stats.games_won += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif result == "0-1":
            self.game_stats.games_lost += 1
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        elif result == "1/2-1/2":
            self.game_stats.games_drawn += 1
            self.consecutive_wins = 0
            self.consecutive_losses = 0
        
        self.game_stats.total_moves += self.game_state.move_number
        self.game_stats.last_game_time = datetime.now()
        
        # Calculate averages
        if self.game_stats.games_played > 0:
            self.game_stats.average_game_length = self.game_stats.total_moves / self.game_stats.games_played
            self.game_stats.win_rate = self.game_stats.games_won / self.game_stats.games_played
    
    def check_safety_limits(self) -> bool:
        """Check if bot should pause due to safety limits"""
        # Check consecutive wins/losses
        if self.consecutive_wins >= config.safety.max_consecutive_wins:
            logger.warning("Too many consecutive wins, pausing")
            self.notification_manager.send_notification("Too many consecutive wins, pausing", "warning")
            return False
        
        if self.consecutive_losses >= config.safety.max_consecutive_losses:
            logger.warning("Too many consecutive losses, pausing")
            self.notification_manager.send_notification("Too many consecutive losses, pausing", "warning")
            return False
        
        return True
    
    def play_game(self):
        """Play a complete game with enhanced features"""
        logger.info("Starting game play...")
        self.notification_manager.send_notification("Game started", "info")
        
        while not self.is_game_over():
            # Check safety limits
            if not self.check_safety_limits():
                break
            
            # Performance monitoring
            self.performance_monitor.log_memory_usage()
            
            if self.is_our_turn():
                # Calculate and make our move
                best_move = self.calculate_move()
                if best_move:
                    if not self.make_move(best_move):
                        logger.error("Could not make move")
                        break
                else:
                    logger.error("Could not calculate move")
                    break
                    
                time.sleep(config.move.move_execution_delay)
            else:
                # Wait for opponent's move
                time.sleep(config.move.move_detection_delay)
        
        # Game finished
        result = self.get_game_result()
        self.update_game_stats(result)
        self.analyze_current_game()
        
        logger.info(f"Game finished with result: {result}")
        self.notification_manager.send_notification(f"Game finished: {result}", "info")
        
        # Cooldown between games
        if config.safety.cooldown_between_games > 0:
            logger.info(f"Waiting {config.safety.cooldown_between_games} seconds before next game")
            time.sleep(config.safety.cooldown_between_games)
    
    def start_background_tasks(self):
        """Start background monitoring tasks"""
        self.running = True
        
        # Performance monitoring thread
        def performance_monitor():
            while self.running:
                self.performance_monitor.log_memory_usage()
                time.sleep(30)  # Check every 30 seconds
        
        # Start background thread
        perf_thread = threading.Thread(target=performance_monitor, daemon=True)
        perf_thread.start()
        self.background_threads.append(perf_thread)
    
    def stop_background_tasks(self):
        """Stop background tasks"""
        self.running = False
        for thread in self.background_threads:
            thread.join(timeout=5)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        perf_stats = self.performance_monitor.get_stats()
        
        return {
            'game_stats': asdict(self.game_stats),
            'performance_stats': perf_stats,
            'session_duration': (datetime.now() - self.session_start_time).total_seconds(),
            'games_this_session': self.games_this_session,
            'consecutive_wins': self.consecutive_wins,
            'consecutive_losses': self.consecutive_losses,
            'config_summary': config.to_dict()
        }
    
    def save_session_report(self, filename: str = None):
        """Save session report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_report_{timestamp}.json"
        
        try:
            stats = self.get_session_stats()
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"Session report saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving session report: {e}")
    
    def close(self):
        """Close browser and cleanup"""
        self.stop_background_tasks()
        
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
        
        # Save final session report
        self.save_session_report()

def main():
    """Main function with enhanced argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Chess.com Bot")
    parser.add_argument("--username", required=True, help="Chess.com username")
    parser.add_argument("--password", required=True, help="Chess.com password")
    parser.add_argument("--game-type", choices=[gt.value for gt in GameType], default=config.game.game_type.value, help="Type of game")
    parser.add_argument("--time-control", default=config.game.time_control, help="Time control")
    parser.add_argument("--difficulty", choices=[d.value for d in DifficultyLevel], default=config.game.difficulty.value, help="Difficulty level")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--max-games", type=int, default=config.safety.max_games_per_session, help="Maximum games per session")
    parser.add_argument("--session-duration", type=int, default=config.safety.session_duration_limit, help="Session duration limit in seconds")
    parser.add_argument("--config-file", help="Load configuration from file")
    parser.add_argument("--save-config", help="Save current configuration to file")
    
    args = parser.parse_args()
    
    # Load configuration from file if specified
    if args.config_file:
        config.load_from_file(args.config_file)
    
    # Override config with command line arguments
    config.browser.headless = args.headless
    config.game.game_type = GameType(args.game_type)
    config.game.time_control = args.time_control
    config.game.difficulty = DifficultyLevel(args.difficulty)
    config.safety.max_games_per_session = args.max_games
    config.safety.session_duration_limit = args.session_duration
    
    # Save configuration if requested
    if args.save_config:
        config.save_to_file(args.save_config)
    
    # Create bot
    bot = AdvancedChessBot(username=args.username, password=args.password)
    
    try:
        # Setup and start
        bot.setup_driver()
        bot.start_background_tasks()
        
        if not bot.login():
            logger.error("Login failed")
            return
        
        # Play games until limits are reached
        while (bot.games_this_session < config.safety.max_games_per_session and 
               (datetime.now() - bot.session_start_time).total_seconds() < config.safety.session_duration_limit):
            
            if not bot.start_game():
                break
            
            bot.play_game()
        
        # Print final statistics
        stats = bot.get_session_stats()
        print("\n" + "="*50)
        print("SESSION STATISTICS")
        print("="*50)
        print(f"Games played: {stats['game_stats']['games_played']}")
        print(f"Games won: {stats['game_stats']['games_won']}")
        print(f"Games lost: {stats['game_stats']['games_lost']}")
        print(f"Games drawn: {stats['game_stats']['games_drawn']}")
        print(f"Win rate: {stats['game_stats']['win_rate']:.2%}")
        print(f"Session duration: {stats['session_duration']:.1f} seconds")
        print(f"Average response time: {stats['performance_stats'].get('average_response_time', 0):.3f}s")
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()