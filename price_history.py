"""
Historical Price & Volume Database
Stores every price tick for pattern learning and trend analysis
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import time

class PriceHistoryDB:
    def __init__(self, db_path: str = "price_history.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize historical price database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Price ticks - every second
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                price FLOAT NOT NULL,
                volume_1m FLOAT,
                mark_price FLOAT,
                funding_rate FLOAT,
                open_interest FLOAT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON price_ticks(timestamp DESC)
        """)
        
        # Volume metrics - calculated every 5 minutes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volume_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                vol_1m FLOAT,
                vol_5m FLOAT,
                vol_15m FLOAT,
                vol_1h FLOAT,
                vol_4h FLOAT,
                vol_24h FLOAT,
                vol_5m_avg_1h FLOAT,
                vol_spike_detected BOOLEAN,
                trend TEXT
            )
        """)
        
        # Pattern events - pumps, dumps, support/resistance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                pattern_type TEXT NOT NULL,
                price_start FLOAT,
                price_end FLOAT,
                percent_move FLOAT,
                duration_seconds INTEGER,
                volume_spike BOOLEAN,
                description TEXT,
                outcome TEXT
            )
        """)
        
        # Support/Resistance levels
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_resistance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                level_type TEXT NOT NULL,
                price_level FLOAT NOT NULL,
                strength INTEGER,
                tests_count INTEGER,
                last_test DATETIME
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Historical price database initialized")
    
    def log_price_tick(self, price: float, volume_1m: float = None, 
                       mark_price: float = None, funding_rate: float = None,
                       open_interest: float = None):
        """Store a price tick (called every 1 second)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO price_ticks 
                (timestamp, price, volume_1m, mark_price, funding_rate, open_interest)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now(), price, volume_1m, mark_price, funding_rate, open_interest))
            
            conn.commit()
            conn.close()
    
    def calculate_volume_metrics(self):
        """Calculate volume metrics from recent ticks"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            
            # Get volume data for different timeframes
            timeframes = {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '1h': 3600,
                '4h': 14400,
                '24h': 86400
            }
            
            volumes = {}
            for name, seconds in timeframes.items():
                cutoff = now - timedelta(seconds=seconds)
                cursor.execute("""
                    SELECT AVG(volume_1m) 
                    FROM price_ticks 
                    WHERE timestamp > ? AND volume_1m IS NOT NULL
                """, (cutoff,))
                result = cursor.fetchone()
                volumes[name] = result[0] if result[0] else 0
            
            # Calculate 1h average for 5m volume (for spike detection)
            cutoff_1h = now - timedelta(hours=1)
            cursor.execute("""
                SELECT AVG(volume_1m)
                FROM price_ticks
                WHERE timestamp > ?
            """, (cutoff_1h,))
            vol_5m_avg_1h = cursor.fetchone()[0] or 0
            
            # Detect volume spike (current 5m > 2x 1h average)
            vol_spike = volumes['5m'] > (vol_5m_avg_1h * 2) if vol_5m_avg_1h > 0 else False
            
            # Determine trend
            if volumes['5m'] > volumes['1h'] * 1.2:
                trend = "INCREASING"
            elif volumes['5m'] < volumes['1h'] * 0.8:
                trend = "DECREASING"
            else:
                trend = "STABLE"
            
            # Store metrics
            cursor.execute("""
                INSERT INTO volume_metrics
                (timestamp, vol_1m, vol_5m, vol_15m, vol_1h, vol_4h, vol_24h, 
                 vol_5m_avg_1h, vol_spike_detected, trend)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (now, volumes['1m'], volumes['5m'], volumes['15m'], 
                  volumes['1h'], volumes['4h'], volumes['24h'],
                  vol_5m_avg_1h, vol_spike, trend))
            
            conn.commit()
            conn.close()
            
            return {
                'volumes': volumes,
                'vol_spike': vol_spike,
                'trend': trend,
                'spike_multiplier': volumes['5m'] / vol_5m_avg_1h if vol_5m_avg_1h > 0 else 0
            }
    
    def get_volume_trend(self, timeframe: str = '5m') -> Dict:
        """Get current volume trend analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT vol_5m, vol_1h, vol_5m_avg_1h, vol_spike_detected, trend
            FROM volume_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {
                'current_5m': 0,
                'avg_1h': 0,
                'spike_detected': False,
                'trend': 'UNKNOWN',
                'multiplier': 0
            }
        
        return {
            'current_5m': row[0],
            'avg_1h': row[1],
            'avg_5m_1h': row[2],
            'spike_detected': bool(row[3]),
            'trend': row[4],
            'multiplier': row[0] / row[2] if row[2] > 0 else 0
        }
    
    def detect_support_resistance(self, lookback_hours: int = 24) -> Dict:
        """Detect support and resistance levels from price history"""
        conn = sqlite3.connect(self.db_path)
        
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        
        query = """
            SELECT price, timestamp
            FROM price_ticks
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        """
        
        df = pd.read_sql_query(query, conn, params=(cutoff,))
        conn.close()
        
        if df.empty or len(df) < 100:
            return {'support': None, 'resistance': None}
        
        # Find local minima (support) and maxima (resistance)
        prices = df['price'].values
        
        # Use rolling window to find support/resistance
        window = 20
        supports = []
        resistances = []
        
        for i in range(window, len(prices) - window):
            if prices[i] == min(prices[i-window:i+window]):
                supports.append(prices[i])
            if prices[i] == max(prices[i-window:i+window]):
                resistances.append(prices[i])
        
        # Get most common levels (price levels tested multiple times)
        support_level = pd.Series(supports).mode()[0] if supports else None
        resistance_level = pd.Series(resistances).mode()[0] if resistances else None
        
        return {
            'support': support_level,
            'resistance': resistance_level,
            'support_tests': supports.count(support_level) if support_level else 0,
            'resistance_tests': resistances.count(resistance_level) if resistance_level else 0
        }
    
    def detect_dip_opportunity(self) -> Dict:
        """
        Detect dip buying opportunities (price drops that precede pumps)
        Looks for: price drops followed by bounce + volume increase
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last 3 minutes of data
        cutoff = datetime.now() - timedelta(minutes=3)
        cursor.execute("""
            SELECT price, timestamp, volume_1m
            FROM price_ticks
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        """, (cutoff,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 30:
            return {'detected': False, 'type': 'INSUFFICIENT_DATA'}
        
        prices = [r[0] for r in rows]
        
        # Find local minimum in last 1 minute (potential dip)
        recent_30s = prices[-30:]
        min_price = min(recent_30s)
        min_idx = len(prices) - 30 + recent_30s.index(min_price)
        
        # Check if we're bouncing from the dip
        current_price = prices[-1]
        bounce_pct = ((current_price - min_price) / min_price) * 100
        
        # Check if price dropped before the dip
        if min_idx >= 30:
            before_dip = prices[min_idx - 30]
            dip_depth = ((before_dip - min_price) / before_dip) * 100
        else:
            dip_depth = 0
        
        # Dip opportunity: dropped >0.3% and now bouncing >0.2%
        if dip_depth > 0.3 and bounce_pct > 0.2:
            return {
                'detected': True,
                'type': 'DIP_BOUNCE',
                'dip_depth': dip_depth,
                'bounce_pct': bounce_pct,
                'dip_price': min_price,
                'current_price': current_price,
                'signal': 'BUY_DIP'
            }
        
        return {'detected': False, 'type': 'NO_DIP'}
    
    def detect_moon_candle(self) -> Dict:
        """
        Detect big pump (moon candle)
        Returns: Detection if price increased >5% in <5 minutes with volume spike
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last 5 minutes of data
        cutoff = datetime.now() - timedelta(minutes=5)
        cursor.execute("""
            SELECT price, timestamp, volume_1m
            FROM price_ticks
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        """, (cutoff,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 30:  # Need at least 30 seconds of data
            return {'detected': False, 'type': 'INSUFFICIENT_DATA'}
        
        start_price = rows[0][0]
        current_price = rows[-1][0]
        price_change_pct = ((current_price - start_price) / start_price) * 100
        
        # Check volume spike
        volumes = [r[2] for r in rows if r[2]]
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        recent_volume = sum(volumes[-10:]) / 10 if len(volumes) >= 10 else 0
        volume_spike = recent_volume > (avg_volume * 2) if avg_volume > 0 else False
        
        # Moon candle criteria
        is_moon = price_change_pct > 5 and volume_spike
        is_pump = price_change_pct > 3 and price_change_pct <= 5
        is_dump = price_change_pct < -5
        
        if is_moon:
            return {
                'detected': True,
                'type': 'MOON_CANDLE',
                'price_change_pct': price_change_pct,
                'start_price': start_price,
                'current_price': current_price,
                'volume_multiplier': recent_volume / avg_volume if avg_volume > 0 else 0,
                'duration_seconds': len(rows)
            }
        elif is_pump:
            return {
                'detected': True,
                'type': 'PUMP',
                'price_change_pct': price_change_pct,
                'start_price': start_price,
                'current_price': current_price
            }
        elif is_dump:
            return {
                'detected': True,
                'type': 'DUMP',
                'price_change_pct': price_change_pct
            }
        else:
            return {'detected': False, 'type': 'NORMAL', 'price_change_pct': price_change_pct}
    
    def log_pattern_event(self, pattern_type: str, price_start: float, 
                         price_end: float, duration_seconds: int,
                         volume_spike: bool = False, description: str = ""):
        """Log a detected pattern event"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            percent_move = ((price_end - price_start) / price_start) * 100
            
            cursor.execute("""
                INSERT INTO pattern_events
                (timestamp, pattern_type, price_start, price_end, 
                 percent_move, duration_seconds, volume_spike, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now(), pattern_type, price_start, price_end,
                  percent_move, duration_seconds, volume_spike, description))
            
            conn.commit()
            conn.close()
    
    def get_recent_patterns(self, hours: int = 24) -> Dict:
        """Analyze recent pump/dump patterns from historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Get recent pattern events
        cursor.execute("""
            SELECT pattern_type, COUNT(*) as count, AVG(percent_move) as avg_move
            FROM pattern_events
            WHERE timestamp > ?
            GROUP BY pattern_type
        """, (cutoff,))
        
        patterns = {}
        for row in cursor.fetchall():
            patterns[row[0]] = {
                'count': row[1],
                'avg_move': row[2]
            }
        
        # Get recent price volatility
        cursor.execute("""
            SELECT price FROM price_ticks
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 60
        """, (cutoff,))
        
        recent_prices = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        if len(recent_prices) < 10:
            return {'patterns': patterns, 'volatility': 'UNKNOWN', 'trend': 'UNKNOWN'}
        
        # Calculate volatility (standard deviation of recent prices)
        import statistics
        volatility_pct = (statistics.stdev(recent_prices) / statistics.mean(recent_prices)) * 100
        
        # Determine recent trend (last hour)
        price_change = ((recent_prices[0] - recent_prices[-1]) / recent_prices[-1]) * 100
        
        volatility_level = 'HIGH' if volatility_pct > 1 else 'MEDIUM' if volatility_pct > 0.5 else 'LOW'
        trend = 'BULLISH' if price_change > 1 else 'BEARISH' if price_change < -1 else 'SIDEWAYS'
        
        return {
            'patterns': patterns,
            'volatility': volatility_level,
            'volatility_pct': volatility_pct,
            'trend': trend,
            'price_change_1h': price_change,
            'moon_candles_24h': patterns.get('MOON_CANDLE', {}).get('count', 0),
            'pumps_24h': patterns.get('PUMP', {}).get('count', 0),
            'dumps_24h': patterns.get('DUMP', {}).get('count', 0)
        }
    
    def get_learning_summary(self) -> str:
        """Generate summary of learned patterns for AI context"""
        try:
            patterns = self.get_recent_patterns(hours=24)
            volume_trend = self.get_volume_trend()
            support_resistance = self.detect_support_resistance(lookback_hours=24)
            
            summary = []
            
            # Pattern summary
            moon_count = patterns.get('moon_candles_24h', 0)
            pump_count = patterns.get('pumps_24h', 0)
            if moon_count > 0:
                summary.append(f"{moon_count} moon candles detected in 24h - high momentum environment")
            elif pump_count > 0:
                summary.append(f"{pump_count} pumps detected in 24h - moderate volatility")
            
            # Volatility context
            if patterns.get('volatility') == 'HIGH':
                summary.append("High volatility - good for scalping with tight stops")
            elif patterns.get('volatility') == 'LOW':
                summary.append("Low volatility - wait for breakout or range trade")
            
            # Volume context
            if volume_trend.get('spike_detected'):
                summary.append(f"Volume spike: {volume_trend.get('multiplier', 0):.1f}x - increased interest")
            
            # Support/Resistance context
            if support_resistance.get('support'):
                summary.append(f"Support at ${support_resistance['support']:.6f}")
            if support_resistance.get('resistance'):
                summary.append(f"Resistance at ${support_resistance['resistance']:.6f}")
            
            return " • ".join(summary) if summary else "Collecting historical data..."
            
        except Exception:
            return "Building pattern database..."
    
    def cleanup_old_data(self, days_to_keep: int = 7):
        """Remove data older than X days to keep database size manageable"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(days=days_to_keep)
            
            cursor.execute("DELETE FROM price_ticks WHERE timestamp < ?", (cutoff,))
            cursor.execute("DELETE FROM volume_metrics WHERE timestamp < ?", (cutoff,))
            cursor.execute("DELETE FROM pattern_events WHERE timestamp < ?", (cutoff,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted