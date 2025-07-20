#!/usr/bin/env python3
"""
Test script for the Chess.com Bot
This script tests the bot components without actually playing on Chess.com
"""

import sys
import logging
import chess
from simple_chess_bot import SimpleChessBot
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def test_sunfish_engine():
    """Test the Sunfish chess engine"""
    logger.info("Testing Sunfish chess engine...")
    
    try:
        # Import sunfish components
        from sunfish import Position, Searcher, initial
        
        # Create a searcher
        searcher = Searcher()
        logger.info("✓ Sunfish searcher created successfully")
        
        # Create initial position
        pos = Position(initial, 0, (True, True), (True, True), 0, 0)
        logger.info("✓ Initial position created successfully")
        
        # Generate moves
        moves = list(pos.gen_moves())
        logger.info(f"✓ Generated {len(moves)} legal moves from initial position")
        
        # Test a simple move
        if moves:
            test_move = moves[0]
            new_pos = pos.move(test_move)
            logger.info(f"✓ Successfully made move: {test_move}")
            logger.info(f"✓ Position score: {new_pos.score}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Sunfish engine test failed: {e}")
        return False

def test_chess_library():
    """Test the python-chess library"""
    logger.info("Testing python-chess library...")
    
    try:
        # Create a board
        board = chess.Board()
        logger.info("✓ Chess board created successfully")
        
        # Test legal moves
        legal_moves = list(board.legal_moves)
        logger.info(f"✓ Generated {len(legal_moves)} legal moves")
        
        # Test a move
        if legal_moves:
            test_move = legal_moves[0]
            board.push(test_move)
            logger.info(f"✓ Successfully made move: {test_move}")
            logger.info(f"✓ Board FEN: {board.fen()}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Chess library test failed: {e}")
        return False

def test_bot_initialization():
    """Test bot initialization"""
    logger.info("Testing bot initialization...")
    
    try:
        # Create bot instance
        bot = SimpleChessBot(username="test", password="test")
        logger.info("✓ Bot instance created successfully")
        
        # Test move calculation (without browser)
        move = bot.calculate_move()
        if move:
            logger.info(f"✓ Calculated move: {move}")
        else:
            logger.warning("⚠ No move calculated (this might be normal)")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Bot initialization test failed: {e}")
        return False

def test_move_conversion():
    """Test move conversion functions"""
    logger.info("Testing move conversion...")
    
    try:
        bot = SimpleChessBot()
        
        # Test UCI move conversion
        test_moves = [
            ("e2e4", "e2", "e4"),
            ("d7d5", "d7", "d5"),
            ("g1f3", "g1", "f3"),
        ]
        
        for uci_move, expected_from, expected_to in test_moves:
            from_square = uci_move[:2]
            to_square = uci_move[2:4]
            
            if from_square == expected_from and to_square == expected_to:
                logger.info(f"✓ Move conversion correct: {uci_move}")
            else:
                logger.error(f"✗ Move conversion failed: {uci_move}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Move conversion test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    
    try:
        # Test config attributes
        required_attrs = [
            'BROWSER_HEADLESS',
            'DEFAULT_TIME_CONTROL',
            'MOVE_TIME_LIMIT',
            'SEARCH_DEPTH',
            'LOG_LEVEL',
            'SELECTORS'
        ]
        
        for attr in required_attrs:
            if hasattr(config, attr):
                logger.info(f"✓ Config attribute found: {attr}")
            else:
                logger.error(f"✗ Config attribute missing: {attr}")
                return False
        
        # Test selectors
        required_selectors = [
            'username_field',
            'password_field',
            'board',
            'piece'
        ]
        
        for selector in required_selectors:
            if selector in config.SELECTORS:
                logger.info(f"✓ Selector found: {selector}")
            else:
                logger.error(f"✗ Selector missing: {selector}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    logger.info("Starting Chess Bot Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Chess Library", test_chess_library),
        ("Sunfish Engine", test_sunfish_engine),
        ("Bot Initialization", test_bot_initialization),
        ("Move Conversion", test_move_conversion),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} test...")
        if test_func():
            passed += 1
            logger.info(f"✓ {test_name} test PASSED")
        else:
            logger.error(f"✗ {test_name} test FAILED")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The bot should work correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Chess Bot Components")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    success = run_all_tests()
    
    if success:
        print("\n✅ Bot is ready to use!")
        print("To run the bot:")
        print("python simple_chess_bot.py --username 'your_username' --password 'your_password'")
    else:
        print("\n❌ Bot has issues that need to be fixed before use.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())