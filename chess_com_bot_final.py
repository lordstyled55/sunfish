#!/usr/bin/env python3
"""
Chess.com Bot using Sunfish Engine and Stagehand
A complete chess bot that can play games on Chess.com using the Sunfish chess engine.
"""

import asyncio
import time
import logging
import json
import os
from typing import Optional, Dict, Any
import chess
import sunfish
from stagehand import Stagehand
from stagehand.actions import click, type_text, wait_for_element, get_text, get_attribute

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chess_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChessComBot:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Chess.com bot.
        
        Args:
            config: Configuration dictionary with bot settings
        """
        self.config = config
        self.username = config.get('username')
        self.password = config.get('password')
        self.time_control = config.get('time_control', '10+0')
        self.engine_time_limit = config.get('engine_time_limit', 5.0)
        self.headless = config.get('headless', False)
        
        # Initialize components
        self.stagehand = None
        self.board = chess.Board()
        self.searcher = sunfish.Searcher()
        self.game_url = None
        self.is_white = None
        self.move_count = 0
        
        # Chess.com selectors (may need updates if site changes)
        self.selectors = {
            'login_username': '[name="username"]',
            'login_password': '[name="password"]',
            'login_button': '[type="submit"]',
            'play_button': '[data-cy="play-button"]',
            'time_control': f'[data-cy="time-control-{self.time_control}"]',
            'find_game': '[data-cy="find-game-button"]',
            'board': '.board',
            'pieces': '.piece',
            'move_input': '.move-input',
            'game_over': '.game-over',
            'resign_button': '.resign-button',
            'draw_button': '.draw-button'
        }
        
    async def start(self):
        """Start the bot and initialize browser."""
        try:
            logger.info("Starting Chess.com bot...")
            
            # Initialize Stagehand
            self.stagehand = Stagehand()
            await self.stagehand.start(headless=self.headless)
            
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    async def login(self) -> bool:
        """Log into Chess.com."""
        try:
            logger.info("Logging into Chess.com...")
            
            # Navigate to login page
            await self.stagehand.goto("https://www.chess.com/login")
            await asyncio.sleep(2)
            
            # Enter credentials
            await wait_for_element(self.stagehand, self.selectors['login_username'])
            await type_text(self.stagehand, self.selectors['login_username'], self.username)
            await type_text(self.stagehand, self.selectors['login_password'], self.password)
            
            # Click login button
            await click(self.stagehand, self.selectors['login_button'])
            await asyncio.sleep(3)
            
            # Check if login was successful
            try:
                await wait_for_element(self.stagehand, '.user-username', timeout=5)
                logger.info("Login successful")
                return True
            except:
                logger.error("Login failed - check credentials")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    async def find_game(self) -> bool:
        """Find and join a game."""
        try:
            logger.info(f"Looking for a {self.time_control} game...")
            
            # Navigate to play page
            await self.stagehand.goto("https://www.chess.com/play/online")
            await asyncio.sleep(2)
            
            # Click play button
            await click(self.stagehand, self.selectors['play_button'])
            await asyncio.sleep(1)
            
            # Select time control
            try:
                await click(self.stagehand, self.selectors['time_control'])
            except:
                logger.warning("Could not find specific time control, using default")
            
            # Find game
            await click(self.stagehand, self.selectors['find_game'])
            
            # Wait for game to start
            await asyncio.sleep(5)
            
            # Store game URL
            self.game_url = self.stagehand.url
            logger.info(f"Game started: {self.game_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error finding game: {e}")
            return False
    
    async def determine_color(self) -> bool:
        """Determine if we're playing white or black."""
        try:
            # Look for white pieces on the board
            white_pieces = await self.stagehand.query_selector_all('.piece.w')
            black_pieces = await self.stagehand.query_selector_all('.piece.b')
            
            if len(white_pieces) > len(black_pieces):
                self.is_white = True
                logger.info("Playing as White")
            else:
                self.is_white = False
                logger.info("Playing as Black")
            
            return True
            
        except Exception as e:
            logger.error(f"Error determining color: {e}")
            return False
    
    async def get_board_state(self) -> str:
        """
        Get the current board state from the webpage.
        Returns FEN string representation.
        """
        try:
            # Initialize empty board array
            board_array = [['' for _ in range(8)] for _ in range(8)]
            
            # Get all pieces on the board
            pieces = await self.stagehand.query_selector_all('.piece')
            
            for piece in pieces:
                # Get piece class to determine type and color
                class_name = await get_attribute(piece, 'class')
                square = await get_attribute(piece, 'data-square')
                
                if class_name and square:
                    piece_type = self.parse_piece_from_class(class_name)
                    if piece_type and square:
                        # Convert square notation to array indices
                        file = ord(square[0]) - ord('a')
                        rank = 8 - int(square[1])
                        
                        if 0 <= file < 8 and 0 <= rank < 8:
                            board_array[rank][file] = piece_type
            
            # Convert to FEN
            fen = self.array_to_fen(board_array)
            return fen
            
        except Exception as e:
            logger.error(f"Error getting board state: {e}")
            return self.board.fen()
    
    def parse_piece_from_class(self, class_name: str) -> Optional[str]:
        """Parse piece type from CSS class."""
        piece_map = {
            'wp': 'P', 'wr': 'R', 'wn': 'N', 'wb': 'B', 'wq': 'Q', 'wk': 'K',
            'bp': 'p', 'br': 'r', 'bn': 'n', 'bb': 'b', 'bq': 'q', 'bk': 'k'
        }
        
        for piece_class, piece_symbol in piece_map.items():
            if piece_class in class_name:
                return piece_symbol
        
        return None
    
    def array_to_fen(self, board_array: list) -> str:
        """Convert board array to FEN string."""
        fen_parts = []
        
        for rank in board_array:
            empty_count = 0
            rank_str = ""
            
            for square in rank:
                if square == '':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        rank_str += str(empty_count)
                        empty_count = 0
                    rank_str += square
            
            if empty_count > 0:
                rank_str += str(empty_count)
            
            fen_parts.append(rank_str)
        
        # Add other FEN components (simplified)
        fen = '/'.join(fen_parts) + ' w KQkq - 0 1'
        return fen
    
    def get_best_move(self, fen: str) -> Optional[str]:
        """
        Get the best move using Sunfish engine.
        
        Args:
            fen: Board position in FEN notation
            
        Returns:
            Best move in UCI format or None
        """
        try:
            # Update board with current position
            self.board = chess.Board(fen)
            
            # Convert to Sunfish position
            pos = sunfish.Position.from_board(self.board)
            
            # Search for best move
            start_time = time.time()
            best_move = None
            
            for depth, gamma, score, move in self.searcher.search([pos]):
                elapsed = time.time() - start_time
                
                if move:
                    best_move = str(move)
                
                # Stop if time limit reached
                if elapsed >= self.engine_time_limit:
                    break
            
            if best_move:
                logger.info(f"Engine suggests: {best_move} (depth: {depth}, score: {score})")
                return best_move
            else:
                logger.warning("No move found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting best move: {e}")
            return None
    
    async def make_move(self, uci_move: str) -> bool:
        """
        Make a move on the chess board.
        
        Args:
            uci_move: Move in UCI format (e.g., "e2e4")
            
        Returns:
            True if move was successful
        """
        try:
            # Convert UCI move to chess notation
            move = chess.Move.from_uci(uci_move)
            from_square = chess.square_name(move.from_square)
            to_square = chess.square_name(move.to_square)
            
            # Handle promotion
            promotion = ""
            if move.promotion:
                promotion_map = {chess.QUEEN: 'q', chess.ROOK: 'r', chess.BISHOP: 'b', chess.KNIGHT: 'n'}
                promotion = promotion_map.get(move.promotion, 'q')
            
            # Click on from square
            from_selector = f'[data-square="{from_square}"]'
            await click(self.stagehand, from_selector)
            await asyncio.sleep(0.1)
            
            # Click on to square
            to_selector = f'[data-square="{to_square}"]'
            await click(self.stagehand, to_selector)
            
            # Handle promotion if needed
            if promotion:
                promotion_selector = f'.promotion-piece.{promotion}'
                await click(self.stagehand, promotion_selector)
            
            self.move_count += 1
            logger.info(f"Made move {self.move_count}: {uci_move}")
            return True
            
        except Exception as e:
            logger.error(f"Error making move {uci_move}: {e}")
            return False
    
    async def wait_for_opponent_move(self, timeout: int = 60) -> bool:
        """
        Wait for opponent to make a move.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            True if opponent moved, False if timeout
        """
        try:
            start_time = time.time()
            initial_fen = await self.get_board_state()
            
            while time.time() - start_time < timeout:
                current_fen = await self.get_board_state()
                
                if current_fen != initial_fen:
                    logger.info("Opponent moved")
                    return True
                
                await asyncio.sleep(0.5)
            
            logger.warning("Timeout waiting for opponent move")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for opponent move: {e}")
            return False
    
    async def is_game_over(self) -> bool:
        """Check if the game is over."""
        try:
            # Check for game over indicators
            game_over_elements = await self.stagehand.query_selector_all(self.selectors['game_over'])
            return len(game_over_elements) > 0
            
        except Exception as e:
            logger.error(f"Error checking game over: {e}")
            return False
    
    async def play_game(self):
        """Play a complete game."""
        try:
            logger.info("Starting game...")
            
            # Determine color
            await self.determine_color()
            
            # Main game loop
            while not await self.is_game_over():
                # Get current board state
                fen = await self.get_board_state()
                
                # Check if it's our turn
                board = chess.Board(fen)
                is_our_turn = (board.turn == chess.WHITE) == self.is_white
                
                if is_our_turn:
                    # Get best move
                    best_move = self.get_best_move(fen)
                    
                    if best_move:
                        # Make the move
                        if await self.make_move(best_move):
                            await asyncio.sleep(1)  # Wait for move to register
                        else:
                            logger.error("Failed to make move")
                            break
                    else:
                        logger.error("No move found")
                        break
                else:
                    # Wait for opponent move
                    if not await self.wait_for_opponent_move():
                        logger.warning("Opponent move timeout")
                        break
            
            logger.info("Game finished")
            
        except Exception as e:
            logger.error(f"Error during game: {e}")
    
    async def close(self):
        """Close the bot and cleanup."""
        try:
            if self.stagehand:
                await self.stagehand.close()
            logger.info("Bot closed")
        except Exception as e:
            logger.error(f"Error closing bot: {e}")

async def main():
    """Main function to run the chess bot."""
    # Configuration
    config = {
        'username': os.getenv('CHESS_COM_USERNAME', 'your_username'),
        'password': os.getenv('CHESS_COM_PASSWORD', 'your_password'),
        'time_control': '10+0',
        'engine_time_limit': 5.0,
        'headless': False
    }
    
    # Check if credentials are set
    if config['username'] == 'your_username' or config['password'] == 'your_password':
        print("⚠️  Please set your Chess.com credentials:")
        print("   export CHESS_COM_USERNAME='your_username'")
        print("   export CHESS_COM_PASSWORD='your_password'")
        print("\nOr edit the config in the script.")
        return
    
    bot = ChessComBot(config)
    
    try:
        # Start bot
        await bot.start()
        
        # Login
        if not await bot.login():
            logger.error("Failed to login")
            return
        
        # Find game
        if not await bot.find_game():
            logger.error("Failed to find game")
            return
        
        # Play game
        await bot.play_game()
        
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())