#!/usr/bin/env python3
"""
Autonomous Chess.com Bot using Sunfish Chess Engine
This bot can play chess automatically on chess.com using the sunfish chess engine.
"""

import time
import sys
import os
import logging
from typing import Optional, Tuple, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import chess
import chess.engine

# Import sunfish chess engine
sys.path.append('.')
from sunfish import Position, Searcher, render, parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChessComBot:
    def __init__(self, username: str = None, password: str = None, headless: bool = False):
        """
        Initialize the Chess.com bot
        
        Args:
            username: Chess.com username (optional, can be set later)
            password: Chess.com password (optional, can be set later)
            headless: Run browser in headless mode
        """
        self.username = username
        self.password = password
        self.driver = None
        self.engine = Searcher()
        self.board = chess.Board()
        self.game_url = None
        self.is_white = None
        self.headless = headless
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
        
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def login(self, username: str = None, password: str = None):
        """
        Login to Chess.com
        
        Args:
            username: Chess.com username
            password: Chess.com password
        """
        if username:
            self.username = username
        if password:
            self.password = password
            
        if not self.username or not self.password:
            logger.error("Username and password are required for login")
            return False
            
        try:
            logger.info("Logging into Chess.com...")
            self.driver.get("https://www.chess.com/login")
            
            # Wait for login form and enter credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for successful login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".user-username"))
            )
            
            logger.info("Successfully logged in to Chess.com")
            return True
            
        except TimeoutException:
            logger.error("Login failed - timeout")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def start_new_game(self, time_control: str = "10+0"):
        """
        Start a new game on Chess.com
        
        Args:
            time_control: Time control (e.g., "10+0", "5+0", "3+2")
        """
        try:
            logger.info(f"Starting new game with time control: {time_control}")
            
            # Navigate to play page
            self.driver.get("https://www.chess.com/play/online")
            time.sleep(2)
            
            # Click on "Play Computer" or "Play Online"
            play_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cy='play-online-button']"))
            )
            play_button.click()
            
            # Set time control if available
            try:
                time_control_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-cy='time-control-{time_control}']"))
                )
                time_control_button.click()
            except TimeoutException:
                logger.warning(f"Could not set time control {time_control}, using default")
            
            # Start the game
            start_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cy='start-game-button']"))
            )
            start_button.click()
            
            # Wait for game to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".board"))
            )
            
            self.game_url = self.driver.current_url
            logger.info(f"Game started: {self.game_url}")
            
            # Determine if we're playing white or black
            self._determine_color()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start new game: {e}")
            return False
    
    def _determine_color(self):
        """Determine if we're playing white or black"""
        try:
            # Look for indicators of our color
            board = self.driver.find_element(By.CSS_SELECTOR, ".board")
            
            # Check if we're on the bottom (white) or top (black)
            # This is a simplified approach - in practice, you'd need more sophisticated detection
            if "flipped" in board.get_attribute("class"):
                self.is_white = False
                logger.info("Playing as Black")
            else:
                self.is_white = True
                logger.info("Playing as White")
                
        except Exception as e:
            logger.warning(f"Could not determine color: {e}")
            # Default to white
            self.is_white = True
    
    def get_board_state(self) -> str:
        """
        Get the current board state in FEN notation
        This is a simplified version - in practice, you'd use computer vision
        """
        try:
            # For now, we'll return the current state from our chess.Board
            # In a real implementation, you'd analyze the board visually
            return self.board.fen()
        except Exception as e:
            logger.error(f"Error getting board state: {e}")
            return None
    
    def make_move(self, move_uci: str):
        """
        Make a move on the chess board
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
        """
        try:
            # Convert UCI to chess.com format
            from_square = move_uci[:2]
            to_square = move_uci[2:4]
            
            # Find the piece to move
            piece_selector = f"[data-square='{from_square}']"
            piece = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, piece_selector))
            )
            piece.click()
            
            # Find the destination square
            dest_selector = f"[data-square='{to_square}']"
            destination = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, dest_selector))
            )
            destination.click()
            
            # Update our internal board
            move = chess.Move.from_uci(move_uci)
            self.board.push(move)
            
            logger.info(f"Made move: {move_uci}")
            return True
            
        except Exception as e:
            logger.error(f"Error making move {move_uci}: {e}")
            return False
    
    def get_opponent_move(self) -> Optional[str]:
        """
        Get the opponent's last move
        Returns the move in UCI format
        """
        try:
            # Look for the last move indicator
            last_move = self.driver.find_element(By.CSS_SELECTOR, ".last-move")
            if last_move:
                # Extract move from the last-move element
                # This is simplified - you'd need to parse the actual move
                pass
            
            # For now, we'll return None and assume the board state is updated
            return None
            
        except NoSuchElementException:
            return None
        except Exception as e:
            logger.error(f"Error getting opponent move: {e}")
            return None
    
    def calculate_best_move(self, time_limit: float = 1.0) -> str:
        """
        Calculate the best move using sunfish engine
        
        Args:
            time_limit: Time limit for calculation in seconds
            
        Returns:
            Best move in UCI format
        """
        try:
            # Convert chess.Board to sunfish Position
            sunfish_pos = self._board_to_sunfish_position()
            
            # Get the best move from sunfish
            start_time = time.time()
            best_move = None
            best_score = float('-inf')
            
            # Simple search with time limit
            for depth in range(1, 10):
                if time.time() - start_time > time_limit:
                    break
                    
                # This is a simplified search - sunfish has more sophisticated search methods
                for move in sunfish_pos.gen_moves():
                    new_pos = sunfish_pos.move(move)
                    score = -new_pos.score
                    
                    if score > best_score:
                        best_score = score
                        best_move = move
            
            if best_move:
                # Convert sunfish move to UCI
                uci_move = self._sunfish_move_to_uci(best_move)
                logger.info(f"Best move: {uci_move} (score: {best_score})")
                return uci_move
            else:
                logger.warning("No best move found")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating best move: {e}")
            return None
    
    def _board_to_sunfish_position(self) -> Position:
        """Convert chess.Board to sunfish Position"""
        # This is a simplified conversion
        # In practice, you'd need to properly convert the board representation
        return Position(initial, 0, (True, True), (True, True), 0, 0)
    
    def _sunfish_move_to_uci(self, sunfish_move) -> str:
        """Convert sunfish move to UCI format"""
        # Convert sunfish move coordinates to UCI
        i, j = sunfish_move.i, sunfish_move.j
        
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
        """Check if it's our turn to move"""
        try:
            # Look for indicators that it's our turn
            # This is simplified - you'd need more sophisticated detection
            turn_indicator = self.driver.find_element(By.CSS_SELECTOR, ".clock-player-turn")
            return "active" in turn_indicator.get_attribute("class")
        except:
            # Default to True if we can't determine
            return True
    
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        try:
            # Look for game over indicators
            game_over = self.driver.find_element(By.CSS_SELECTOR, ".game-over")
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"Error checking if game is over: {e}")
            return False
    
    def play_game(self, auto_play: bool = True):
        """
        Play a complete game
        
        Args:
            auto_play: If True, play automatically. If False, wait for user input.
        """
        logger.info("Starting game play...")
        
        while not self.is_game_over():
            if self.is_our_turn():
                # Calculate and make our move
                best_move = self.calculate_best_move(time_limit=2.0)
                if best_move:
                    self.make_move(best_move)
                else:
                    logger.error("Could not calculate best move")
                    break
                    
                time.sleep(1)  # Wait for move to register
            else:
                # Wait for opponent's move
                time.sleep(0.5)
                
                # Update our board state if opponent moved
                opponent_move = self.get_opponent_move()
                if opponent_move:
                    # Update internal board
                    move = chess.Move.from_uci(opponent_move)
                    self.board.push(move)
        
        logger.info("Game finished")
    
    def close(self):
        """Close the browser and cleanup"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def main():
    """Main function to run the chess bot"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Chess.com Bot")
    parser.add_argument("--username", help="Chess.com username")
    parser.add_argument("--password", help="Chess.com password")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--time-control", default="10+0", help="Time control (e.g., 10+0, 5+0)")
    parser.add_argument("--auto-play", action="store_true", help="Play automatically")
    
    args = parser.parse_args()
    
    # Create bot instance
    bot = ChessComBot(
        username=args.username,
        password=args.password,
        headless=args.headless
    )
    
    try:
        # Setup driver
        bot.setup_driver()
        
        # Login if credentials provided
        if args.username and args.password:
            if not bot.login():
                logger.error("Login failed. Exiting.")
                return
        
        # Start new game
        if not bot.start_new_game(time_control=args.time_control):
            logger.error("Failed to start new game. Exiting.")
            return
        
        # Play the game
        bot.play_game(auto_play=args.auto_play)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()