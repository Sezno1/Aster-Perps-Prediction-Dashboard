"""
Organic Pattern Learning Engine
Discovers patterns across ALL timeframes (1m-1d) using historical data
Learns what works, tweaks patterns naturally, and validates with backtesting
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import itertools
from collections import defaultdict

@dataclass
class PatternCondition:
    """Individual pattern condition (price action, volume, indicators)"""
    timeframe: str
    indicator: str
    comparison: str  # '>', '<', '>=', '<=', '==', 'crossover', 'crossunder'
    value: float
    lookback: int = 1
    weight: float = 1.0

@dataclass
class MultiTFPattern:
    """Multi-timeframe pattern definition"""
    pattern_id: str
    name: str
    conditions: List[PatternCondition]
    entry_rules: Dict
    exit_rules: Dict
    timeframes_involved: List[str]
    min_confluence: int  # Minimum timeframes that must agree
    created_date: datetime
    total_backtests: int = 0
    win_rate: float = 0.0
    avg_profit: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    best_cycles: List[str] = None
    performance_by_tf: Dict = None

class OrganicPatternEngine:
    """
    Learns patterns organically across ALL timeframes
    - Scans 1m, 5m, 15m, 30m, 1h, 4h, 1d charts
    - Finds what actually works using historical data
    - Tweaks patterns based on performance
    - Validates everything with backtesting
    """
    
    def __init__(self):
        self.timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        self.indicators = ['price', 'volume', 'rsi', 'macd', 'ema', 'sma', 'bb', 'support', 'resistance']
        self.create_databases()
        self.patterns = {}
        self.load_existing_patterns()
        print("🧠 Organic Pattern Engine: Learning from ALL timeframes")
    
    def create_databases(self):
        """Create enhanced pattern databases"""
        conn = sqlite3.connect('data/organic_patterns.db')
        cursor = conn.cursor()
        
        # Multi-timeframe patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mtf_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_name TEXT,
                conditions_json TEXT,
                entry_rules_json TEXT,
                exit_rules_json TEXT,
                timeframes_json TEXT,
                min_confluence INTEGER,
                created_date TEXT,
                last_updated TEXT,
                total_backtests INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_profit REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                best_cycles_json TEXT,
                performance_by_tf_json TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Pattern performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_backtests (
                backtest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT,
                timeframe TEXT,
                start_date TEXT,
                end_date TEXT,
                total_trades INTEGER,
                winning_trades INTEGER,
                total_profit REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                backtest_date TEXT,
                data_quality_score REAL
            )
        ''')
        
        # Real-time pattern matches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT,
                timestamp TEXT,
                timeframes_matched TEXT,
                confluence_score REAL,
                entry_price REAL,
                confidence REAL,
                outcome TEXT,
                exit_price REAL,
                profit_pct REAL,
                hold_time_minutes INTEGER
            )
        ''')
        
        # Pattern evolution tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_evolution (
                evolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_pattern_id TEXT,
                new_pattern_id TEXT,
                modification_type TEXT,
                performance_improvement REAL,
                evolution_date TEXT,
                reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Organic pattern databases initialized")
    
    def discover_patterns_from_history(self, symbol: str = 'ASTERUSDT', lookback_days: int = 90):
        """
        Organically discover patterns by analyzing ALL historical data
        This is where the magic happens - finding what ACTUALLY works
        """
        print(f"🔍 Discovering patterns from {lookback_days} days of history...")
        
        # Load historical data for all timeframes
        historical_data = {}
        for tf in self.timeframes:
            historical_data[tf] = self.load_historical_data(symbol, tf, lookback_days)
            print(f"📊 Loaded {len(historical_data[tf])} {tf} candles")
        
        # Find successful price movements (what we want to predict)
        successful_moves = self.identify_successful_moves(historical_data)
        print(f"🎯 Found {len(successful_moves)} successful moves to learn from")
        
        # For each successful move, analyze what conditions preceded it
        discovered_patterns = []
        for move in successful_moves:
            patterns = self.reverse_engineer_conditions(move, historical_data)
            discovered_patterns.extend(patterns)
        
        print(f"🧬 Discovered {len(discovered_patterns)} potential patterns")
        
        # Validate patterns with backtesting
        validated_patterns = []
        for pattern in discovered_patterns:
            performance = self.backtest_pattern(pattern, historical_data)
            if performance['win_rate'] > 0.6 and performance['profit_factor'] > 1.5:
                pattern.win_rate = performance['win_rate']
                pattern.profit_factor = performance['profit_factor']
                pattern.total_backtests = performance['total_trades']
                validated_patterns.append(pattern)
        
        print(f"✅ Validated {len(validated_patterns)} profitable patterns")
        
        # Save to database
        for pattern in validated_patterns:
            self.save_pattern(pattern)
        
        return validated_patterns
    
    def load_historical_data(self, symbol: str, timeframe: str, days: int) -> pd.DataFrame:
        """Load historical data for pattern discovery"""
        try:
            conn = sqlite3.connect('data/market_data.db')
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = '''
                SELECT timestamp, open, high, low, close, volume 
                FROM ohlcv 
                WHERE symbol = ? AND timeframe = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, timeframe, start_date.isoformat()))
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                
                # Add technical indicators
                df = self.add_technical_indicators(df)
            
            return df
            
        except Exception as e:
            print(f"Error loading {timeframe} data: {e}")
            return pd.DataFrame()
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators for pattern discovery"""
        if df.empty or len(df) < 50:
            return df
        
        try:
            # Moving averages
            df['ema_9'] = df['close'].ewm(span=9).mean()
            df['ema_21'] = df['close'].ewm(span=21).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema_12 - ema_26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Support/Resistance
            df['support'] = df['low'].rolling(window=20).min()
            df['resistance'] = df['high'].rolling(window=20).max()
            
            # Volume analysis
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price action
            df['body_size'] = abs(df['close'] - df['open']) / df['open']
            df['upper_wick'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['open']
            df['lower_wick'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['open']
            
        except Exception as e:
            print(f"Error adding indicators: {e}")
        
        return df
    
    def identify_successful_moves(self, historical_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        Identify successful price movements across all timeframes
        These are the outcomes we want to predict
        """
        successful_moves = []
        
        # Use 1-hour data as base for finding moves
        base_df = historical_data.get('1h', pd.DataFrame())
        if base_df.empty:
            return []
        
        for i in range(50, len(base_df) - 24):  # Look for moves with 24h forward projection
            current_price = base_df.iloc[i]['close']
            
            # Look ahead for profitable moves (2%+ within 24 hours)
            future_prices = base_df.iloc[i+1:i+25]['high'].max()
            profit_pct = (future_prices - current_price) / current_price * 100
            
            if profit_pct >= 2.0:  # 2%+ move = successful
                # Find the exact peak time
                peak_idx = base_df.iloc[i+1:i+25]['high'].idxmax()
                peak_price = base_df.loc[peak_idx]['high']
                
                successful_moves.append({
                    'entry_time': base_df.index[i],
                    'entry_price': current_price,
                    'peak_time': peak_idx,
                    'peak_price': peak_price,
                    'profit_pct': profit_pct,
                    'hold_hours': (peak_idx - base_df.index[i]).total_seconds() / 3600
                })
        
        # Sort by profit percentage (learn from best moves first)
        successful_moves.sort(key=lambda x: x['profit_pct'], reverse=True)
        
        return successful_moves[:100]  # Top 100 moves
    
    def reverse_engineer_conditions(self, move: Dict, historical_data: Dict[str, pd.DataFrame]) -> List[MultiTFPattern]:
        """
        Reverse engineer what conditions preceded a successful move
        This is the core learning algorithm
        """
        patterns = []
        entry_time = move['entry_time']
        
        # Look at conditions across all timeframes at entry time
        timeframe_conditions = {}
        
        for tf in self.timeframes:
            df = historical_data.get(tf, pd.DataFrame())
            if df.empty:
                continue
            
            # Find the closest candle to entry time
            try:
                entry_candle = df.loc[df.index <= entry_time].iloc[-1]
                prev_candle = df.loc[df.index <= entry_time].iloc[-2] if len(df.loc[df.index <= entry_time]) > 1 else None
                
                if prev_candle is not None:
                    conditions = self.extract_conditions_from_candle(entry_candle, prev_candle, tf)
                    timeframe_conditions[tf] = conditions
            except:
                continue
        
        # Generate pattern combinations
        if len(timeframe_conditions) >= 2:  # Need at least 2 timeframes
            pattern = self.create_pattern_from_conditions(
                timeframe_conditions, 
                move['profit_pct'], 
                move['hold_hours']
            )
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def extract_conditions_from_candle(self, current_candle, previous_candle, timeframe: str) -> List[PatternCondition]:
        """Extract meaningful conditions from a candle"""
        conditions = []
        
        try:
            # Price action conditions
            if current_candle['close'] > current_candle['open']:
                conditions.append(PatternCondition(
                    timeframe=timeframe,
                    indicator='candle_type',
                    comparison='==',
                    value=1,  # 1 = bullish
                    weight=0.5
                ))
            
            # RSI conditions
            if not pd.isna(current_candle.get('rsi', np.nan)):
                rsi = current_candle['rsi']
                if 30 <= rsi <= 50:  # Oversold recovery
                    conditions.append(PatternCondition(
                        timeframe=timeframe,
                        indicator='rsi',
                        comparison='between',
                        value=40,  # Approximate middle
                        weight=0.8
                    ))
            
            # Volume conditions
            if not pd.isna(current_candle.get('volume_ratio', np.nan)):
                vol_ratio = current_candle['volume_ratio']
                if vol_ratio > 1.5:  # Volume spike
                    conditions.append(PatternCondition(
                        timeframe=timeframe,
                        indicator='volume_spike',
                        comparison='>',
                        value=1.5,
                        weight=1.0
                    ))
            
            # EMA conditions
            if (not pd.isna(current_candle.get('ema_9', np.nan)) and 
                not pd.isna(current_candle.get('ema_21', np.nan))):
                if current_candle['ema_9'] > current_candle['ema_21']:
                    conditions.append(PatternCondition(
                        timeframe=timeframe,
                        indicator='ema_9_above_21',
                        comparison='==',
                        value=1,
                        weight=0.7
                    ))
            
            # Support/Resistance conditions
            if (not pd.isna(current_candle.get('support', np.nan)) and 
                current_candle['low'] <= current_candle['support'] * 1.02):  # Near support
                conditions.append(PatternCondition(
                    timeframe=timeframe,
                    indicator='near_support',
                    comparison='<=',
                    value=1.02,  # Within 2% of support
                    weight=0.9
                ))
            
        except Exception as e:
            pass
        
        return conditions
    
    def create_pattern_from_conditions(self, timeframe_conditions: Dict, profit_pct: float, hold_hours: float) -> Optional[MultiTFPattern]:
        """Create a pattern from multi-timeframe conditions"""
        
        all_conditions = []
        timeframes_involved = []
        
        for tf, conditions in timeframe_conditions.items():
            if conditions:  # Only include timeframes with valid conditions
                all_conditions.extend(conditions)
                timeframes_involved.append(tf)
        
        if len(all_conditions) < 2 or len(timeframes_involved) < 2:
            return None
        
        # Create pattern ID
        pattern_id = f"organic_{len(timeframes_involved)}tf_{int(profit_pct*10)}p_{int(datetime.now().timestamp())}"
        
        # Create pattern name
        pattern_name = f"Multi-TF {'+'.join(timeframes_involved)} ({profit_pct:.1f}% target)"
        
        # Entry rules
        entry_rules = {
            'min_confluence': min(len(timeframes_involved), 3),
            'min_confidence': 70,
            'volume_requirement': True
        }
        
        # Exit rules based on historical performance
        exit_rules = {
            'target_profit_pct': min(profit_pct * 0.8, 5.0),  # Take 80% of historical move
            'stop_loss_pct': 2.0,
            'max_hold_hours': min(hold_hours * 1.5, 24.0)
        }
        
        return MultiTFPattern(
            pattern_id=pattern_id,
            name=pattern_name,
            conditions=all_conditions,
            entry_rules=entry_rules,
            exit_rules=exit_rules,
            timeframes_involved=timeframes_involved,
            min_confluence=len(timeframes_involved),
            created_date=datetime.now()
        )
    
    def backtest_pattern(self, pattern: MultiTFPattern, historical_data: Dict[str, pd.DataFrame]) -> Dict:
        """Backtest a pattern against historical data"""
        
        results = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'avg_profit': 0,
            'max_drawdown': 0
        }
        
        # Use 1h timeframe as base for backtesting
        base_df = historical_data.get('1h', pd.DataFrame())
        if base_df.empty or len(base_df) < 100:
            return results
        
        trades = []
        
        for i in range(50, len(base_df) - 50):
            # Check if pattern conditions are met
            if self.check_pattern_match(pattern, historical_data, base_df.index[i]):
                entry_price = base_df.iloc[i]['close']
                
                # Simulate trade
                target_price = entry_price * (1 + pattern.exit_rules['target_profit_pct'] / 100)
                stop_price = entry_price * (1 - pattern.exit_rules['stop_loss_pct'] / 100)
                max_hold_candles = int(pattern.exit_rules['max_hold_hours'])
                
                # Look ahead for exit
                for j in range(i + 1, min(i + max_hold_candles + 1, len(base_df))):
                    candle = base_df.iloc[j]
                    
                    if candle['high'] >= target_price:
                        # Target hit
                        profit_pct = (target_price - entry_price) / entry_price * 100
                        trades.append(profit_pct)
                        break
                    elif candle['low'] <= stop_price:
                        # Stop hit
                        loss_pct = (stop_price - entry_price) / entry_price * 100
                        trades.append(loss_pct)
                        break
                else:
                    # Time exit
                    exit_price = base_df.iloc[min(i + max_hold_candles, len(base_df) - 1)]['close']
                    profit_pct = (exit_price - entry_price) / entry_price * 100
                    trades.append(profit_pct)
        
        if trades:
            results['total_trades'] = len(trades)
            results['winning_trades'] = sum(1 for t in trades if t > 0)
            results['total_profit'] = sum(trades)
            results['win_rate'] = results['winning_trades'] / results['total_trades']
            results['avg_profit'] = results['total_profit'] / results['total_trades']
            
            winning_trades = [t for t in trades if t > 0]
            losing_trades = [abs(t) for t in trades if t < 0]
            
            if losing_trades:
                avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0
                avg_loss = sum(losing_trades) / len(losing_trades)
                results['profit_factor'] = avg_win / avg_loss if avg_loss > 0 else 0
        
        return results
    
    def check_pattern_match(self, pattern: MultiTFPattern, historical_data: Dict[str, pd.DataFrame], timestamp) -> bool:
        """Check if pattern conditions are met at specific timestamp"""
        
        matched_timeframes = 0
        
        for tf in pattern.timeframes_involved:
            df = historical_data.get(tf, pd.DataFrame())
            if df.empty:
                continue
            
            try:
                # Find closest candle
                candle = df.loc[df.index <= timestamp].iloc[-1]
                
                # Check conditions for this timeframe
                tf_conditions = [c for c in pattern.conditions if c.timeframe == tf]
                tf_matches = 0
                
                for condition in tf_conditions:
                    if self.evaluate_condition(condition, candle):
                        tf_matches += 1
                
                # Timeframe matches if >50% of conditions met
                if tf_matches >= len(tf_conditions) * 0.5:
                    matched_timeframes += 1
                    
            except:
                continue
        
        # Pattern matches if enough timeframes agree
        return matched_timeframes >= pattern.min_confluence
    
    def evaluate_condition(self, condition: PatternCondition, candle) -> bool:
        """Evaluate a single pattern condition"""
        try:
            if condition.indicator == 'candle_type':
                actual = 1 if candle['close'] > candle['open'] else 0
            elif condition.indicator == 'rsi':
                actual = candle.get('rsi', 50)
            elif condition.indicator == 'volume_spike':
                actual = candle.get('volume_ratio', 1)
            elif condition.indicator == 'ema_9_above_21':
                actual = 1 if candle.get('ema_9', 0) > candle.get('ema_21', 0) else 0
            elif condition.indicator == 'near_support':
                support = candle.get('support', candle['low'])
                actual = candle['low'] / support if support > 0 else 1
            else:
                return False
            
            if condition.comparison == '>':
                return actual > condition.value
            elif condition.comparison == '>=':
                return actual >= condition.value
            elif condition.comparison == '<':
                return actual < condition.value
            elif condition.comparison == '<=':
                return actual <= condition.value
            elif condition.comparison == '==':
                return abs(actual - condition.value) < 0.1
            elif condition.comparison == 'between':
                return condition.value - 10 <= actual <= condition.value + 10
            
        except Exception as e:
            return False
        
        return False
    
    def save_pattern(self, pattern: MultiTFPattern):
        """Save pattern to database"""
        try:
            conn = sqlite3.connect('data/organic_patterns.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO mtf_patterns
                (pattern_id, pattern_name, conditions_json, entry_rules_json, exit_rules_json,
                 timeframes_json, min_confluence, created_date, win_rate, profit_factor, total_backtests)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id,
                pattern.name,
                json.dumps([{
                    'timeframe': c.timeframe,
                    'indicator': c.indicator,
                    'comparison': c.comparison,
                    'value': c.value,
                    'weight': c.weight
                } for c in pattern.conditions]),
                json.dumps(pattern.entry_rules),
                json.dumps(pattern.exit_rules),
                json.dumps(pattern.timeframes_involved),
                pattern.min_confluence,
                pattern.created_date.isoformat(),
                pattern.win_rate,
                pattern.profit_factor,
                pattern.total_backtests
            ))
            
            conn.commit()
            conn.close()
            
            print(f"💾 Saved pattern: {pattern.name} (Win rate: {pattern.win_rate:.1%})")
            
        except Exception as e:
            print(f"Error saving pattern: {e}")
    
    def load_existing_patterns(self):
        """Load existing patterns from database"""
        try:
            conn = sqlite3.connect('data/organic_patterns.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM mtf_patterns WHERE is_active = 1')
            rows = cursor.fetchall()
            
            for row in rows:
                # Reconstruct pattern object
                pattern_id = row[0]
                self.patterns[pattern_id] = {
                    'name': row[1],
                    'win_rate': row[8],
                    'profit_factor': row[9],
                    'timeframes': json.loads(row[5]),
                    'total_backtests': row[10]
                }
            
            conn.close()
            print(f"📚 Loaded {len(self.patterns)} existing patterns")
            
        except Exception as e:
            print(f"Error loading patterns: {e}")
    
    def get_best_patterns(self, min_win_rate: float = 0.65) -> List[Dict]:
        """Get best performing patterns"""
        best_patterns = []
        
        for pattern_id, pattern in self.patterns.items():
            if (pattern['win_rate'] >= min_win_rate and 
                pattern['profit_factor'] > 1.5 and 
                pattern['total_backtests'] >= 10):
                best_patterns.append({
                    'pattern_id': pattern_id,
                    'name': pattern['name'],
                    'win_rate': pattern['win_rate'],
                    'profit_factor': pattern['profit_factor'],
                    'timeframes': pattern['timeframes'],
                    'total_backtests': pattern['total_backtests']
                })
        
        # Sort by win rate * profit factor
        best_patterns.sort(key=lambda x: x['win_rate'] * x['profit_factor'], reverse=True)
        return best_patterns[:10]  # Top 10

# Global instance
organic_engine = OrganicPatternEngine()

if __name__ == "__main__":
    print("🚀 Starting Organic Pattern Discovery...")
    
    # Discover patterns from historical data
    patterns = organic_engine.discover_patterns_from_history(
        symbol='ASTERUSDT', 
        lookback_days=90
    )
    
    print(f"\n✅ Discovery complete! Found {len(patterns)} profitable patterns")
    
    # Show best patterns
    best = organic_engine.get_best_patterns()
    print(f"\n🏆 Top patterns:")
    for i, pattern in enumerate(best[:5], 1):
        print(f"{i}. {pattern['name']}")
        print(f"   Win Rate: {pattern['win_rate']:.1%}")
        print(f"   Profit Factor: {pattern['profit_factor']:.2f}")
        print(f"   Timeframes: {', '.join(pattern['timeframes'])}")
        print(f"   Backtests: {pattern['total_backtests']}")
        print()