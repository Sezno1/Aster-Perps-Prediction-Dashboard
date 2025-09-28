"""
Pattern Mining Engine
Automatically discovers profitable patterns from historical data
Uses statistical analysis and ML techniques to find repeating setups
"""

import pandas as pd
import numpy as np
import sqlite3
from pattern_library import PatternLibrary
from market_regime import MarketRegimeDetector
from datetime import datetime, timedelta

class PatternMiner:
    
    def __init__(self):
        self.pattern_lib = PatternLibrary()
        self.regime_detector = MarketRegimeDetector()
    
    def load_historical_data(self, symbol, timeframe, days=90):
        """Load historical data from market_data.db"""
        try:
            conn = sqlite3.connect('market_data.db')
            
            query = '''
                SELECT timestamp, open, high, low, close, volume 
                FROM ohlcv 
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, timeframe))
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df):
        """Calculate technical indicators for pattern recognition"""
        
        if df.empty or len(df) < 50:
            return df
        
        df = df.copy()
        
        df['ema_9'] = df['close'].ewm(span=9).mean()
        df['ema_20'] = df['close'].ewm(span=20).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['std_20'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['sma_20'] + (df['std_20'] * 2)
        df['bb_lower'] = df['sma_20'] - (df['std_20'] * 2)
        
        df['vol_ma'] = df['volume'].rolling(window=20).mean()
        df['vol_ratio'] = df['volume'] / df['vol_ma']
        
        df['price_change_pct'] = df['close'].pct_change() * 100
        
        df['higher_high'] = df['high'] > df['high'].shift(1)
        df['higher_low'] = df['low'] > df['low'].shift(1)
        
        return df
    
    def find_volume_spike_pattern(self, df, min_spike=2.5, min_win_rate=0.7):
        """
        Discover: When volume spikes X times average, what happens to price?
        """
        
        df = self.calculate_indicators(df)
        
        if df.empty or 'vol_ratio' not in df.columns:
            return None
        
        volume_spikes = df[df['vol_ratio'] > min_spike].copy()
        
        if len(volume_spikes) < 20:
            return None
        
        trades = []
        
        for idx in volume_spikes.index:
            try:
                entry_idx = df.index.get_loc(idx)
                
                if entry_idx + 5 >= len(df):
                    continue
                
                entry_price = df.iloc[entry_idx]['close']
                
                future_high = df.iloc[entry_idx+1:entry_idx+6]['high'].max()
                future_low = df.iloc[entry_idx+1:entry_idx+6]['low'].min()
                
                upside = ((future_high - entry_price) / entry_price) * 100
                downside = ((entry_price - future_low) / entry_price) * 100
                
                if upside > 2:
                    outcome = 'WIN'
                    profit = upside
                elif downside > 1:
                    outcome = 'LOSS'
                    profit = -downside
                else:
                    outcome = 'NEUTRAL'
                    profit = 0
                
                trades.append({
                    'outcome': outcome,
                    'profit': profit,
                    'entry_price': entry_price,
                    'vol_ratio': df.iloc[entry_idx]['vol_ratio']
                })
                
            except Exception:
                continue
        
        if len(trades) < 10:
            return None
        
        wins = sum(1 for t in trades if t['outcome'] == 'WIN')
        losses = sum(1 for t in trades if t['outcome'] == 'LOSS')
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        
        if win_rate >= min_win_rate:
            avg_profit = np.mean([t['profit'] for t in trades if t['outcome'] == 'WIN'])
            
            pattern_data = {
                'pattern_name': f'Volume Spike {min_spike}x Pattern',
                'win_rate': win_rate * 100,
                'total_trades': len(trades),
                'wins': wins,
                'losses': losses,
                'avg_profit': avg_profit,
                'description': f'When volume spikes >{min_spike}x average, price tends to move up {avg_profit:.1f}% within 5 candles'
            }
            
            return pattern_data
        
        return None
    
    def find_ema_bounce_pattern(self, df, ema_period=20, min_win_rate=0.7):
        """
        Discover: In uptrend, when price touches EMA and bounces, what's the win rate?
        """
        
        df = self.calculate_indicators(df)
        
        if df.empty or f'ema_{ema_period}' not in df.columns:
            return None
        
        ema_col = f'ema_{ema_period}'
        
        uptrend = df[df['close'] > df[ema_col]]
        
        bounces = []
        
        for i in range(1, len(uptrend) - 5):
            try:
                current_idx = i
                prev_idx = i - 1
                
                current = uptrend.iloc[current_idx]
                prev = uptrend.iloc[prev_idx]
                
                touched_ema = current['low'] <= current[ema_col] * 1.005
                bounced = current['close'] > current['low']
                
                if touched_ema and bounced:
                    entry_price = current['close']
                    
                    future_high = uptrend.iloc[current_idx+1:current_idx+6]['high'].max()
                    future_low = uptrend.iloc[current_idx+1:current_idx+6]['low'].min()
                    
                    upside = ((future_high - entry_price) / entry_price) * 100
                    downside = ((entry_price - future_low) / entry_price) * 100
                    
                    if upside > 1.5:
                        outcome = 'WIN'
                        profit = upside
                    elif downside > 1:
                        outcome = 'LOSS'
                        profit = -downside
                    else:
                        outcome = 'NEUTRAL'
                        profit = 0
                    
                    bounces.append({'outcome': outcome, 'profit': profit})
                    
            except Exception:
                continue
        
        if len(bounces) < 10:
            return None
        
        wins = sum(1 for b in bounces if b['outcome'] == 'WIN')
        losses = sum(1 for b in bounces if b['outcome'] == 'LOSS')
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        
        if win_rate >= min_win_rate:
            avg_profit = np.mean([b['profit'] for b in bounces if b['outcome'] == 'WIN'])
            
            return {
                'pattern_name': f'EMA-{ema_period} Bounce in Uptrend',
                'win_rate': win_rate * 100,
                'total_trades': len(bounces),
                'wins': wins,
                'losses': losses,
                'avg_profit': avg_profit,
                'description': f'Pullback to EMA-{ema_period} in uptrend typically gains {avg_profit:.1f}% within 5 candles'
            }
        
        return None
    
    def find_rsi_oversold_pattern(self, df, rsi_threshold=30, min_win_rate=0.65):
        """
        Discover: When RSI hits oversold in uptrend, reversal probability?
        """
        
        df = self.calculate_indicators(df)
        
        if df.empty or 'rsi' not in df.columns:
            return None
        
        oversold_signals = df[(df['rsi'] < rsi_threshold) & (df['close'] > df['ema_50'])].copy()
        
        if len(oversold_signals) < 10:
            return None
        
        trades = []
        
        for idx in oversold_signals.index:
            try:
                entry_idx = df.index.get_loc(idx)
                
                if entry_idx + 10 >= len(df):
                    continue
                
                entry_price = df.iloc[entry_idx]['close']
                
                future_high = df.iloc[entry_idx+1:entry_idx+11]['high'].max()
                future_low = df.iloc[entry_idx+1:entry_idx+11]['low'].min()
                
                upside = ((future_high - entry_price) / entry_price) * 100
                downside = ((entry_price - future_low) / entry_price) * 100
                
                if upside > 2:
                    outcome = 'WIN'
                    profit = upside
                elif downside > 1.5:
                    outcome = 'LOSS'
                    profit = -downside
                else:
                    outcome = 'NEUTRAL'
                    profit = 0
                
                trades.append({'outcome': outcome, 'profit': profit})
                
            except Exception:
                continue
        
        if len(trades) < 5:
            return None
        
        wins = sum(1 for t in trades if t['outcome'] == 'WIN')
        losses = sum(1 for t in trades if t['outcome'] == 'LOSS')
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        
        if win_rate >= min_win_rate:
            avg_profit = np.mean([t['profit'] for t in trades if t['outcome'] == 'WIN'])
            
            return {
                'pattern_name': f'RSI Oversold (<{rsi_threshold}) in Uptrend',
                'win_rate': win_rate * 100,
                'total_trades': len(trades),
                'wins': wins,
                'losses': losses,
                'avg_profit': avg_profit,
                'description': f'RSI oversold in uptrend reverses for {avg_profit:.1f}% average gain'
            }
        
        return None
    
    def mine_patterns(self, symbol='BTC/USDT', timeframe='1h', days=180):
        """
        Main pattern mining function - discovers all patterns
        """
        
        print(f"\n⛏️  Mining patterns from {symbol} {timeframe} (last {days} days)...")
        
        df = self.load_historical_data(symbol, timeframe, days)
        
        if df.empty:
            print(f"❌ No data available for {symbol} {timeframe}")
            return []
        
        print(f"   Loaded {len(df)} candles")
        
        discovered_patterns = []
        
        print("\n   🔍 Searching for Volume Spike patterns...")
        vol_pattern = self.find_volume_spike_pattern(df, min_spike=2.5)
        if vol_pattern:
            discovered_patterns.append(vol_pattern)
            print(f"   ✅ Found: {vol_pattern['pattern_name']} - {vol_pattern['win_rate']:.1f}% win rate")
        
        print("\n   🔍 Searching for EMA Bounce patterns...")
        for ema in [20, 50]:
            ema_pattern = self.find_ema_bounce_pattern(df, ema_period=ema)
            if ema_pattern:
                discovered_patterns.append(ema_pattern)
                print(f"   ✅ Found: {ema_pattern['pattern_name']} - {ema_pattern['win_rate']:.1f}% win rate")
        
        print("\n   🔍 Searching for RSI Oversold patterns...")
        rsi_pattern = self.find_rsi_oversold_pattern(df, rsi_threshold=30)
        if rsi_pattern:
            discovered_patterns.append(rsi_pattern)
            print(f"   ✅ Found: {rsi_pattern['pattern_name']} - {rsi_pattern['win_rate']:.1f}% win rate")
        
        print(f"\n✅ Pattern mining complete: {len(discovered_patterns)} patterns discovered")
        
        return discovered_patterns

if __name__ == '__main__':
    miner = PatternMiner()
    
    print("\n" + "="*70)
    print("⛏️  PATTERN MINING ENGINE")
    print("="*70)
    
    patterns = miner.mine_patterns('BTC/USDT', '1h', 180)
    
    if patterns:
        print("\n📊 Discovered Patterns Summary:")
        for p in patterns:
            print(f"\n   {p['pattern_name']}")
            print(f"   Win Rate: {p['win_rate']:.1f}%")
            print(f"   Trades: {p['total_trades']} ({p['wins']}W / {p['losses']}L)")
            print(f"   Avg Profit: {p['avg_profit']:.2f}%")
            print(f"   Description: {p['description']}")
    else:
        print("\n   No patterns met minimum criteria (need more data)")