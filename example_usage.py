#!/usr/bin/env python3
"""
Example usage of the Chess.com Bot
This script demonstrates how to use the bot with proper error handling
"""

import sys
import logging
from simple_chess_bot import SimpleChessBot
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def example_basic_usage():
    """Example of basic bot usage"""
    print("=== Basic Bot Usage Example ===")
    
    # Create bot instance
    bot = SimpleChessBot(username="your_username", password="your_password")
    
    try:
        # Setup browser
        print("Setting up browser...")
        bot.setup_driver()
        
        # Login
        print("Logging in...")
        if bot.login():
            print("✓ Login successful")
        else:
            print("✗ Login failed")
            return
        
        # Start game
        print("Starting game...")
        if bot.start_game(time_control="5+0"):
            print("✓ Game started")
        else:
            print("✗ Failed to start game")
            return
        
        # Play game
        print("Playing game...")
        bot.play_game()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.close()

def example_headless_mode():
    """Example of running in headless mode"""
    print("=== Headless Mode Example ===")
    
    # Update config for headless mode
    config.BROWSER_HEADLESS = True
    
    bot = SimpleChessBot(username="your_username", password="your_password")
    
    try:
        bot.setup_driver()
        if bot.login() and bot.start_game():
            bot.play_game()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.close()

def example_custom_configuration():
    """Example of custom configuration"""
    print("=== Custom Configuration Example ===")
    
    # Custom configuration
    config.MOVE_TIME_LIMIT = 1.0  # Faster moves
    config.SEARCH_DEPTH = 3       # Shorter search
    config.DEFAULT_TIME_CONTROL = "3+0"  # Blitz game
    
    bot = SimpleChessBot(username="your_username", password="your_password")
    
    try:
        bot.setup_driver()
        if bot.login() and bot.start_game():
            bot.play_game()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.close()

def example_error_handling():
    """Example of proper error handling"""
    print("=== Error Handling Example ===")
    
    bot = SimpleChessBot(username="invalid", password="invalid")
    
    try:
        bot.setup_driver()
        
        # Try to login with invalid credentials
        if not bot.login():
            print("Expected login failure with invalid credentials")
            return
        
        print("Unexpected: Login succeeded with invalid credentials")
        
    except Exception as e:
        print(f"Caught expected error: {e}")
    finally:
        bot.close()

def main():
    """Main function with menu"""
    print("Chess.com Bot - Example Usage")
    print("=" * 40)
    print("1. Basic usage")
    print("2. Headless mode")
    print("3. Custom configuration")
    print("4. Error handling example")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect an example (1-5): ").strip()
            
            if choice == "1":
                example_basic_usage()
            elif choice == "2":
                example_headless_mode()
            elif choice == "3":
                example_custom_configuration()
            elif choice == "4":
                example_error_handling()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()