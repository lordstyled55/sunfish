#!/usr/bin/env python3
"""
Analysis Tools for Chess Bot
Provides game analysis, performance metrics, and reporting capabilities
"""

import json
import csv
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class GameAnalyzer:
    """Advanced game analysis tools"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_game_file(self, filename: str) -> Dict[str, Any]:
        """Analyze a game analysis file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            return self.analyze_game_data(data)
        except Exception as e:
            logger.error(f"Error analyzing game file {filename}: {e}")
            return {}
    
    def analyze_game_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze game data"""
        analysis = {
            'game_info': {},
            'move_analysis': [],
            'position_evaluations': [],
            'critical_moments': [],
            'opening_analysis': {},
            'middlegame_analysis': {},
            'endgame_analysis': {},
            'performance_metrics': {}
        }
        
        # Extract game information
        if 'game_analysis' in data:
            moves = data['game_analysis']
            analysis['game_info']['total_moves'] = len(moves)
            analysis['game_info']['final_position'] = data.get('final_position', '')
            
            # Analyze moves
            evaluations = []
            for i, move_data in enumerate(moves):
                move_num = move_data.get('move_number', i + 1)
                move = move_data.get('move', '')
                evaluation = move_data.get('evaluation', 0)
                
                evaluations.append(evaluation)
                
                # Find critical moments (large evaluation swings)
                if i > 0:
                    eval_change = abs(evaluation - evaluations[i-1])
                    if eval_change > 200:  # Significant evaluation change
                        analysis['critical_moments'].append({
                            'move_number': move_num,
                            'move': move,
                            'evaluation_change': eval_change,
                            'evaluation': evaluation
                        })
                
                # Categorize by game phase
                if move_num <= 10:
                    # Opening phase
                    if 'opening_moves' not in analysis['opening_analysis']:
                        analysis['opening_analysis']['opening_moves'] = []
                    analysis['opening_analysis']['opening_moves'].append({
                        'move': move,
                        'evaluation': evaluation
                    })
                elif move_num <= 30:
                    # Middlegame phase
                    if 'middlegame_moves' not in analysis['middlegame_analysis']:
                        analysis['middlegame_analysis']['middlegame_moves'] = []
                    analysis['middlegame_analysis']['middlegame_moves'].append({
                        'move': move,
                        'evaluation': evaluation
                    })
                else:
                    # Endgame phase
                    if 'endgame_moves' not in analysis['endgame_analysis']:
                        analysis['endgame_analysis']['endgame_moves'] = []
                    analysis['endgame_analysis']['endgame_moves'].append({
                        'move': move,
                        'evaluation': evaluation
                    })
            
            # Performance metrics
            if evaluations:
                analysis['performance_metrics'] = {
                    'average_evaluation': np.mean(evaluations),
                    'evaluation_volatility': np.std(evaluations),
                    'best_evaluation': max(evaluations),
                    'worst_evaluation': min(evaluations),
                    'evaluation_trend': self._calculate_trend(evaluations)
                }
        
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 50:
            return "strongly_improving"
        elif slope > 10:
            return "improving"
        elif slope < -50:
            return "strongly_declining"
        elif slope < -10:
            return "declining"
        else:
            return "stable"
    
    def generate_game_report(self, analysis: Dict[str, Any], output_file: str = None):
        """Generate a detailed game report"""
        report = []
        report.append("=" * 60)
        report.append("CHESS GAME ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Game information
        game_info = analysis.get('game_info', {})
        report.append("GAME INFORMATION:")
        report.append(f"  Total moves: {game_info.get('total_moves', 0)}")
        report.append("")
        
        # Performance metrics
        metrics = analysis.get('performance_metrics', {})
        report.append("PERFORMANCE METRICS:")
        report.append(f"  Average evaluation: {metrics.get('average_evaluation', 0):.1f}")
        report.append(f"  Evaluation volatility: {metrics.get('evaluation_volatility', 0):.1f}")
        report.append(f"  Best evaluation: {metrics.get('best_evaluation', 0):.1f}")
        report.append(f"  Worst evaluation: {metrics.get('worst_evaluation', 0):.1f}")
        report.append(f"  Evaluation trend: {metrics.get('evaluation_trend', 'unknown')}")
        report.append("")
        
        # Critical moments
        critical_moments = analysis.get('critical_moments', [])
        if critical_moments:
            report.append("CRITICAL MOMENTS:")
            for moment in critical_moments[:5]:  # Top 5 critical moments
                report.append(f"  Move {moment['move_number']}: {moment['move']} "
                            f"(eval change: {moment['evaluation_change']:.1f})")
            report.append("")
        
        # Phase analysis
        opening = analysis.get('opening_analysis', {})
        if opening.get('opening_moves'):
            report.append("OPENING ANALYSIS:")
            report.append(f"  Moves played: {len(opening['opening_moves'])}")
            opening_evals = [m['evaluation'] for m in opening['opening_moves']]
            if opening_evals:
                report.append(f"  Average evaluation: {np.mean(opening_evals):.1f}")
            report.append("")
        
        middlegame = analysis.get('middlegame_analysis', {})
        if middlegame.get('middlegame_moves'):
            report.append("MIDDLEGAME ANALYSIS:")
            report.append(f"  Moves played: {len(middlegame['middlegame_moves'])}")
            middlegame_evals = [m['evaluation'] for m in middlegame['middlegame_moves']]
            if middlegame_evals:
                report.append(f"  Average evaluation: {np.mean(middlegame_evals):.1f}")
            report.append("")
        
        endgame = analysis.get('endgame_analysis', {})
        if endgame.get('endgame_moves'):
            report.append("ENDGAME ANALYSIS:")
            report.append(f"  Moves played: {len(endgame['endgame_moves'])}")
            endgame_evals = [m['evaluation'] for m in endgame['endgame_moves']]
            if endgame_evals:
                report.append(f"  Average evaluation: {np.mean(endgame_evals):.1f}")
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Game report saved to {output_file}")
        else:
            print(report_text)
        
        return report_text

class PerformanceAnalyzer:
    """Analyze bot performance across multiple sessions"""
    
    def __init__(self):
        self.session_data = []
        
    def load_session_reports(self, directory: str = "."):
        """Load all session reports from directory"""
        pattern = "session_report_*.json"
        for file_path in Path(directory).glob(pattern):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['filename'] = file_path.name
                    data['date'] = datetime.fromisoformat(data.get('session_duration', '0'))
                    self.session_data.append(data)
            except Exception as e:
                logger.error(f"Error loading session report {file_path}: {e}")
        
        # Sort by date
        self.session_data.sort(key=lambda x: x.get('date', datetime.min))
        logger.info(f"Loaded {len(self.session_data)} session reports")
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends across sessions"""
        if not self.session_data:
            return {}
        
        analysis = {
            'total_sessions': len(self.session_data),
            'total_games': 0,
            'total_wins': 0,
            'total_losses': 0,
            'total_draws': 0,
            'win_rates': [],
            'session_durations': [],
            'games_per_session': [],
            'performance_trends': {}
        }
        
        for session in self.session_data:
            game_stats = session.get('game_stats', {})
            
            games_played = game_stats.get('games_played', 0)
            games_won = game_stats.get('games_won', 0)
            games_lost = game_stats.get('games_lost', 0)
            games_drawn = game_stats.get('games_drawn', 0)
            
            analysis['total_games'] += games_played
            analysis['total_wins'] += games_won
            analysis['total_losses'] += games_lost
            analysis['total_draws'] += games_drawn
            
            if games_played > 0:
                win_rate = games_won / games_played
                analysis['win_rates'].append(win_rate)
                analysis['games_per_session'].append(games_played)
            
            session_duration = session.get('session_duration', 0)
            if session_duration > 0:
                analysis['session_durations'].append(session_duration)
        
        # Calculate trends
        if analysis['win_rates']:
            analysis['performance_trends']['win_rate_trend'] = self._calculate_trend(analysis['win_rates'])
            analysis['performance_trends']['average_win_rate'] = np.mean(analysis['win_rates'])
        
        if analysis['session_durations']:
            analysis['performance_trends']['session_duration_trend'] = self._calculate_trend(analysis['session_durations'])
            analysis['performance_trends']['average_session_duration'] = np.mean(analysis['session_durations'])
        
        if analysis['games_per_session']:
            analysis['performance_trends']['games_per_session_trend'] = self._calculate_trend(analysis['games_per_session'])
            analysis['performance_trends']['average_games_per_session'] = np.mean(analysis['games_per_session'])
        
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend of values"""
        if len(values) < 2:
            return "insufficient_data"
        
        slope = np.polyfit(range(len(values)), values, 1)[0]
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def generate_performance_report(self, analysis: Dict[str, Any], output_file: str = None):
        """Generate performance report"""
        report = []
        report.append("=" * 60)
        report.append("BOT PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("OVERALL STATISTICS:")
        report.append(f"  Total sessions: {analysis.get('total_sessions', 0)}")
        report.append(f"  Total games: {analysis.get('total_games', 0)}")
        report.append(f"  Total wins: {analysis.get('total_wins', 0)}")
        report.append(f"  Total losses: {analysis.get('total_losses', 0)}")
        report.append(f"  Total draws: {analysis.get('total_draws', 0)}")
        
        total_games = analysis.get('total_games', 0)
        if total_games > 0:
            overall_win_rate = analysis.get('total_wins', 0) / total_games
            report.append(f"  Overall win rate: {overall_win_rate:.2%}")
        report.append("")
        
        # Performance trends
        trends = analysis.get('performance_trends', {})
        report.append("PERFORMANCE TRENDS:")
        report.append(f"  Win rate trend: {trends.get('win_rate_trend', 'unknown')}")
        report.append(f"  Average win rate: {trends.get('average_win_rate', 0):.2%}")
        report.append(f"  Session duration trend: {trends.get('session_duration_trend', 'unknown')}")
        report.append(f"  Average session duration: {trends.get('average_session_duration', 0):.1f} seconds")
        report.append(f"  Games per session trend: {trends.get('games_per_session_trend', 'unknown')}")
        report.append(f"  Average games per session: {trends.get('average_games_per_session', 0):.1f}")
        report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Performance report saved to {output_file}")
        else:
            print(report_text)
        
        return report_text
    
    def create_performance_charts(self, output_dir: str = "charts"):
        """Create performance visualization charts"""
        if not self.session_data:
            logger.warning("No session data available for charts")
            return
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Prepare data
        dates = [session.get('date', datetime.now()) for session in self.session_data]
        win_rates = []
        games_per_session = []
        session_durations = []
        
        for session in self.session_data:
            game_stats = session.get('game_stats', {})
            games_played = game_stats.get('games_played', 0)
            games_won = game_stats.get('games_won', 0)
            
            if games_played > 0:
                win_rates.append(games_won / games_played)
            else:
                win_rates.append(0)
            
            games_per_session.append(games_played)
            session_durations.append(session.get('session_duration', 0) / 3600)  # Convert to hours
        
        # Create charts
        plt.figure(figsize=(15, 10))
        
        # Win rate over time
        plt.subplot(2, 2, 1)
        plt.plot(dates, win_rates, 'b-o')
        plt.title('Win Rate Over Time')
        plt.ylabel('Win Rate')
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # Games per session
        plt.subplot(2, 2, 2)
        plt.plot(dates, games_per_session, 'g-o')
        plt.title('Games Per Session')
        plt.ylabel('Number of Games')
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # Session duration
        plt.subplot(2, 2, 3)
        plt.plot(dates, session_durations, 'r-o')
        plt.title('Session Duration')
        plt.ylabel('Duration (hours)')
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # Win rate distribution
        plt.subplot(2, 2, 4)
        plt.hist(win_rates, bins=10, alpha=0.7, color='blue')
        plt.title('Win Rate Distribution')
        plt.xlabel('Win Rate')
        plt.ylabel('Frequency')
        plt.grid(True)
        
        plt.tight_layout()
        chart_file = Path(output_dir) / "performance_charts.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Performance charts saved to {chart_file}")

class OpeningAnalyzer:
    """Analyze opening performance"""
    
    def __init__(self):
        self.opening_stats = defaultdict(lambda: {
            'games': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'average_evaluation': 0,
            'moves': []
        })
    
    def analyze_openings(self, game_files: List[str]):
        """Analyze openings from game files"""
        for game_file in game_files:
            try:
                with open(game_file, 'r') as f:
                    data = json.load(f)
                
                self._analyze_game_openings(data)
            except Exception as e:
                logger.error(f"Error analyzing openings in {game_file}: {e}")
    
    def _analyze_game_openings(self, game_data: Dict[str, Any]):
        """Analyze openings in a single game"""
        game_analysis = game_data.get('game_analysis', [])
        if not game_analysis:
            return
        
        # Get opening moves (first 10 moves)
        opening_moves = []
        for i, move_data in enumerate(game_analysis[:10]):
            move = move_data.get('move', '')
            evaluation = move_data.get('evaluation', 0)
            opening_moves.append(move)
        
        # Create opening key (first few moves)
        opening_key = " ".join(opening_moves[:4])  # First 4 moves
        
        # Update statistics
        stats = self.opening_stats[opening_key]
        stats['games'] += 1
        stats['moves'].extend(opening_moves)
        
        # Calculate average evaluation for opening
        evaluations = [m.get('evaluation', 0) for m in game_analysis[:10]]
        if evaluations:
            stats['average_evaluation'] = (stats['average_evaluation'] * (stats['games'] - 1) + np.mean(evaluations)) / stats['games']
    
    def generate_opening_report(self, output_file: str = None):
        """Generate opening analysis report"""
        report = []
        report.append("=" * 60)
        report.append("OPENING ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Sort openings by frequency
        sorted_openings = sorted(
            self.opening_stats.items(),
            key=lambda x: x[1]['games'],
            reverse=True
        )
        
        report.append("MOST PLAYED OPENINGS:")
        for opening, stats in sorted_openings[:10]:
            report.append(f"  {opening}")
            report.append(f"    Games: {stats['games']}")
            report.append(f"    Average evaluation: {stats['average_evaluation']:.1f}")
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Opening report saved to {output_file}")
        else:
            print(report_text)
        
        return report_text

def main():
    """Main function for analysis tools"""
    parser = argparse.ArgumentParser(description="Chess Bot Analysis Tools")
    parser.add_argument("--mode", choices=["game", "performance", "openings"], required=True,
                       help="Analysis mode")
    parser.add_argument("--input", required=True, help="Input file or directory")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--charts", action="store_true", help="Generate charts")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    if args.mode == "game":
        # Analyze single game
        analyzer = GameAnalyzer()
        analysis = analyzer.analyze_game_file(args.input)
        analyzer.generate_game_report(analysis, args.output)
        
    elif args.mode == "performance":
        # Analyze performance across sessions
        analyzer = PerformanceAnalyzer()
        analyzer.load_session_reports(args.input)
        analysis = analyzer.analyze_performance_trends()
        analyzer.generate_performance_report(analysis, args.output)
        
        if args.charts:
            analyzer.create_performance_charts()
    
    elif args.mode == "openings":
        # Analyze openings
        import glob
        game_files = glob.glob(f"{args.input}/analysis_*.json")
        
        analyzer = OpeningAnalyzer()
        analyzer.analyze_openings(game_files)
        analyzer.generate_opening_report(args.output)

if __name__ == "__main__":
    main()