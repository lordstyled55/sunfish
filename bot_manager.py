#!/usr/bin/env python3
"""
Bot Manager for Advanced Chess.com Bot
Manages multiple bot instances, scheduling, and monitoring
"""

import time
import json
import logging
import threading
import subprocess
import signal
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse

from advanced_chess_bot import AdvancedChessBot
from config import config, GameType, DifficultyLevel

logger = logging.getLogger(__name__)

@dataclass
class BotInstance:
    """Represents a bot instance"""
    id: str
    username: str
    password: str
    game_type: GameType
    time_control: str
    difficulty: DifficultyLevel
    max_games: int
    session_duration: int
    status: str = "stopped"  # running, stopped, error
    process: Optional[subprocess.Popen] = None
    start_time: Optional[datetime] = None
    stats: Dict[str, Any] = None

class BotScheduler:
    """Schedule bot sessions"""
    
    def __init__(self):
        self.schedules = []
        self.running = False
        
    def add_schedule(self, schedule: Dict[str, Any]):
        """Add a new schedule"""
        self.schedules.append(schedule)
        logger.info(f"Added schedule: {schedule}")
    
    def remove_schedule(self, schedule_id: str):
        """Remove a schedule"""
        self.schedules = [s for s in self.schedules if s.get('id') != schedule_id]
        logger.info(f"Removed schedule: {schedule_id}")
    
    def get_active_schedules(self) -> List[Dict[str, Any]]:
        """Get currently active schedules"""
        now = datetime.now()
        active = []
        
        for schedule in self.schedules:
            if self._is_schedule_active(schedule, now):
                active.append(schedule)
        
        return active
    
    def _is_schedule_active(self, schedule: Dict[str, Any], now: datetime) -> bool:
        """Check if schedule is active at given time"""
        # Check day of week
        if 'days' in schedule and now.strftime('%A').lower() not in schedule['days']:
            return False
        
        # Check time range
        if 'start_time' in schedule and 'end_time' in schedule:
            start_time = datetime.strptime(schedule['start_time'], '%H:%M').time()
            end_time = datetime.strptime(schedule['end_time'], '%H:%M').time()
            current_time = now.time()
            
            if not (start_time <= current_time <= end_time):
                return False
        
        return True

class BotManager:
    """Manages multiple bot instances"""
    
    def __init__(self):
        self.bots: Dict[str, BotInstance] = {}
        self.scheduler = BotScheduler()
        self.running = False
        self.management_thread = None
        
    def add_bot(self, bot_config: Dict[str, Any]) -> str:
        """Add a new bot instance"""
        bot_id = bot_config.get('id', f"bot_{len(self.bots) + 1}")
        
        bot = BotInstance(
            id=bot_id,
            username=bot_config['username'],
            password=bot_config['password'],
            game_type=GameType(bot_config.get('game_type', 'rapid')),
            time_control=bot_config.get('time_control', '10+0'),
            difficulty=DifficultyLevel(bot_config.get('difficulty', 'intermediate')),
            max_games=bot_config.get('max_games', 10),
            session_duration=bot_config.get('session_duration', 3600),
            stats={}
        )
        
        self.bots[bot_id] = bot
        logger.info(f"Added bot: {bot_id}")
        return bot_id
    
    def remove_bot(self, bot_id: str):
        """Remove a bot instance"""
        if bot_id in self.bots:
            self.stop_bot(bot_id)
            del self.bots[bot_id]
            logger.info(f"Removed bot: {bot_id}")
    
    def start_bot(self, bot_id: str) -> bool:
        """Start a bot instance"""
        if bot_id not in self.bots:
            logger.error(f"Bot {bot_id} not found")
            return False
        
        bot = self.bots[bot_id]
        
        if bot.status == "running":
            logger.warning(f"Bot {bot_id} is already running")
            return False
        
        try:
            # Build command
            cmd = [
                sys.executable, "advanced_chess_bot.py",
                "--username", bot.username,
                "--password", bot.password,
                "--game-type", bot.game_type.value,
                "--time-control", bot.time_control,
                "--difficulty", bot.difficulty.value,
                "--max-games", str(bot.max_games),
                "--session-duration", str(bot.session_duration),
                "--headless"  # Run in headless mode
            ]
            
            # Start process
            bot.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            bot.status = "running"
            bot.start_time = datetime.now()
            
            logger.info(f"Started bot: {bot_id} (PID: {bot.process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bot {bot_id}: {e}")
            bot.status = "error"
            return False
    
    def stop_bot(self, bot_id: str) -> bool:
        """Stop a bot instance"""
        if bot_id not in self.bots:
            logger.error(f"Bot {bot_id} not found")
            return False
        
        bot = self.bots[bot_id]
        
        if bot.status != "running" or not bot.process:
            logger.warning(f"Bot {bot_id} is not running")
            return False
        
        try:
            # Send SIGTERM
            bot.process.terminate()
            
            # Wait for graceful shutdown
            try:
                bot.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                bot.process.kill()
                bot.process.wait()
            
            bot.status = "stopped"
            bot.process = None
            
            logger.info(f"Stopped bot: {bot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop bot {bot_id}: {e}")
            return False
    
    def restart_bot(self, bot_id: str) -> bool:
        """Restart a bot instance"""
        if self.stop_bot(bot_id):
            time.sleep(2)  # Wait a bit before restarting
            return self.start_bot(bot_id)
        return False
    
    def get_bot_status(self, bot_id: str) -> Dict[str, Any]:
        """Get status of a bot instance"""
        if bot_id not in self.bots:
            return {"error": "Bot not found"}
        
        bot = self.bots[bot_id]
        status = {
            "id": bot.id,
            "username": bot.username,
            "status": bot.status,
            "game_type": bot.game_type.value,
            "time_control": bot.time_control,
            "difficulty": bot.difficulty.value,
            "max_games": bot.max_games,
            "session_duration": bot.session_duration,
            "stats": bot.stats or {}
        }
        
        if bot.start_time:
            status["start_time"] = bot.start_time.isoformat()
            status["uptime"] = (datetime.now() - bot.start_time).total_seconds()
        
        if bot.process:
            status["pid"] = bot.process.pid
            status["returncode"] = bot.process.poll()
        
        return status
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all bots"""
        return {
            bot_id: self.get_bot_status(bot_id)
            for bot_id in self.bots
        }
    
    def update_bot_stats(self, bot_id: str, stats: Dict[str, Any]):
        """Update bot statistics"""
        if bot_id in self.bots:
            self.bots[bot_id].stats = stats
    
    def start_management(self):
        """Start the management system"""
        self.running = True
        self.management_thread = threading.Thread(target=self._management_loop, daemon=True)
        self.management_thread.start()
        logger.info("Bot management started")
    
    def stop_management(self):
        """Stop the management system"""
        self.running = False
        
        # Stop all bots
        for bot_id in list(self.bots.keys()):
            self.stop_bot(bot_id)
        
        if self.management_thread:
            self.management_thread.join(timeout=10)
        
        logger.info("Bot management stopped")
    
    def _management_loop(self):
        """Main management loop"""
        while self.running:
            try:
                # Check bot health
                self._check_bot_health()
                
                # Handle scheduling
                self._handle_scheduling()
                
                # Update statistics
                self._update_statistics()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in management loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_bot_health(self):
        """Check health of running bots"""
        for bot_id, bot in self.bots.items():
            if bot.status == "running" and bot.process:
                # Check if process is still running
                returncode = bot.process.poll()
                if returncode is not None:
                    # Process has ended
                    if returncode == 0:
                        logger.info(f"Bot {bot_id} completed successfully")
                        bot.status = "stopped"
                    else:
                        logger.error(f"Bot {bot_id} failed with return code {returncode}")
                        bot.status = "error"
                    
                    bot.process = None
                
                # Check session duration
                if bot.start_time:
                    session_duration = (datetime.now() - bot.start_time).total_seconds()
                    if session_duration > bot.session_duration:
                        logger.info(f"Bot {bot_id} session duration exceeded, stopping")
                        self.stop_bot(bot_id)
    
    def _handle_scheduling(self):
        """Handle bot scheduling"""
        active_schedules = self.scheduler.get_active_schedules()
        
        for schedule in active_schedules:
            bot_id = schedule.get('bot_id')
            if bot_id and bot_id in self.bots:
                bot = self.bots[bot_id]
                if bot.status != "running":
                    logger.info(f"Starting scheduled bot: {bot_id}")
                    self.start_bot(bot_id)
    
    def _update_statistics(self):
        """Update bot statistics"""
        # This would typically read from log files or API endpoints
        # For now, we'll just log that we're updating
        pass

class WebInterface:
    """Simple web interface for bot management"""
    
    def __init__(self, bot_manager: BotManager, port: int = 8080):
        self.bot_manager = bot_manager
        self.port = port
        self.running = False
        
    def start(self):
        """Start the web interface"""
        try:
            from flask import Flask, jsonify, request, render_template_string
            self.app = Flask(__name__)
            
            # Define routes
            @self.app.route('/')
            def index():
                return self._get_index_html()
            
            @self.app.route('/api/bots')
            def get_bots():
                return jsonify(self.bot_manager.get_all_status())
            
            @self.app.route('/api/bots/<bot_id>/start', methods=['POST'])
            def start_bot(bot_id):
                success = self.bot_manager.start_bot(bot_id)
                return jsonify({"success": success})
            
            @self.app.route('/api/bots/<bot_id>/stop', methods=['POST'])
            def stop_bot(bot_id):
                success = self.bot_manager.stop_bot(bot_id)
                return jsonify({"success": success})
            
            @self.app.route('/api/bots/<bot_id>/restart', methods=['POST'])
            def restart_bot(bot_id):
                success = self.bot_manager.restart_bot(bot_id)
                return jsonify({"success": success})
            
            @self.app.route('/api/schedules', methods=['GET', 'POST'])
            def handle_schedules():
                if request.method == 'POST':
                    schedule = request.json
                    self.bot_manager.scheduler.add_schedule(schedule)
                    return jsonify({"success": True})
                else:
                    return jsonify(self.bot_manager.scheduler.schedules)
            
            self.running = True
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
            
        except ImportError:
            logger.error("Flask not installed. Web interface not available.")
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
    
    def _get_index_html(self):
        """Get the main HTML page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chess Bot Manager</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .bot-card { border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .status-running { background-color: #d4edda; }
                .status-stopped { background-color: #f8d7da; }
                .status-error { background-color: #fff3cd; }
                .button { padding: 5px 10px; margin: 2px; border: none; border-radius: 3px; cursor: pointer; }
                .btn-start { background-color: #28a745; color: white; }
                .btn-stop { background-color: #dc3545; color: white; }
                .btn-restart { background-color: #ffc107; color: black; }
            </style>
        </head>
        <body>
            <h1>Chess Bot Manager</h1>
            <div id="bots"></div>
            
            <script>
                function loadBots() {
                    fetch('/api/bots')
                        .then(response => response.json())
                        .then(bots => {
                            const container = document.getElementById('bots');
                            container.innerHTML = '';
                            
                            Object.values(bots).forEach(bot => {
                                const card = document.createElement('div');
                                card.className = `bot-card status-${bot.status}`;
                                card.innerHTML = `
                                    <h3>${bot.id}</h3>
                                    <p><strong>Status:</strong> ${bot.status}</p>
                                    <p><strong>Username:</strong> ${bot.username}</p>
                                    <p><strong>Game Type:</strong> ${bot.game_type}</p>
                                    <p><strong>Time Control:</strong> ${bot.time_control}</p>
                                    <p><strong>Difficulty:</strong> ${bot.difficulty}</p>
                                    ${bot.uptime ? `<p><strong>Uptime:</strong> ${Math.round(bot.uptime)}s</p>` : ''}
                                    <button class="button btn-start" onclick="startBot('${bot.id}')">Start</button>
                                    <button class="button btn-stop" onclick="stopBot('${bot.id}')">Stop</button>
                                    <button class="button btn-restart" onclick="restartBot('${bot.id}')">Restart</button>
                                `;
                                container.appendChild(card);
                            });
                        });
                }
                
                function startBot(botId) {
                    fetch(`/api/bots/${botId}/start`, {method: 'POST'})
                        .then(() => setTimeout(loadBots, 1000));
                }
                
                function stopBot(botId) {
                    fetch(`/api/bots/${botId}/stop`, {method: 'POST'})
                        .then(() => setTimeout(loadBots, 1000));
                }
                
                function restartBot(botId) {
                    fetch(`/api/bots/${botId}/restart`, {method: 'POST'})
                        .then(() => setTimeout(loadBots, 1000));
                }
                
                // Load bots every 5 seconds
                loadBots();
                setInterval(loadBots, 5000);
            </script>
        </body>
        </html>
        """

def load_bot_configs(filename: str) -> List[Dict[str, Any]]:
    """Load bot configurations from file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {filename} not found")
        return []
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        return []

def save_bot_configs(configs: List[Dict[str, Any]], filename: str):
    """Save bot configurations to file"""
    try:
        with open(filename, 'w') as f:
            json.dump(configs, f, indent=2)
        logger.info(f"Bot configs saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving config file: {e}")

def main():
    """Main function for bot manager"""
    parser = argparse.ArgumentParser(description="Chess Bot Manager")
    parser.add_argument("--config", default="bot_configs.json", help="Bot configuration file")
    parser.add_argument("--web-port", type=int, default=8080, help="Web interface port")
    parser.add_argument("--no-web", action="store_true", help="Disable web interface")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Create bot manager
    manager = BotManager()
    
    # Load bot configurations
    configs = load_bot_configs(args.config)
    for config in configs:
        manager.add_bot(config)
    
    # Start management
    manager.start_management()
    
    # Start web interface if enabled
    if not args.no_web:
        web_interface = WebInterface(manager, args.web_port)
        web_thread = threading.Thread(target=web_interface.start, daemon=True)
        web_thread.start()
        logger.info(f"Web interface started on port {args.web_port}")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down bot manager...")
    finally:
        manager.stop_management()

if __name__ == "__main__":
    main()