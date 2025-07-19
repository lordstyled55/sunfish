#!/usr/bin/env python3
"""
Test script for Sunfish engine UCI interface
"""

import asyncio
import subprocess
import sys
import chess

async def test_sunfish_uci():
    """Test the Sunfish engine UCI interface."""
    print("Testing Sunfish UCI interface...")
    
    try:
        # Start the engine process
        process = await asyncio.create_subprocess_exec(
            sys.executable, "sunfish.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Test UCI initialization
        print("1. Testing UCI initialization...")
        await send_command(process, "uci")
        response = await get_response(process)
        print(f"UCI response: {response}")
        
        # Test isready
        print("2. Testing isready...")
        await send_command(process, "isready")
        response = await get_response(process)
        print(f"isready response: {response}")
        
        # Test position setup
        print("3. Testing position setup...")
        initial_fen = chess.Board().fen()
        await send_command(process, f"position fen {initial_fen}")
        
        # Test go command
        print("4. Testing go command...")
        await send_command(process, "go movetime 1000")
        
        # Wait for bestmove
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 2:
            response = await get_response(process, timeout=0.5)
            if response.startswith("bestmove"):
                print(f"Best move: {response}")
                break
            elif response:
                print(f"Engine info: {response}")
        
        # Test quit
        print("5. Testing quit...")
        await send_command(process, "quit")
        await process.wait()
        
        print("✅ Sunfish UCI test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Sunfish UCI: {e}")
        return False

async def send_command(process, command: str):
    """Send a command to the engine."""
    try:
        process.stdin.write(f"{command}\n".encode())
        await process.stdin.drain()
    except Exception as e:
        print(f"Error sending command {command}: {e}")

async def get_response(process, timeout: float = 1.0) -> str:
    """Get response from the engine."""
    try:
        response = await asyncio.wait_for(process.stdout.readline(), timeout)
        return response.decode().strip()
    except asyncio.TimeoutError:
        return ""
    except Exception as e:
        print(f"Error getting response: {e}")
        return ""

async def test_sunfish_direct():
    """Test Sunfish engine directly without UCI."""
    print("\nTesting Sunfish engine directly...")
    
    try:
        import sunfish
        
        # Create a searcher
        searcher = sunfish.Searcher()
        
        # Get initial position
        pos = sunfish.Position.from_board(chess.Board())
        
        # Search for best move
        print("Searching for best move...")
        start_time = asyncio.get_event_loop().time()
        
        for depth, gamma, score, move in searcher.search([pos]):
            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"Depth {depth}, Score {score}, Move {move}, Time {elapsed:.2f}s")
            
            if elapsed > 2.0:  # Stop after 2 seconds
                break
        
        print("✅ Direct Sunfish test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Sunfish directly: {e}")
        return False

async def main():
    """Main test function."""
    print("🧪 Chess Bot Engine Test Suite")
    print("=" * 40)
    
    # Test UCI interface
    uci_success = await test_sunfish_uci()
    
    # Test direct interface
    direct_success = await test_sunfish_direct()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"UCI Interface: {'✅ PASS' if uci_success else '❌ FAIL'}")
    print(f"Direct Interface: {'✅ PASS' if direct_success else '❌ FAIL'}")
    
    if uci_success and direct_success:
        print("\n🎉 All tests passed! The engine is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the engine setup.")

if __name__ == "__main__":
    asyncio.run(main())