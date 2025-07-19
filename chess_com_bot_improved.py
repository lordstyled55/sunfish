#!/usr/bin/env python3
"""
Improved Chess.com Bot using Sunfish Engine and Stagehand
A chess bot that can play games on chess.com using the Sunfish chess engine.
"""

import asyncio
import time
import logging
import subprocess
import sys
from typing import Optional, Tuple
import chess
import chess.engine
from stagehand import Stagehand
from stagehand.actions import click, type_text, wait_for_element, get_text, get_attribute
import sunfish

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
    def __init__(self, username: str, password: str, engine_path: str = "sunfish.py"):
        """
        Initialize the Chess.com bot.
        
        Args:
            username: Chess.com username
            password: Chess.com password
            engine_path: Path to the Sunfish engine
        """
        self.username = username
        self.password = password
        self.engine_path = engine_path
        self.stagehand = None
        self.engine_process = None
        self.board = chess.Board()
        self.game_url = None
        self.is_white = None
        
    async def start(self):
        """Start the bot and initialize browser and engine."""
        try:
            # Initialize Stagehand
            self.stagehand = Stagehand()
            await self.stagehand.start()
            
            # Initialize Sunfish engine as UCI process
            self.engine_process = await self.start_uci_engine()
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def start_uci_engine(self):
        """Start the Sunfish engine as a UCI process."""
        try:
            # Start the engine process
            process = await asyncio.create_subprocess_exec(
                sys.executable, self.engine_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize UCI protocol
            await self.send_uci_command(process, "uci")
            await self.send_uci_command(process, "isready")
            
            logger.info("UCI engine started successfully")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start UCI engine: {e}")
            raise
    
    async def send_uci_command(self, process, command: str):
        """Send a command to the UCI engine."""
        try:
            process.stdin.write(f"{command}\n".encode())
            await process.stdin.drain()
        except Exception as e:
            logger.error(f"Error sending UCI command {command}: {e}")
    
    async def get_uci_response(self, process, timeout: float = 5.0) -> str:
        """Get response from the UCI engine."""
        try:
            response = await asyncio.wait_for(process.stdout.readline(), timeout)
            return response.decode().strip()
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for UCI response")
            return ""
        except Exception as e:
            logger.error(f"Error getting UCI response: {e}")
            return ""
    
    async def get_best_move_uci(self, fen: str, time_limit: float = 5.0) -> str:
        """
        Get the best move from Sunfish engine using UCI protocol.
        
        Args:
            fen: Board position in FEN notation
            time_limit: Time limit for engine calculation in seconds
            
        Returns:
            Best move in UCI format (e.g., "e2e4")
        """
        try:
            # Set up the position
            await self.send_uci_command(self.engine_process, f"position fen {fen}")
            
            # Start search with time limit
            movetime_ms = int(time_limit * 1000)
            await self.send_uci_command(self.engine_process, f"go movetime {movetime_ms}")
            
            # Wait for bestmove response
            start_time = time.time()
            while time.time() - start_time < time_limit + 1:
                response = await self.get_uci_response(self.engine_process, 1.0)
                
                if response.startswith("bestmove"):
                    # Extract move from "bestmove e2e4" format
                    move = response.split()[1]
                    if move != "(none)":
                        logger.info(f"Engine suggests: {move}")
                        return move
                    else:
                        logger.warning("Engine returned no move")
                        return None
                
                if not response:
                    break
            
            logger.warning("Timeout waiting for engine response")
            return None
            
        except Exception as e:
            logger.error(f"Error getting best move: {e}")
            return None
    
    async def login(self):
        """Log into Chess.com."""
        try:
            logger.info("Logging into Chess.com...")
            
            # Navigate to chess.com
            await self.stagehand.goto("https://www.chess.com/login")
            
            # Wait for login form and enter credentials
            await wait_for_element(self.stagehand, '[name="username"]')
            await type_text(self.stagehand, '[name="username"]', self.username)
            await type_text(self.stagehand, '[name="password"]', self.password)
            
            # Click login button
            await click(self.stagehand, '[type="submit"]')
            
            # Wait for login to complete
            await asyncio.sleep(3)
            
            # Check if login was successful
            try:
                await wait_for_element(self.stagehand, '.user-username', timeout=5)
                logger.info("Login successful")
                return True
            except:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    async def find_game(self, time_control: str = "10+0"):
        """
        Find and join a game.
        
        Args:
            time_control: Time control (e.g., "10+0", "5+0", "3+0")
        """
        try:
            logger.info(f"Looking for a {time_control} game...")
            
            # Navigate to play page
            await self.stagehand.goto("https://www.chess.com/play/online")
            await asyncio.sleep(2)
            
            # Try different selectors for time control
            time_control_selectors = [
                f'[data-cy="time-control-{time_control}"]',
                f'[data-time-control="{time_control}"]',
                f'.time-control[data-value="{time_control}"]'
            ]
            
            time_control_found = False
            for selector in time_control_selectors:
                try:
                    await wait_for_element(self.stagehand, selector, timeout=2)
                    await click(self.stagehand, selector)
                    time_control_found = True
                    break
                except:
                    continue
            
            if not time_control_found:
                logger.warning(f"Could not find time control {time_control}, using default")
            
            # Click play button
            play_selectors = [
                '[data-cy="play-button"]',
                '.play-button',
                'button:contains("Play")'
            ]
            
            play_found = False
            for selector in play_selectors:
                try:
                    await wait_for_element(self.stagehand, selector, timeout=2)
                    await click(self.stagehand, selector)
                    play_found = True
                    break
                except:
                    continue
            
            if not play_found:
                logger.error("Could not find play button")
                return False
            
            # Wait for game to start
            await asyncio.sleep(5)
            
            # Get current URL (game URL)
            self.game_url = self.stagehand.page.url
            logger.info(f"Game started: {self.game_url}")
            
            # Determine if we're white or black
            await self.determine_color()
            
            return True
            
        except Exception as e:
            logger.error(f"Error finding game: {e}")
            return False
    
    async def determine_color(self):
        """Determine if we're playing as white or black."""
        try:
            # Look for the board orientation indicator
            # If we see white pieces at the bottom, we're white
            white_pieces_bottom = await self.stagehand.page.query_selector('.board.flipped')
            self.is_white = white_pieces_bottom is None
            
            logger.info(f"Playing as {'white' if self.is_white else 'black'}")
            
        except Exception as e:
            logger.error(f"Error determining color: {e}")
            # Default to white if we can't determine
            self.is_white = True
    
    async def get_board_state(self) -> str:
        """Get the current board state in FEN notation."""
        try:
            # Get the board element
            board_element = await wait_for_element(self.stagehand, '.board')
            
            # Extract piece positions
            pieces = await board_element.query_selector_all('.piece')
            board_array = ['.'] * 64
            
            for piece in pieces:
                # Get piece class to determine type and color
                class_name = await get_attribute(piece, 'class')
                square = await get_attribute(piece, 'data-square')
                
                if square and class_name:
                    # Parse piece type from class name
                    piece_type = self.parse_piece_from_class(class_name)
                    if piece_type:
                        board_array[int(square)] = piece_type
            
            # Convert to FEN
            fen = self.array_to_fen(board_array)
            return fen
            
        except Exception as e:
            logger.error(f"Error getting board state: {e}")
            return chess.Board().fen()
    
    def parse_piece_from_class(self, class_name: str) -> Optional[str]:
        """Parse piece type from CSS class name."""
        if 'wp' in class_name: return 'P'
        elif 'wr' in class_name: return 'R'
        elif 'wn' in class_name: return 'N'
        elif 'wb' in class_name: return 'B'
        elif 'wq' in class_name: return 'Q'
        elif 'wk' in class_name: return 'K'
        elif 'bp' in class_name: return 'p'
        elif 'br' in class_name: return 'r'
        elif 'bn' in class_name: return 'n'
        elif 'bb' in class_name: return 'b'
        elif 'bq' in class_name: return 'q'
        elif 'bk' in class_name: return 'k'
        return None
    
    def array_to_fen(self, board_array: list) -> str:
        """Convert board array to FEN notation."""
        fen_parts = []
        
        for rank in range(8):
            rank_str = ""
            empty_count = 0
            
            for file in range(8):
                square = rank * 8 + file
                piece = board_array[square]
                
                if piece == '.':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        rank_str += str(empty_count)
                        empty_count = 0
                    rank_str += piece
            
            if empty_count > 0:
                rank_str += str(empty_count)
            
            fen_parts.append(rank_str)
        
        # Add other FEN components (assuming standard chess rules)
        fen = '/'.join(fen_parts) + ' w KQkq - 0 1'
        return fen
    
    async def make_move(self, uci_move: str):
        """
        Make a move on the chess.com board.
        
        Args:
            uci_move: Move in UCI format (e.g., "e2e4")
        """
        try:
            if not uci_move or len(uci_move) < 4:
                logger.error(f"Invalid move format: {uci_move}")
                return False
            
            from_square = uci_move[:2]
            to_square = uci_move[2:4]
            
            # Click on the from square
            from_selector = f'[data-square="{from_square}"]'
            await wait_for_element(self.stagehand, from_selector)
            await click(self.stagehand, from_selector)
            
            # Click on the to square
            to_selector = f'[data-square="{to_square}"]'
            await wait_for_element(self.stagehand, to_selector)
            await click(self.stagehand, to_selector)
            
            # Handle promotion if needed
            if len(uci_move) > 4:
                promotion_piece = uci_move[4].upper()
                promotion_selector = f'[data-piece="{promotion_piece}"]'
                await click(self.stagehand, promotion_selector)
            
            logger.info(f"Made move: {uci_move}")
            return True
            
        except Exception as e:
            logger.error(f"Error making move {uci_move}: {e}")
            return False
    
    async def wait_for_opponent_move(self, timeout: int = 60) -> bool:
        """
        Wait for opponent to make a move.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if opponent moved, False if timeout
        """
        try:
            start_time = time.time()
            initial_fen = await self.get_board_state()
            
            while time.time() - start_time < timeout:
                current_fen = await self.get_board_state()
                if current_fen != initial_fen:
                    logger.info("Opponent made a move")
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
            # Look for game over indicators
            game_over_elements = await self.stagehand.page.query_selector_all('.game-over, .game-result')
            return len(game_over_elements) > 0
            
        except Exception as e:
            logger.error(f"Error checking game over: {e}")
            return False
    
    async def play_game(self, time_control: str = "10+0"):
        """Play a complete game."""
        try:
            # Find and join a game
            if not await self.find_game(time_control):
                logger.error("Failed to find game")
                return
            
            # Main game loop
            while not await self.is_game_over():
                # Get current board state
                fen = await self.get_board_state()
                self.board = chess.Board(fen)
                
                # Check if it's our turn
                if self.board.turn == self.is_white:
                    # Get best move from engine
                    best_move = await self.get_best_move_uci(fen)
                    
                    if best_move:
                        # Make the move
                        await self.make_move(best_move)
                    else:
                        logger.error("No move available")
                        break
                else:
                    # Wait for opponent move
                    if not await self.wait_for_opponent_move():
                        logger.warning("Opponent didn't move in time")
                        break
                
                await asyncio.sleep(1)
            
            logger.info("Game finished")
            
        except Exception as e:
            logger.error(f"Error during game: {e}")
    
    async def close(self):
        """Close the bot and cleanup resources."""
        try:
            if self.engine_process:
                await self.send_uci_command(self.engine_process, "quit")
                await self.engine_process.wait()
            
            if self.stagehand:
                await self.stagehand.close()
                
            logger.info("Bot closed")
        except Exception as e:
            logger.error(f"Error closing bot: {e}")

async def main():
    """Main function to run the chess bot."""
    # Configuration
    USERNAME = "your_username"  # Replace with your chess.com username
    PASSWORD = "your_password"  # Replace with your chess.com password
    TIME_CONTROL = "10+0"  # Time control for games
    
    bot = ChessComBot(USERNAME, PASSWORD)
    
    try:
        # Start the bot
        await bot.start()
        
        # Login to chess.com
        if not await bot.login():
            logger.error("Failed to login")
            return
        
        # Play a game
        await bot.play_game(TIME_CONTROL)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())