# 🏆 Advanced Chess.com Bot

A comprehensive, feature-rich autonomous chess bot that plays on Chess.com using the powerful Sunfish chess engine. This bot includes advanced features like game analysis, performance monitoring, multi-bot management, and a web interface.

## ✨ Features

### 🎮 Core Gameplay
- **Autonomous Play**: Fully automated chess gameplay on Chess.com
- **Multiple Game Types**: Support for Rapid, Blitz, Bullet, and Daily games
- **Computer Opponents**: Play against Chess.com's computer with configurable difficulty
- **Online Play**: Play against real opponents automatically
- **Smart Resignation**: Automatically resign when position is too bad
- **Draw Offers**: Intelligent draw offer handling

### 🧠 Advanced Engine Integration
- **Sunfish Chess Engine**: Powerful, lightweight chess engine for move calculation
- **Configurable Search Depth**: Adjustable search depth for different time controls
- **Move Time Limits**: Configurable time limits for move calculation
- **Position Evaluation**: Real-time position evaluation and analysis

### 🛡️ Safety & Fair Play
- **Human-like Behavior**: Random delays and realistic move patterns
- **Session Limits**: Configurable maximum games and session duration
- **Consecutive Win/Loss Limits**: Automatic pausing to avoid detection
- **Suspicious Pattern Avoidance**: Smart behavior to maintain fair play
- **Cooldown Periods**: Automatic breaks between games

### 📊 Analysis & Monitoring
- **Game Analysis**: Detailed analysis of every game played
- **Performance Metrics**: Win rates, average game length, evaluation trends
- **Critical Moment Detection**: Identify key turning points in games
- **Opening Analysis**: Track and analyze opening performance
- **Session Reports**: Comprehensive session statistics and reports

### 🔧 Management & Control
- **Multi-Bot Management**: Run multiple bot instances simultaneously
- **Web Interface**: Beautiful web dashboard for bot monitoring and control
- **Scheduling**: Schedule bot sessions for specific times
- **Real-time Monitoring**: Live status updates and performance tracking
- **Process Management**: Automatic restart and health monitoring

### 📈 Visualization & Reporting
- **Performance Charts**: Visual charts showing win rates and trends
- **Game Reports**: Detailed analysis reports for individual games
- **Opening Reports**: Analysis of opening performance
- **Session Reports**: Comprehensive session summaries
- **Export Capabilities**: Export data in various formats

## 🚀 Quick Start

### 1. Setup
```bash
# Clone the repository
git clone <repository-url>
cd chess-bot

# Run the setup script
python setup.py
```

### 2. Configuration
Edit the `.env` file with your Chess.com credentials:
```bash
CHESS_USERNAME=your_username
CHESS_PASSWORD=your_password
GAME_TYPE=rapid
TIME_CONTROL=10+0
DIFFICULTY=intermediate
```

### 3. Run the Bot
```bash
# Single bot
./run_bot.sh

# Or manually
source venv/bin/activate
python advanced_chess_bot.py --username YOUR_USERNAME --password YOUR_PASSWORD
```

## 📁 Project Structure

```
chess-bot/
├── advanced_chess_bot.py      # Main bot implementation
├── simple_chess_bot.py        # Simplified bot version
├── bot_manager.py             # Multi-bot management system
├── analysis_tools.py          # Game analysis and reporting tools
├── config.py                  # Configuration management
├── setup.py                   # Setup and installation script
├── requirements.txt           # Python dependencies
├── bot_configs.json          # Multi-bot configurations
├── .env                      # Environment variables
├── run_bot.sh               # Bot execution script
├── run_manager.sh           # Manager execution script
├── run_analysis.sh          # Analysis execution script
└── README.md                # This file
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Chess.com credentials
CHESS_USERNAME=your_username
CHESS_PASSWORD=your_password

# Game settings
GAME_TYPE=rapid              # rapid, blitz, bullet, daily, custom
TIME_CONTROL=10+0            # Time control (e.g., 10+0, 3+2, 1+0)
DIFFICULTY=intermediate      # beginner, intermediate, advanced, expert

# Session limits
MAX_GAMES_PER_SESSION=5
SESSION_DURATION_LIMIT=3600

# Browser settings
BROWSER_HEADLESS=false
DISABLE_IMAGES=true
INCOGNITO=true

# Safety settings
HUMAN_LIKE_BEHAVIOR=true
```

### Bot Configuration (bot_configs.json)
```json
[
  {
    "id": "rapid_bot",
    "username": "your_rapid_username",
    "password": "your_rapid_password",
    "game_type": "rapid",
    "time_control": "10+0",
    "difficulty": "intermediate",
    "max_games": 5,
    "session_duration": 1800,
    "description": "Rapid games bot"
  }
]
```

## 🎯 Usage Examples

### Single Bot
```bash
# Basic usage
python advanced_chess_bot.py --username user --password pass

# With custom settings
python advanced_chess_bot.py \
  --username user \
  --password pass \
  --game-type blitz \
  --time-control 3+0 \
  --difficulty advanced \
  --max-games 10 \
  --headless
```

### Bot Manager (Multiple Bots)
```bash
# Start bot manager with web interface
python bot_manager.py --config bot_configs.json --web-port 8080

# Headless mode
python bot_manager.py --config bot_configs.json --no-web
```

### Analysis Tools
```bash
# Analyze single game
python analysis_tools.py --mode game --input analysis_game_123.json --output game_report.txt

# Analyze performance across sessions
python analysis_tools.py --mode performance --input . --output performance_report.txt --charts

# Analyze openings
python analysis_tools.py --mode openings --input . --output opening_report.txt
```

## 🌐 Web Interface

The bot manager includes a web interface accessible at `http://localhost:8080`:

- **Real-time Status**: View all bot instances and their current status
- **Start/Stop Control**: Control individual bots with one click
- **Performance Metrics**: View win rates, games played, and session statistics
- **Live Monitoring**: Real-time updates of bot performance

## 📊 Analysis Features

### Game Analysis
- **Move-by-move evaluation**: Track position evaluation throughout the game
- **Critical moments**: Identify key turning points and blunders
- **Phase analysis**: Separate analysis for opening, middlegame, and endgame
- **Performance metrics**: Average evaluation, volatility, and trends

### Performance Analysis
- **Win rate tracking**: Monitor performance over time
- **Session statistics**: Games per session, duration, and efficiency
- **Trend analysis**: Identify improving or declining performance
- **Visual charts**: Graphical representation of performance data

### Opening Analysis
- **Opening frequency**: Track most played openings
- **Opening performance**: Win rates and evaluation for each opening
- **Opening recommendations**: Identify best performing openings

## 🛡️ Safety Features

### Fair Play
- **Human-like delays**: Random move timing to mimic human behavior
- **Session limits**: Automatic stopping after maximum games or time
- **Consecutive win/loss limits**: Pause after too many wins or losses
- **Pattern avoidance**: Avoid suspicious playing patterns

### Resource Management
- **Memory monitoring**: Track and limit memory usage
- **CPU monitoring**: Monitor CPU usage and performance
- **Process management**: Automatic restart on failures
- **Cleanup**: Proper resource cleanup and logging

## 🔧 Advanced Configuration

### Engine Settings
```python
# In config.py
engine = EngineSettings(
    engine_type=EngineType.SUNFISH,
    search_depth=5,
    move_time_limit=2.0,
    nodes_limit=1000000,
    skill_level=20
)
```

### Browser Settings
```python
browser = BrowserSettings(
    headless=False,
    window_size=(1920, 1080),
    disable_images=True,
    incognito=True,
    disable_extensions=True
)
```

### Safety Settings
```python
safety = SafetySettings(
    max_games_per_session=10,
    session_duration_limit=3600,
    cooldown_between_games=30,
    human_like_behavior=True,
    max_consecutive_wins=5,
    max_consecutive_losses=3
)
```

## 📈 Performance Monitoring

### Real-time Metrics
- **Response times**: Track move calculation and execution times
- **Memory usage**: Monitor memory consumption
- **Error rates**: Track and log errors and failures
- **Success rates**: Monitor successful moves and games

### Logging
- **Comprehensive logging**: Detailed logs for debugging and analysis
- **Performance logs**: Track performance metrics over time
- **Error logging**: Detailed error reporting and analysis
- **Game logs**: Complete game history and analysis

## 🚨 Troubleshooting

### Common Issues

1. **Login Failed**
   - Check credentials in `.env` file
   - Ensure Chess.com account is active
   - Try disabling 2FA temporarily

2. **Browser Issues**
   - Update Chrome to latest version
   - Check Chrome driver compatibility
   - Try running in headless mode

3. **Move Detection Issues**
   - Check CSS selectors in config
   - Ensure stable internet connection
   - Try different time controls

4. **Performance Issues**
   - Reduce search depth
   - Increase move time limits
   - Check system resources

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python advanced_chess_bot.py --username user --password pass
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect Chess.com's terms of service and use responsibly.

## ⚠️ Disclaimer

This bot is for educational and research purposes only. Users are responsible for complying with Chess.com's terms of service. The authors are not responsible for any consequences of using this software.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on GitHub with detailed information

---

**Happy Chess Playing! 🎮♟️**
