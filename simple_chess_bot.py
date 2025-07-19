#!/usr/bin/env python3
"""
Simple Chess Bot Example using Sunfish Engine
A demonstration of how to use Sunfish engine for chess analysis and move generation.
"""

import asyncio
import time
import logging
from typing import Optional, Tuple
import chess
import sunfish

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleChessBot:
    def __init__(self):
        """Initialize the simple chess bot."""
        self.board = chess.Board()
        self.searcher = sunfish.Searcher()
        self.move_history = []
        
    def get_best_move(self, fen: str = None, time_limit: float = 2.0) -> Optional[str]:
        """
        Get the best move for a given position.
        
        Args:
            fen: Board position in FEN notation (None for current position)
            time_limit: Time limit for engine calculation in seconds
            
        Returns:
            Best move in UCI format (e.g., "e2e4") or None if no move found
        """
        try:
            # Use provided FEN or current board
            if fen:
                board = chess.Board(fen)
            else:
                board = self.board
            
            # Convert to Sunfish position
            pos = sunfish.Position.from_board(board)
            
            # Search for best move
            start_time = time.time()
            best_move = None
            
            for depth, gamma, score, move in self.searcher.search([pos]):
                elapsed = time.time() - start_time
                
                # Log search progress
                logger.info(f"Depth {depth}, Score {score}, Move {move}, Time {elapsed:.2f}s")
                
                # Store the best move found so far
                if move:
                    best_move = str(move)
                
                # Stop if time limit reached
                if elapsed >= time_limit:
                    break
            
            if best_move:
                logger.info(f"Best move found: {best_move}")
                return best_move
            else:
                logger.warning("No move found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting best move: {e}")
            return None
    
    def make_move(self, uci_move: str) -> bool:
        """
        Make a move on the board.
        
        Args:
            uci_move: Move in UCI format (e.g., "e2e4")
            
        Returns:
            True if move was legal, False otherwise
        """
        try:
            move = chess.Move.from_uci(uci_move)
            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(uci_move)
                logger.info(f"Made move: {uci_move}")
                logger.info(f"Board FEN: {self.board.fen()}")
                return True
            else:
                logger.warning(f"Illegal move: {uci_move}")
                return False
                
        except Exception as e:
            logger.error(f"Error making move {uci_move}: {e}")
            return False
    
    def analyze_position(self, fen: str = None, depth: int = 6) -> dict:
        """
        Analyze a position and return evaluation.
        
        Args:
            fen: Board position in FEN notation (None for current position)
            depth: Search depth
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Use provided FEN or current board
            if fen:
                board = chess.Board(fen)
            else:
                board = self.board
            
            # Convert to Sunfish position
            pos = sunfish.Position.from_board(board)
            
            # Search for analysis
            start_time = time.time()
            analysis = {
                'fen': board.fen(),
                'moves': [],
                'final_score': None,
                'search_time': 0
            }
            
            for search_depth, gamma, score, move in self.searcher.search([pos]):
                elapsed = time.time() - start_time
                
                analysis['moves'].append({
                    'depth': search_depth,
                    'score': score,
                    'move': str(move) if move else None,
                    'time': elapsed
                })
                
                analysis['final_score'] = score
                analysis['search_time'] = elapsed
                
                if search_depth >= depth:
                    break
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing position: {e}")
            return {}
    
    def play_game_against_self(self, max_moves: int = 20):
        """
        Play a game against itself for demonstration.
        
        Args:
            max_moves: Maximum number of moves to play
        """
        logger.info("Starting self-play game...")
        logger.info(f"Initial position: {self.board.fen()}")
        
        move_count = 0
        while not self.board.is_game_over() and move_count < max_moves:
            # Get best move
            best_move = self.get_best_move(time_limit=1.0)
            
            if best_move:
                # Make the move
                if self.make_move(best_move):
                    move_count += 1
                    logger.info(f"Move {move_count}: {best_move}")
                    
                    # Check game status
                    if self.board.is_checkmate():
                        logger.info("Checkmate!")
                        break
                    elif self.board.is_stalemate():
                        logger.info("Stalemate!")
                        break
                    elif self.board.is_insufficient_material():
                        logger.info("Insufficient material!")
                        break
                    elif self.board.is_fifty_moves():
                        logger.info("Fifty-move rule!")
                        break
                    elif self.board.is_repetition():
                        logger.info("Repetition!")
                        break
                else:
                    logger.error("Failed to make move")
                    break
            else:
                logger.error("No move found")
                break
        
        logger.info(f"Game ended after {move_count} moves")
        logger.info(f"Final position: {self.board.fen()}")
        logger.info(f"Move history: {' '.join(self.move_history)}")
    
    def analyze_famous_positions(self):
        """Analyze some famous chess positions."""
        positions = {
            "Starting Position": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "Sicilian Defense": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
            "Ruy Lopez": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
            "Queen's Gambit": "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2"
        }
        
        for name, fen in positions.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Analyzing: {name}")
            logger.info(f"Position: {fen}")
            
            analysis = self.analyze_position(fen, depth=4)
            
            if analysis:
                logger.info(f"Final Score: {analysis['final_score']}")
                logger.info(f"Search Time: {analysis['search_time']:.2f}s")
                
                # Show top moves
                if analysis['moves']:
                    best_move = analysis['moves'][-1]
                    logger.info(f"Best Move: {best_move['move']} (Score: {best_move['score']})")

async def main():
    """Main function to demonstrate the chess bot."""
    print("🤖 Simple Chess Bot Demo")
    print("=" * 40)
    
    # Create bot instance
    bot = SimpleChessBot()
    
    # Analyze famous positions
    print("\n📊 Analyzing Famous Positions...")
    bot.analyze_famous_positions()
    
    # Play a short game against itself
    print("\n🎮 Playing a Short Game...")
    bot.play_game_against_self(max_moves=10)
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())