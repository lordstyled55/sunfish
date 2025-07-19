# Chess.com Bot with Sunfish Engine

A chess bot that can play games on Chess.com using the Sunfish chess engine and Stagehand for browser automation.

## Features

- 🤖 Automated chess gameplay on Chess.com
- 🧠 Powered by the Sunfish chess engine (2000+ ELO strength)
- 🌐 Browser automation using Stagehand
- ⚡ Support for multiple time controls (bullet, blitz, rapid, classical)
- 📊 Comprehensive logging and error handling
- 🔧 Configurable settings via JSON or environment variables
- 🎮 Simple launcher script for easy use

## Prerequisites

- Python 3.8 or higher
- Chess.com account
- Internet connection

## Installation

1. **Clone or download the Sunfish engine repository** (already included in this workspace)

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your credentials:**
   
   **Option A: Environment Variables (Recommended)**
   ```bash
   export CHESS_COM_USERNAME='your_username'
   export CHESS_COM_PASSWORD='your_password'
   ```
   
   **Option B: Edit config.json**
   ```json
   {
       "chess_com": {
           "username": "your_username",
           "password": "your_password"
       }
   }
   ```

## Quick Start

### 1. Test the Engine (Optional)
Run the simple test to verify everything is working:
```bash
python3 simple_test.py
```

### 2. Run the Bot
Use the launcher script for easy setup:
```bash
python3 run_bot.py
```

Or run the bot directly:
```bash
python3 chess_com_bot_final.py
```

## Configuration

### Time Controls
Available time controls in `config.json`:
- `"1+0"` - Bullet (1 minute)
- `"3+0"` - Blitz (3 minutes)
- `"5+0"` - Blitz (5 minutes)
- `"10+0"` - Rapid (10 minutes)
- `"15+10"` - Classical (15 minutes + 10 second increment)

### Engine Settings
- `engine_time_limit`: Maximum time for engine calculation (seconds)
- `headless`: Run browser in headless mode (true/false)

### Example Configuration
```json
{
    "chess_com": {
        "username": "your_username",
        "password": "your_password"
    },
    "game_settings": {
        "time_control": "10+0",
        "engine_time_limit": 5.0,
        "headless": false
    }
}
```

## Files Overview

- `chess_com_bot_final.py` - Main bot implementation
- `simple_chess_bot.py` - Simple demo without browser automation
- `run_bot.py` - Easy launcher script
- `config.json` - Configuration file
- `requirements.txt` - Python dependencies
- `simple_test.py` - Engine test script

## How It Works

1. **Browser Automation**: Uses Stagehand to control a web browser
2. **Login**: Automatically logs into Chess.com
3. **Game Finding**: Searches for games with specified time control
4. **Board Reading**: Extracts board state from the webpage
5. **Move Calculation**: Uses Sunfish engine to find best moves
6. **Move Execution**: Clicks on squares to make moves

## Engine Strength

The Sunfish engine is rated around 2000+ ELO, making it competitive against most casual players. The engine uses:
- Alpha-beta search algorithm
- Position evaluation heuristics
- Opening book knowledge
- Endgame tablebases

## Safety and Ethics

⚠️ **Important Notes:**
- Using bots on Chess.com may violate their Terms of Service
- This bot is for educational purposes only
- Use responsibly and at your own risk
- Consider playing against the engine locally instead

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Check your username and password
   - Ensure 2FA is disabled or handled properly
   - Try logging in manually first

2. **Browser Issues**
   - Update Stagehand: `pip install --upgrade stagehand`
   - Try headless mode: set `"headless": true` in config
   - Check if browser is blocked by firewall

3. **Engine Not Working**
   - Run `python3 simple_test.py` to test the engine
   - Check if all dependencies are installed
   - Verify Python version (3.8+ required)

4. **Move Recognition Issues**
   - Chess.com may have updated their interface
   - Check the selectors in the bot code
   - Update selectors if needed

### Debug Mode
Enable debug logging by changing the log level in the bot:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Usage

### Custom Time Controls
Add custom time controls by modifying the selectors in the bot code.

### Engine Tuning
Adjust engine strength by modifying:
- Search depth limits
- Time allocation
- Evaluation parameters

### Multiple Games
The bot can play multiple games by restarting after each game.

## Legal Disclaimer

This software is provided for educational purposes only. Users are responsible for complying with Chess.com's Terms of Service and applicable laws. The authors are not responsible for any consequences of using this bot.

## Contributing

Feel free to contribute improvements:
- Bug fixes
- Feature additions
- Documentation updates
- Performance optimizations

## License

This project is open source. Please respect the original Sunfish engine license and contribute back to the community.

---

**Happy Chess Playing! 🎮♟️**