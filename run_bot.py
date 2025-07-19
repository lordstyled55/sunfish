#!/usr/bin/env python3
"""
Chess Bot Launcher
Simple script to run the Chess.com bot with configuration.
"""

import json
import os
import sys
import asyncio
from chess_com_bot_final import ChessComBot

def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Override with environment variables if set
        if os.getenv('CHESS_COM_USERNAME'):
            config['chess_com']['username'] = os.getenv('CHESS_COM_USERNAME')
        if os.getenv('CHESS_COM_PASSWORD'):
            config['chess_com']['password'] = os.getenv('CHESS_COM_PASSWORD')
        
        return config
    except FileNotFoundError:
        print(f"❌ Configuration file {config_file} not found!")
        print("Please create config.json or set environment variables:")
        print("  export CHESS_COM_USERNAME='your_username'")
        print("  export CHESS_COM_PASSWORD='your_password'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {config_file}: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = ['stagehand', 'chess', 'sunfish']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sunfish':
                import sunfish
            elif package == 'chess':
                import chess
            elif package == 'stagehand':
                from stagehand import Stagehand
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All dependencies are installed")

async def main():
    """Main function to run the chess bot."""
    print("🤖 Chess.com Bot Launcher")
    print("=" * 30)
    
    # Check dependencies
    check_dependencies()
    
    # Load configuration
    config = load_config()
    
    # Check credentials
    username = config['chess_com']['username']
    password = config['chess_com']['password']
    
    if username == 'your_username' or password == 'your_password':
        print("❌ Please set your Chess.com credentials in config.json or environment variables")
        sys.exit(1)
    
    # Create bot configuration
    bot_config = {
        'username': username,
        'password': password,
        'time_control': config['game_settings']['time_control'],
        'engine_time_limit': config['game_settings']['engine_time_limit'],
        'headless': config['game_settings']['headless']
    }
    
    print(f"🎮 Starting bot with time control: {bot_config['time_control']}")
    print(f"⏱️  Engine time limit: {bot_config['engine_time_limit']}s")
    print(f"🌐 Headless mode: {bot_config['headless']}")
    print()
    
    # Create and run bot
    bot = ChessComBot(bot_config)
    
    try:
        # Start bot
        await bot.start()
        
        # Login
        if not await bot.login():
            print("❌ Failed to login. Check your credentials.")
            return
        
        # Find game
        if not await bot.find_game():
            print("❌ Failed to find a game.")
            return
        
        # Play game
        await bot.play_game()
        
    except KeyboardInterrupt:
        print("\n⏹️  Bot interrupted by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())