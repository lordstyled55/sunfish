#!/usr/bin/env python3
"""
Simple test script for Sunfish engine and dependencies
"""

import sys
import chess

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import sunfish
        print("✅ Sunfish imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import sunfish: {e}")
        return False
    
    try:
        import chess
        print("✅ Python-chess imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import chess: {e}")
        return False
    
    try:
        from stagehand import Stagehand
        print("✅ Stagehand imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import stagehand: {e}")
        return False
    
    return True

def test_sunfish_basic():
    """Test basic Sunfish functionality."""
    print("\nTesting basic Sunfish functionality...")
    
    try:
        import sunfish
        
        # Create a searcher
        searcher = sunfish.Searcher()
        
        # Get initial position
        pos = sunfish.Position.from_board(chess.Board())
        
        # Search for best move (limited depth)
        print("Searching for best move...")
        for depth, gamma, score, move in searcher.search([pos]):
            print(f"Depth {depth}, Score {score}, Move {move}")
            if depth >= 4:  # Stop at depth 4
                break
        
        print("✅ Basic Sunfish test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic Sunfish test: {e}")
        return False

def test_chess_board():
    """Test chess board functionality."""
    print("\nTesting chess board...")
    
    try:
        board = chess.Board()
        print(f"Initial FEN: {board.fen()}")
        
        # Make a move
        move = chess.Move.from_uci("e2e4")
        board.push(move)
        print(f"After e2e4: {board.fen()}")
        
        print("✅ Chess board test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in chess board test: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Simple Chess Bot Test")
    print("=" * 30)
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ Import test failed. Please install missing packages.")
        return
    
    # Test chess board
    board_ok = test_chess_board()
    
    # Test Sunfish
    sunfish_ok = test_sunfish_basic()
    
    print("\n" + "=" * 30)
    print("📊 Test Results:")
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Chess Board: {'✅ PASS' if board_ok else '❌ FAIL'}")
    print(f"Sunfish: {'✅ PASS' if sunfish_ok else '❌ FAIL'}")
    
    if imports_ok and board_ok and sunfish_ok:
        print("\n🎉 All tests passed! Ready to create chess bot.")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")

if __name__ == "__main__":
    main()