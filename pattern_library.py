"""
Pattern Library System
Stores discovered patterns with performance metrics
"""

import sqlite3
from datetime import datetime
import json

class PatternLibrary:
    
    def __init__(self):
        self.create_db()
    
    def create_db(self):
        """Create pattern library database"""
        conn = sqlite3.connect('pattern_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_name TEXT,
                pattern_type TEXT,
                timeframe TEXT,
                conditions TEXT,
                entry_logic TEXT,
                exit_logic TEXT,
                created_date TEXT,
                last_updated TEXT,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_profit_pct REAL DEFAULT 0,
                avg_loss_pct REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                best_market_regime TEXT,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT,
                timestamp TEXT,
                entry_price REAL,
                exit_price REAL,
                profit_pct REAL,
                outcome TEXT,
                market_regime TEXT,
                notes TEXT,
                FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_pattern(self, pattern_id, pattern_name, pattern_type, timeframe, conditions, entry_logic, exit_logic, notes=""):
        """Add new pattern to library"""
        
        conn = sqlite3.connect('pattern_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO patterns 
            (pattern_id, pattern_name, pattern_type, timeframe, conditions, entry_logic, exit_logic, created_date, last_updated, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            pattern_name,
            pattern_type,
            timeframe,
            json.dumps(conditions),
            entry_logic,
            exit_logic,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            notes
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Pattern '{pattern_name}' added to library")
    
    def log_pattern_trade(self, pattern_id, entry_price, exit_price, market_regime="", notes=""):
        """Log a trade result for a pattern"""
        
        profit_pct = ((exit_price - entry_price) / entry_price) * 100
        outcome = 'WIN' if profit_pct > 0 else 'LOSS'
        
        conn = sqlite3.connect('pattern_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pattern_trades 
            (pattern_id, timestamp, entry_price, exit_price, profit_pct, outcome, market_regime, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            datetime.now().isoformat(),
            entry_price,
            exit_price,
            profit_pct,
            outcome,
            market_regime,
            notes
        ))
        
        cursor.execute('''
            SELECT COUNT(*), 
                   SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN outcome = 'LOSS' THEN 1 ELSE 0 END),
                   AVG(CASE WHEN outcome = 'WIN' THEN profit_pct ELSE 0 END),
                   AVG(CASE WHEN outcome = 'LOSS' THEN ABS(profit_pct) ELSE 0 END)
            FROM pattern_trades 
            WHERE pattern_id = ?
        ''', (pattern_id,))
        
        total, wins, losses, avg_profit, avg_loss = cursor.fetchone()
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        if avg_loss and avg_loss > 0:
            profit_factor = (wins * avg_profit) / (losses * avg_loss) if losses > 0 else 999
        else:
            profit_factor = 999 if wins > 0 else 0
        
        cursor.execute('''
            UPDATE patterns 
            SET total_trades = ?,
                winning_trades = ?,
                losing_trades = ?,
                win_rate = ?,
                avg_profit_pct = ?,
                avg_loss_pct = ?,
                profit_factor = ?,
                last_updated = ?
            WHERE pattern_id = ?
        ''', (
            total,
            wins,
            losses,
            win_rate,
            avg_profit or 0,
            avg_loss or 0,
            profit_factor,
            datetime.now().isoformat(),
            pattern_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Trade logged for pattern {pattern_id}: {outcome} ({profit_pct:+.2f}%)")
        print(f"   Pattern stats: {wins}/{total} wins ({win_rate:.0f}%), PF: {profit_factor:.2f}")
    
    def get_pattern(self, pattern_id):
        """Retrieve pattern by ID"""
        conn = sqlite3.connect('pattern_library.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patterns WHERE pattern_id = ?', (pattern_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            pattern = dict(zip(columns, row))
            pattern['conditions'] = json.loads(pattern['conditions'])
            conn.close()
            return pattern
        
        conn.close()
        return None
    
    def get_best_patterns(self, min_trades=5, min_win_rate=70, timeframe=None):
        """Get best performing patterns"""
        
        conn = sqlite3.connect('pattern_library.db')
        cursor = conn.cursor()
        
        query = '''
            SELECT pattern_id, pattern_name, timeframe, total_trades, win_rate, profit_factor, avg_profit_pct
            FROM patterns 
            WHERE total_trades >= ? AND win_rate >= ?
        '''
        
        params = [min_trades, min_win_rate]
        
        if timeframe:
            query += ' AND timeframe = ?'
            params.append(timeframe)
        
        query += ' ORDER BY win_rate DESC, profit_factor DESC'
        
        cursor.execute(query, params)
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'pattern_id': row[0],
                'pattern_name': row[1],
                'timeframe': row[2],
                'total_trades': row[3],
                'win_rate': row[4],
                'profit_factor': row[5],
                'avg_profit_pct': row[6]
            })
        
        conn.close()
        return patterns
    
    def get_all_patterns_summary(self):
        """Get summary of all patterns"""
        
        conn = sqlite3.connect('pattern_library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_id, pattern_name, timeframe, total_trades, win_rate, profit_factor 
            FROM patterns 
            ORDER BY win_rate DESC
        ''')
        
        patterns = cursor.fetchall()
        conn.close()
        
        return patterns
    
    def seed_initial_patterns(self):
        """Seed library with common profitable patterns to start"""
        
        print("\n🌱 Seeding Pattern Library with proven setups...\n")
        
        self.add_pattern(
            pattern_id='FLAG_BREAKOUT_1H',
            pattern_name='Bullish Flag Breakout',
            pattern_type='CONTINUATION',
            timeframe='1h',
            conditions={
                'strong_trend': 'Price above 20 EMA and 50 EMA',
                'flag_formation': 'Tight consolidation after strong move up',
                'volume': 'Volume decreasing during flag, spikes on breakout',
                'breakout': 'Price breaks above flag resistance with volume'
            },
            entry_logic='Enter when price breaks flag high with 1.5x avg volume',
            exit_logic='Target: Flagpole height added to breakout point. Stop: Below flag low',
            notes='One of highest probability continuation patterns. Works best in strong trends.'
        )
        
        self.add_pattern(
            pattern_id='SUPPORT_BOUNCE_15M',
            pattern_name='Support Bounce with Volume',
            pattern_type='REVERSAL',
            timeframe='15m',
            conditions={
                'support_level': 'Price hits known support level',
                'volume_spike': 'Volume 2x average on bounce candle',
                'rejection_wick': 'Long lower wick showing rejection of lower prices',
                'confirmation': 'Next candle closes above support'
            },
            entry_logic='Enter on close above support with volume confirmation',
            exit_logic='Target: 2-3% gain. Stop: Below support level',
            notes='Quick scalp pattern. Best in ranging markets or pullbacks in uptrends.'
        )
        
        self.add_pattern(
            pattern_id='PULLBACK_TO_EMA_1H',
            pattern_name='Pullback to 20 EMA in Uptrend',
            pattern_type='CONTINUATION',
            timeframe='1h',
            conditions={
                'uptrend': 'Price in clear uptrend, making higher highs',
                'pullback': 'Price pulls back to 20 EMA',
                'rsi': 'RSI bounces from 40-50 range (not oversold)',
                'volume': 'Volume low on pullback, increases on bounce'
            },
            entry_logic='Enter when price bounces off 20 EMA with bullish candle',
            exit_logic='Target: Previous high or higher. Stop: Below 50 EMA',
            notes='Bread and butter trend-following setup. High win rate in strong trends.'
        )
        
        self.add_pattern(
            pattern_id='VOLUME_SPIKE_BREAKOUT_5M',
            pattern_name='Volume Spike Breakout',
            pattern_type='BREAKOUT',
            timeframe='5m',
            conditions={
                'consolidation': 'Price consolidating in tight range',
                'volume_explosion': 'Volume spikes 3x+ average',
                'price_move': 'Price breaks consolidation with strong candle',
                'momentum': 'RSI breaks above 60'
            },
            entry_logic='Enter on breakout candle close with massive volume',
            exit_logic='Target: 1-2% quick scalp. Stop: Below breakout candle low',
            notes='Fast scalp pattern. Exit quickly. Best during high volatility periods.'
        )
        
        self.add_pattern(
            pattern_id='DOUBLE_BOTTOM_4H',
            pattern_name='Double Bottom Reversal',
            pattern_type='REVERSAL',
            timeframe='4h',
            conditions={
                'two_lows': 'Two clear lows at similar price level',
                'higher_low': 'Second low slightly higher or equal to first',
                'volume': 'Volume higher on second bounce',
                'breakout': 'Price breaks neckline resistance'
            },
            entry_logic='Enter on break above neckline with volume',
            exit_logic='Target: Distance from low to neckline, projected upward. Stop: Below second low',
            notes='Classic reversal pattern. Larger timeframe = more reliable. Patient entry required.'
        )
        
        self.add_pattern(
            pattern_id='ASIA_DUMP_US_PUMP',
            pattern_name='Asia Dump, US Pump Pattern',
            pattern_type='TIME_BASED',
            timeframe='1h',
            conditions={
                'time': 'During Asia session (00:00-08:00 UTC)',
                'price_action': 'Price dumps 2-4% during Asia hours',
                'oversold': 'RSI hits <35 on 1h',
                'us_session_approach': 'Approaching US trading hours (13:00+ UTC)'
            },
            entry_logic='Enter when US session starts if price stabilizes',
            exit_logic='Target: Recover 50-100% of Asia dump. Stop: If continues dumping',
            notes='Time-based pattern. US traders often buy the Asia dip. Works best when BTC is stable.'
        )
        
        print("✅ 6 proven patterns seeded into library")
        print("   AI will learn from these and discover new patterns over time\n")

if __name__ == '__main__':
    lib = PatternLibrary()
    lib.seed_initial_patterns()
    
    print("\n📚 Pattern Library Initialized")
    
    patterns = lib.get_all_patterns_summary()
    print(f"\n📊 Total Patterns: {len(patterns)}")
    for p in patterns:
        print(f"   • {p[1]} ({p[2]}) - {p[3]} trades, {p[4]:.0f}% win rate")