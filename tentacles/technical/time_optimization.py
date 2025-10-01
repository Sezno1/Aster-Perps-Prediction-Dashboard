"""
⏰ TIME-OF-DAY OPTIMIZATION SYSTEM
Analyzes optimal trading times based on market sessions, volatility patterns, and historical performance

FEATURES:
- Global trading session analysis (US, EU, Asia)
- Time-based volatility patterns
- Optimal entry/exit time windows
- Session overlap opportunities
- Historical performance by time
"""

from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import sqlite3
import numpy as np

class TimeOptimization:
    """
    Provides time-based trading intelligence for optimal execution
    """
    
    def __init__(self):
        self.create_time_database()
        self.sessions = self._define_trading_sessions()
        print("⏰ Time Optimization: ONLINE")
        print("🌍 Monitoring global trading sessions and volatility patterns")
    
    def create_time_database(self):
        """Create database for time-based analysis"""
        
        conn = sqlite3.connect('data/time_optimization.db')
        cursor = conn.cursor()
        
        # Time-based performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hour_utc INTEGER,
                day_of_week INTEGER,
                session_name TEXT,
                avg_volatility REAL,
                win_rate REAL,
                avg_profit_pct REAL,
                trade_count INTEGER,
                volume_multiplier REAL,
                last_updated TEXT
            )
        """)
        
        # Session overlaps
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_overlaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                overlap_name TEXT,
                start_hour_utc INTEGER,
                end_hour_utc INTEGER,
                primary_session TEXT,
                secondary_session TEXT,
                volatility_boost REAL,
                opportunity_score REAL
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Initialize with default data
        self._initialize_default_data()
    
    def _define_trading_sessions(self) -> Dict[str, Dict]:
        """Define global trading sessions"""
        
        return {
            'ASIA_MORNING': {
                'start_utc': 0,   # 9 AM Tokyo (UTC+9) = 0 UTC
                'end_utc': 6,     # 3 PM Tokyo
                'timezone': 'Asia/Tokyo',
                'characteristics': 'Initial momentum, news reactions',
                'volatility_factor': 1.2,
                'best_for': 'breakout_trading'
            },
            'EU_MORNING': {
                'start_utc': 7,   # 8 AM London (UTC+1) = 7 UTC  
                'end_utc': 11,    # 12 PM London
                'timezone': 'Europe/London',
                'characteristics': 'High liquidity, trend continuation',
                'volatility_factor': 1.4,
                'best_for': 'trend_following'
            },
            'EU_US_OVERLAP': {
                'start_utc': 12,  # 1 PM London / 8 AM NY
                'end_utc': 16,    # 5 PM London / 12 PM NY
                'timezone': 'US/Eastern',
                'characteristics': 'Highest liquidity, major moves',
                'volatility_factor': 1.8,
                'best_for': 'scalping_and_swings'
            },
            'US_AFTERNOON': {
                'start_utc': 17,  # 1 PM EST
                'end_utc': 21,    # 5 PM EST
                'timezone': 'US/Eastern',
                'characteristics': 'US market close effects',
                'volatility_factor': 1.3,
                'best_for': 'reversal_trading'
            },
            'US_EVENING': {
                'start_utc': 22,  # 6 PM EST
                'end_utc': 23,    # 11 PM EST
                'timezone': 'US/Eastern', 
                'characteristics': 'Lower liquidity, ranging',
                'volatility_factor': 0.8,
                'best_for': 'range_trading'
            }
        }
    
    def _initialize_default_data(self):
        """Initialize with historical time-based performance data"""
        
        conn = sqlite3.connect('data/time_optimization.db')
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM time_performance")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample historical performance by hour (based on crypto market patterns)
        time_data = [
            # Hour, Day, Session, Volatility, Win Rate, Avg Profit, Volume Mult
            (0, 1, 'ASIA_MORNING', 1.2, 0.68, 2.8, 1.1),   # Asia open
            (1, 1, 'ASIA_MORNING', 1.3, 0.72, 3.2, 1.2),   # Asia momentum
            (2, 1, 'ASIA_MORNING', 1.1, 0.65, 2.5, 1.0),   # Asia mid
            (7, 1, 'EU_MORNING', 1.5, 0.75, 3.8, 1.4),     # London open
            (8, 1, 'EU_MORNING', 1.6, 0.78, 4.1, 1.5),     # London momentum
            (9, 1, 'EU_MORNING', 1.4, 0.73, 3.5, 1.3),     # London mid
            (12, 1, 'EU_US_OVERLAP', 1.9, 0.82, 5.2, 1.8), # NYC open overlap
            (13, 1, 'EU_US_OVERLAP', 2.1, 0.85, 5.8, 2.0), # Peak overlap
            (14, 1, 'EU_US_OVERLAP', 1.8, 0.80, 4.9, 1.7), # High activity
            (15, 1, 'EU_US_OVERLAP', 1.7, 0.77, 4.3, 1.6), # Late overlap
            (17, 1, 'US_AFTERNOON', 1.4, 0.71, 3.6, 1.3),  # US afternoon
            (18, 1, 'US_AFTERNOON', 1.3, 0.69, 3.2, 1.2),  # US late
            (22, 1, 'US_EVENING', 0.9, 0.58, 1.8, 0.8),    # Evening quiet
            (23, 1, 'US_EVENING', 0.8, 0.55, 1.5, 0.7)     # Late evening
        ]
        
        for hour, day, session, vol, win_rate, profit, vol_mult in time_data:
            cursor.execute("""
                INSERT INTO time_performance 
                (hour_utc, day_of_week, session_name, avg_volatility, win_rate, 
                 avg_profit_pct, trade_count, volume_multiplier, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (hour, day, session, vol, win_rate, profit, 50, vol_mult, datetime.now().isoformat()))
        
        # Session overlaps
        overlaps = [
            ('EU_US_OVERLAP', 12, 16, 'EU_MORNING', 'US_AFTERNOON', 1.8, 0.85),
            ('ASIA_EU_TRANSITION', 6, 8, 'ASIA_MORNING', 'EU_MORNING', 1.3, 0.70),
            ('US_ASIA_OVERNIGHT', 22, 2, 'US_EVENING', 'ASIA_MORNING', 0.9, 0.45)
        ]
        
        for name, start, end, primary, secondary, vol_boost, opp_score in overlaps:
            cursor.execute("""
                INSERT INTO session_overlaps
                (overlap_name, start_hour_utc, end_hour_utc, primary_session, 
                 secondary_session, volatility_boost, opportunity_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, start, end, primary, secondary, vol_boost, opp_score))
        
        conn.commit()
        conn.close()
        print("✅ Time optimization database initialized with historical patterns")
    
    def get_current_session(self) -> Dict:
        """Get current trading session information"""
        
        utc_now = datetime.now(pytz.UTC)
        current_hour = utc_now.hour
        
        # Find current session
        current_session = None
        for session_name, session_info in self.sessions.items():
            start = session_info['start_utc']
            end = session_info['end_utc']
            
            if start <= end:  # Normal range
                if start <= current_hour < end:
                    current_session = session_name
                    break
            else:  # Crosses midnight
                if current_hour >= start or current_hour < end:
                    current_session = session_name
                    break
        
        if not current_session:
            current_session = 'OFF_HOURS'
        
        return {
            'session': current_session,
            'hour_utc': current_hour,
            'session_info': self.sessions.get(current_session, {}),
            'timezone_local': str(utc_now.astimezone())
        }
    
    def get_time_based_confidence(self) -> Dict:
        """Get confidence modifier based on current time"""
        
        conn = sqlite3.connect('data/time_optimization.db')
        cursor = conn.cursor()
        
        current_session = self.get_current_session()
        current_hour = current_session['hour_utc']
        current_day = datetime.now().weekday()  # 0 = Monday
        
        # Get performance data for current time
        cursor.execute("""
            SELECT avg_volatility, win_rate, avg_profit_pct, volume_multiplier
            FROM time_performance
            WHERE hour_utc = ? AND day_of_week = ?
        """, (current_hour, current_day))
        
        time_data = cursor.fetchone()
        
        if not time_data:
            # Fallback to hour-only data
            cursor.execute("""
                SELECT avg_volatility, win_rate, avg_profit_pct, volume_multiplier
                FROM time_performance
                WHERE hour_utc = ?
                ORDER BY trade_count DESC
                LIMIT 1
            """, (current_hour,))
            time_data = cursor.fetchone()
        
        # Calculate time-based confidence
        time_confidence = 0.0
        opportunity_level = 'NORMAL'
        
        if time_data:
            volatility, win_rate, avg_profit, volume_mult = time_data
            
            # Base confidence from win rate
            if win_rate > 0.8:
                time_confidence += 0.3  # Excellent time
            elif win_rate > 0.7:
                time_confidence += 0.2  # Good time
            elif win_rate > 0.6:
                time_confidence += 0.1  # Decent time
            else:
                time_confidence -= 0.1  # Poor time
            
            # Volatility bonus
            if volatility > 1.5:
                time_confidence += 0.15
                opportunity_level = 'HIGH'
            elif volatility > 1.2:
                time_confidence += 0.1
                opportunity_level = 'GOOD'
            elif volatility < 0.9:
                time_confidence -= 0.1
                opportunity_level = 'LOW'
            
            # Volume bonus
            if volume_mult > 1.5:
                time_confidence += 0.1
            elif volume_mult < 0.8:
                time_confidence -= 0.05
        
        # Check for session overlaps
        cursor.execute("""
            SELECT overlap_name, volatility_boost, opportunity_score
            FROM session_overlaps
            WHERE start_hour_utc <= ? AND end_hour_utc > ?
        """, (current_hour, current_hour))
        
        overlap_data = cursor.fetchone()
        if overlap_data:
            overlap_name, vol_boost, opp_score = overlap_data
            time_confidence += opp_score * 0.2  # Overlap bonus
            opportunity_level = 'OVERLAP_HIGH'
        
        conn.close()
        
        # Weekend adjustment (crypto trades 24/7 but patterns differ)
        if current_day >= 5:  # Saturday/Sunday
            time_confidence *= 0.8  # Slightly lower confidence on weekends
        
        return {
            'time_confidence': max(-0.3, min(0.4, time_confidence)),  # Cap at ±30-40%
            'opportunity_level': opportunity_level,
            'current_session': current_session['session'],
            'session_info': current_session['session_info'],
            'hour_utc': current_hour,
            'weekend': current_day >= 5,
            'performance_data': {
                'volatility': time_data[0] if time_data else 1.0,
                'historical_win_rate': time_data[1] if time_data else 0.6,
                'avg_profit': time_data[2] if time_data else 2.0,
                'volume_multiplier': time_data[3] if time_data else 1.0
            }
        }
    
    def get_optimal_trading_windows(self, hours_ahead: int = 24) -> List[Dict]:
        """Get optimal trading windows for next N hours"""
        
        conn = sqlite3.connect('data/time_optimization.db')
        cursor = conn.cursor()
        
        optimal_windows = []
        current_utc = datetime.now(pytz.UTC)
        
        for hour_offset in range(hours_ahead):
            future_time = current_utc + timedelta(hours=hour_offset)
            hour_utc = future_time.hour
            day_of_week = future_time.weekday()
            
            cursor.execute("""
                SELECT avg_volatility, win_rate, avg_profit_pct
                FROM time_performance
                WHERE hour_utc = ?
                ORDER BY trade_count DESC
                LIMIT 1
            """, (hour_utc,))
            
            data = cursor.fetchone()
            if data and data[1] > 0.7:  # Only good windows
                optimal_windows.append({
                    'time_utc': future_time.isoformat(),
                    'hour_utc': hour_utc,
                    'win_rate': data[1],
                    'expected_profit': data[2],
                    'volatility': data[0],
                    'session': self._get_session_for_hour(hour_utc),
                    'hours_from_now': hour_offset
                })
        
        conn.close()
        
        # Sort by win rate and profit potential
        optimal_windows.sort(key=lambda x: x['win_rate'] * x['expected_profit'], reverse=True)
        return optimal_windows[:10]  # Top 10 windows
    
    def _get_session_for_hour(self, hour_utc: int) -> str:
        """Get session name for a specific UTC hour"""
        
        for session_name, session_info in self.sessions.items():
            start = session_info['start_utc']
            end = session_info['end_utc']
            
            if start <= end:
                if start <= hour_utc < end:
                    return session_name
            else:
                if hour_utc >= start or hour_utc < end:
                    return session_name
        
        return 'OFF_HOURS'

# Global instance
time_optimizer = TimeOptimization()

if __name__ == "__main__":
    print("⏰ Testing Time Optimization...")
    
    # Current session
    session = time_optimizer.get_current_session()
    print(f"Current session: {session['session']}")
    
    # Time confidence
    confidence = time_optimizer.get_time_based_confidence()
    print(f"Time confidence: {confidence['time_confidence']:.2f}")
    print(f"Opportunity level: {confidence['opportunity_level']}")
    
    # Optimal windows
    windows = time_optimizer.get_optimal_trading_windows(12)
    print(f"Optimal windows in next 12h: {len(windows)}")
    if windows:
        best = windows[0]
        print(f"Best window: {best['session']} (Win rate: {best['win_rate']:.1%})")