"""
Market Regime Detection
Determines if market is TRENDING, RANGING, or VOLATILE across multiple timeframes
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

class MarketRegimeDetector:
    
    def __init__(self):
        self.create_db()
    
    def create_db(self):
        """Create database for regime tracking"""
        conn = sqlite3.connect('market_regime.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regime_history (
                timestamp TEXT,
                symbol TEXT,
                timeframe TEXT,
                regime TEXT,
                trend_strength REAL,
                volatility REAL,
                atr REAL,
                PRIMARY KEY (timestamp, symbol, timeframe)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def detect_regime(self, df, timeframe='1h'):
        """
        Detect market regime from OHLCV dataframe
        Returns: TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE
        """
        
        if df.empty or len(df) < 50:
            return {
                'regime': 'UNKNOWN',
                'trend_strength': 0,
                'volatility': 0,
                'confidence': 0
            }
        
        df = df.copy()
        
        df['ema_20'] = df['close'].ewm(span=20).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        df['atr'] = self.calculate_atr(df, period=14)
        
        df['higher_high'] = df['high'] > df['high'].shift(1)
        df['higher_low'] = df['low'] > df['low'].shift(1)
        df['lower_high'] = df['high'] < df['high'].shift(1)
        df['lower_low'] = df['low'] < df['low'].shift(1)
        
        last_20 = df.tail(20)
        
        hh_count = last_20['higher_high'].sum()
        hl_count = last_20['higher_low'].sum()
        lh_count = last_20['lower_high'].sum()
        ll_count = last_20['lower_low'].sum()
        
        uptrend_score = (hh_count + hl_count) / 40
        downtrend_score = (lh_count + ll_count) / 40
        
        current_price = df['close'].iloc[-1]
        ema_20 = df['ema_20'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        
        above_emas = current_price > ema_20 and current_price > ema_50
        below_emas = current_price < ema_20 and current_price < ema_50
        ema_aligned_up = ema_20 > ema_50
        ema_aligned_down = ema_20 < ema_50
        
        recent_volatility = df['atr'].iloc[-1] / current_price
        avg_volatility = df['atr'].tail(50).mean() / df['close'].tail(50).mean()
        
        volatility_ratio = recent_volatility / avg_volatility if avg_volatility > 0 else 1.0
        
        price_range = (df['high'].tail(20).max() - df['low'].tail(20).min()) / current_price
        
        if volatility_ratio > 1.5 and price_range > 0.05:
            regime = 'VOLATILE'
            trend_strength = 0
            confidence = volatility_ratio * 50
        
        elif uptrend_score > 0.6 and above_emas and ema_aligned_up:
            regime = 'TRENDING_UP'
            trend_strength = uptrend_score * 100
            confidence = min(uptrend_score * 100, 95)
        
        elif downtrend_score > 0.6 and below_emas and ema_aligned_down:
            regime = 'TRENDING_DOWN'
            trend_strength = -downtrend_score * 100
            confidence = min(downtrend_score * 100, 95)
        
        elif price_range < 0.03:
            regime = 'RANGING'
            trend_strength = 0
            confidence = (1 - price_range / 0.03) * 80
        
        else:
            regime = 'MIXED'
            trend_strength = (uptrend_score - downtrend_score) * 50
            confidence = 40
        
        return {
            'regime': regime,
            'trend_strength': trend_strength,
            'volatility': recent_volatility,
            'volatility_ratio': volatility_ratio,
            'atr': df['atr'].iloc[-1],
            'confidence': confidence,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'price_range_pct': price_range * 100
        }
    
    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        return true_range.rolling(period).mean()
    
    def detect_multi_timeframe_regime(self, symbol, market_data):
        """
        Analyze regime across multiple timeframes
        Returns overall market structure
        """
        
        timeframes = {
            '1m': market_data.get('1m'),
            '5m': market_data.get('5m'),
            '15m': market_data.get('15m'),
            '1h': market_data.get('1h'),
            '4h': market_data.get('4h')
        }
        
        regimes = {}
        
        for tf, df in timeframes.items():
            if df is not None and not df.empty:
                regimes[tf] = self.detect_regime(df, tf)
        
        trending_up_count = sum(1 for r in regimes.values() if r['regime'] == 'TRENDING_UP')
        trending_down_count = sum(1 for r in regimes.values() if r['regime'] == 'TRENDING_DOWN')
        ranging_count = sum(1 for r in regimes.values() if r['regime'] == 'RANGING')
        
        total = len(regimes)
        
        if trending_up_count >= total * 0.6:
            overall_regime = 'STRONG_UPTREND'
            strategy = 'Ride momentum. Buy dips. Hold winners. Increase leverage.'
        elif trending_down_count >= total * 0.6:
            overall_regime = 'STRONG_DOWNTREND'
            strategy = 'Stay defensive. Wait for reversal. Minimal exposure.'
        elif ranging_count >= total * 0.5:
            overall_regime = 'RANGING_MARKET'
            strategy = 'Mean reversion plays. Buy support, sell resistance. Lower leverage.'
        else:
            overall_regime = 'MIXED_SIGNALS'
            strategy = 'Wait for clarity. Reduce position sizes. Be selective.'
        
        return {
            'overall_regime': overall_regime,
            'strategy': strategy,
            'timeframe_regimes': regimes,
            'trending_up_count': trending_up_count,
            'trending_down_count': trending_down_count,
            'ranging_count': ranging_count,
            'alignment_score': max(trending_up_count, trending_down_count, ranging_count) / total * 100
        }
    
    def log_regime(self, symbol, timeframe, regime_data):
        """Log regime detection to database"""
        conn = sqlite3.connect('market_regime.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO regime_history 
            (timestamp, symbol, timeframe, regime, trend_strength, volatility, atr)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            symbol,
            timeframe,
            regime_data['regime'],
            regime_data['trend_strength'],
            regime_data['volatility'],
            regime_data['atr']
        ))
        
        conn.commit()
        conn.close()
    
    def get_regime_summary(self, multi_tf_analysis):
        """Generate human-readable regime summary"""
        
        overall = multi_tf_analysis['overall_regime']
        strategy = multi_tf_analysis['strategy']
        alignment = multi_tf_analysis['alignment_score']
        
        summary = f"""
📊 MARKET REGIME: {overall}
   • Alignment Score: {alignment:.0f}%
   • Strategy: {strategy}

🕐 Timeframe Breakdown:
"""
        
        for tf, data in multi_tf_analysis['timeframe_regimes'].items():
            emoji = '📈' if 'UP' in data['regime'] else '📉' if 'DOWN' in data['regime'] else '↔️'
            summary += f"   • {tf}: {emoji} {data['regime']} (confidence: {data['confidence']:.0f}%)\n"
        
        return summary

if __name__ == '__main__':
    print("✅ Market Regime Detector Ready")