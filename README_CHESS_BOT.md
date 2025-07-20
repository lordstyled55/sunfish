# Autonomous Chess.com Bot

An autonomous chess bot that plays on Chess.com using the Sunfish chess engine. This bot can automatically log in, start games, and play chess using computer vision and the Sunfish chess engine.

## Features

- **Automatic Login**: Logs into Chess.com with provided credentials
- **Game Management**: Automatically starts new games with configurable time controls
- **Chess Engine Integration**: Uses the Sunfish chess engine for move calculation
- **Browser Automation**: Uses Selenium WebDriver for web interaction
- **Configurable**: Easy to configure via environment variables or config file
- **Logging**: Comprehensive logging for debugging and monitoring

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Chess.com account
- Virtual environment (recommended)

## Installation

1. **Clone or download the project files**
   ```bash
   # Make sure you have the following files in your directory:
   # - simple_chess_bot.py
   # - config.py
   # - sunfish.py
   # - requirements.txt
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Chrome WebDriver**
   The bot will automatically download and manage the Chrome WebDriver using `webdriver-manager`.

## Usage

### Basic Usage

```bash
python simple_chess_bot.py --username "your_username" --password "your_password"
```

### Advanced Usage

```bash
# Run in headless mode (no browser window)
python simple_chess_bot.py --username "your_username" --password "your_password" --headless

# Set custom time control
python simple_chess_bot.py --username "your_username" --password "your_password" --time-control "5+0"

# Run with environment variables
export CHESS_USERNAME="your_username"
export CHESS_PASSWORD="your_password"
python simple_chess_bot.py --username $CHESS_USERNAME --password $CHESS_PASSWORD
```

### Command Line Arguments

- `--username`: Your Chess.com username (required)
- `--password`: Your Chess.com password (required)
- `--time-control`: Time control for the game (default: "10+0")
- `--headless`: Run browser in headless mode (no visible window)

### Environment Variables

You can configure the bot using environment variables:

```bash
export BROWSER_HEADLESS=true          # Run in headless mode
export TIME_CONTROL="5+0"             # Set time control
export MOVE_TIME_LIMIT=2.0            # Move calculation time limit
export SEARCH_DEPTH=5                 # Engine search depth
export LOG_LEVEL=INFO                 # Logging level
```

## Configuration

The bot uses a `config.py` file for configuration. You can modify this file to change default settings:

```python
# Browser settings
BROWSER_HEADLESS = False
BROWSER_WINDOW_SIZE = (1920, 1080)

# Game settings
DEFAULT_TIME_CONTROL = "10+0"
MOVE_TIME_LIMIT = 2.0  # seconds
SEARCH_DEPTH = 5

# Logging settings
LOG_LEVEL = "INFO"
```

## How It Works

1. **Initialization**: The bot sets up a Chrome WebDriver and logs into Chess.com
2. **Game Start**: Navigates to the play page and starts a new game
3. **Game Loop**: 
   - Checks if it's the bot's turn
   - Calculates the best move using Sunfish engine
   - Makes the move on the board
   - Waits for opponent's move
4. **Game End**: Detects when the game is over and stops

## Chess Engine Integration

The bot uses the Sunfish chess engine for move calculation. Sunfish is a simple but strong chess engine written in Python that can play at ratings above 2000 on Lichess.

### Engine Features

- **MTD-bi search algorithm**: Also known as C*
- **Piece Square Tables**: Efficient evaluation function
- **UCI interface**: Standard chess engine protocol
- **Small size**: Only 131 lines of code

## Safety and Ethics

⚠️ **Important**: Using automated bots on Chess.com may violate their Terms of Service. Please:

1. **Check Terms of Service**: Review Chess.com's terms before using this bot
2. **Use Responsibly**: Consider using this for educational purposes only
3. **Fair Play**: Don't use this bot in rated games or tournaments
4. **Account Safety**: Use a separate account for testing

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Check your username and password
   - Ensure your account is not locked
   - Try running without headless mode to see what's happening

2. **Browser Issues**
   - Make sure Chrome is installed
   - Update Chrome to the latest version
   - Check if antivirus is blocking the WebDriver

3. **Move Detection Issues**
   - The bot may have trouble detecting opponent moves
   - Check the CSS selectors in `config.py`
   - Chess.com may have updated their interface

4. **Engine Issues**
   - Ensure `sunfish.py` is in the same directory
   - Check that all dependencies are installed

### Debug Mode

To run with more detailed logging:

```bash
export LOG_LEVEL=DEBUG
python simple_chess_bot.py --username "your_username" --password "your_password"
```

## Limitations

- **Board Recognition**: Currently uses a simplified approach for board state detection
- **Move Detection**: May not always correctly detect opponent moves
- **Time Controls**: Limited support for complex time controls
- **Game Types**: Primarily designed for standard chess games
- **Browser Dependencies**: Requires Chrome and may break if Chess.com updates their interface

## Future Improvements

- **Computer Vision**: Integrate the chessboard recognizer for better board state detection
- **Move Validation**: Better detection and validation of opponent moves
- **Multiple Engines**: Support for other chess engines (Stockfish, etc.)
- **Game Analysis**: Post-game analysis and statistics
- **GUI**: Web interface for bot control and monitoring

## Contributing

Feel free to contribute to this project by:

1. Reporting bugs
2. Suggesting new features
3. Improving the code
4. Adding better documentation

## License

This project is for educational purposes. Please respect Chess.com's Terms of Service and use responsibly.

## Acknowledgments

- **Sunfish Engine**: Created by Thomas Ahle (https://github.com/thomasahle/sunfish)
- **Chessboard Recognizer**: Created by linrock (https://github.com/linrock/chessboard-recognizer)
- **Selenium**: Web automation framework
- **Python-Chess**: Chess library for Python

## Disclaimer

This bot is provided for educational purposes only. Using automated bots on Chess.com may violate their Terms of Service. Use at your own risk and responsibility.