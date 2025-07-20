#!/usr/bin/env python3
"""
Simple Chess.com Bot using Sunfish Chess Engine
A simplified version that focuses on core functionality.
"""

import time
import sys
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import chess

# Import sunfish chess engine
sys.path.append('.')
from sunfish import Position, Searcher, render, parse, initial
from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class SimpleChessBot:
    def __init__(self, username: str = None, password: str = None):
        """Initialize the simple chess bot"""
        self.username = username
        self.password = password
        self.driver = None
        self.searcher = Searcher()
        self.board = chess.Board()
        self.is_white = True
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        
        if config.BROWSER_HEADLESS:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={config.BROWSER_WINDOW_SIZE[0]},{config.BROWSER_WINDOW_SIZE[1]}")
        chrome_options.add_argument(f"--user-agent={config.BROWSER_USER_AGENT}")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def login(self):
        """Login to Chess.com"""
        if not self.username or not self.password:
            logger.error("Username and password are required for login")
            return False
            
        try:
            logger.info("Logging into Chess.com...")
            self.driver.get(config.LOGIN_URL)
            
            # Enter credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["username_field"]))
            )
            password_field = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["password_field"])
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["login_button"])
            login_button.click()
            
            # Wait for successful login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.SELECTORS["user_username"]))
            )
            
            logger.info("Successfully logged in to Chess.com")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def start_game(self, time_control: str = None):
        """Start a new game"""
        if not time_control:
            time_control = config.DEFAULT_TIME_CONTROL
            
        try:
            logger.info(f"Starting new game with time control: {time_control}")
            
            # Navigate to play page
            self.driver.get(config.PLAY_URL)
            time.sleep(2)
            
            # Click play online
            play_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, config.SELECTORS["play_online_button"]))
            )
            play_button.click()
            
            # Set time control if possible
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
            
            logger.info("Game started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start game: {e}")
            return False
    
    def get_sunfish_position(self) -> Position:
        """Get current position in sunfish format"""
        # For now, return initial position
        # In a real implementation, you'd convert the current board state
        return Position(initial, 0, (True, True), (True, True), 0, 0)
    
    def calculate_move(self) -> Optional[str]:
        """Calculate best move using sunfish"""
        try:
            pos = self.get_sunfish_position()
            
            # Use sunfish's search method
            start_time = time.time()
            best_move = None
            
            # Simple iterative deepening
            for depth in range(1, config.SEARCH_DEPTH + 1):
                if time.time() - start_time > config.MOVE_TIME_LIMIT:
                    break
                    
                # Get all legal moves
                moves = list(pos.gen_moves())
                if not moves:
                    break
                
                # Evaluate each move
                best_score = float('-inf')
                for move in moves:
                    new_pos = pos.move(move)
                    score = -new_pos.score
                    
                    if score > best_score:
                        best_score = score
                        best_move = move
            
            if best_move:
                # Convert to UCI format
                uci_move = self.sunfish_move_to_uci(best_move)
                logger.info(f"Best move: {uci_move} (score: {best_score})")
                return uci_move
            else:
                logger.warning("No legal moves found")
                return None
                
        except Exception as e:
            logger.error(f"Error calculating move: {e}")
            return None
    
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
    
    def make_move(self, uci_move: str) -> bool:
        """Make a move on the board"""
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
            
            logger.info(f"Made move: {uci_move}")
            return True
            
        except Exception as e:
            logger.error(f"Error making move {uci_move}: {e}")
            return False
    
    def is_our_turn(self) -> bool:
        """Check if it's our turn"""
        try:
            # Look for turn indicator
            turn_indicator = self.driver.find_element(By.CSS_SELECTOR, config.SELECTORS["clock_player_turn"])
            return "active" in turn_indicator.get_attribute("class")
        except:
            # Default to True if we can't determine
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
    
    def play_game(self):
        """Play a complete game"""
        logger.info("Starting game play...")
        
        while not self.is_game_over():
            if self.is_our_turn():
                # Calculate and make our move
                best_move = self.calculate_move()
                if best_move:
                    self.make_move(best_move)
                else:
                    logger.error("Could not calculate move")
                    break
                    
                time.sleep(1)
            else:
                # Wait for opponent's move
                time.sleep(config.MOVE_DETECTION_DELAY)
        
        logger.info("Game finished")
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Chess.com Bot")
    parser.add_argument("--username", required=True, help="Chess.com username")
    parser.add_argument("--password", required=True, help="Chess.com password")
    parser.add_argument("--time-control", default=config.DEFAULT_TIME_CONTROL, help="Time control")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    # Update config
    if args.headless:
        config.BROWSER_HEADLESS = True
    
    # Create bot
    bot = SimpleChessBot(username=args.username, password=args.password)
    
    try:
        # Setup and start
        bot.setup_driver()
        
        if not bot.login():
            logger.error("Login failed")
            return
        
        if not bot.start_game(time_control=args.time_control):
            logger.error("Failed to start game")
            return
        
        # Play the game
        bot.play_game()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()