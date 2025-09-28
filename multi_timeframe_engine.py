"""
Multi-Timeframe Analysis Engine
Analyzes all timeframes simultaneously and finds confluence
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3

class MultiTimeframeEngine:
    
    def __init__(self):
        self.timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    
    def load_timeframe_data(self, symbol, timeframe, limit=200):
        """Load data for specific timeframe"""
        try:
            conn = sqlite3.connect('market_data.db')
            
            query = '''
                SELECT timestamp, open, high, low, close, volume 
                FROM ohlcv 
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, timeframe, limit))
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            return pd.DataFrame()
    
    def analyze_timeframe(self, df):
        """Analyze single timeframe and extract signals"""
        
        if df.empty or len(df) < 50:
            return {
                'trend': 'UNKNOWN',
                'strength': 0,
                'support': None,
                'resistance': None,
                'signal': 'WAIT'
            }
        
        df = df.copy()
        
        df['ema_9'] = df['close'].ewm(span=9).mean()
        df['ema_20'] = df['close'].ewm(span=20).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        current_price = df['close'].iloc[-1]
        ema_9 = df['ema_9'].iloc[-1]
        ema_20 = df['ema_20'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        
        if current_price > ema_9 > ema_20 > ema_50:
            trend = 'STRONG_UPTREND'
            strength = 90
        elif current_price > ema_20 > ema_50:
            trend = 'UPTREND'
            strength = 70
        elif current_price > ema_50:
            trend = 'WEAK_UPTREND'
            strength = 50
        elif current_price < ema_9 < ema_20 < ema_50:
            trend = 'STRONG_DOWNTREND'
            strength = -90
        elif current_price < ema_20 < ema_50:
            trend = 'DOWNTREND'
            strength = -70
        elif current_price < ema_50:
            trend = 'WEAK_DOWNTREND'
            strength = -50
        else:
            trend = 'RANGING'
            strength = 0
        
        recent_lows = df['low'].tail(20).nsmallest(3)
        recent_highs = df['high'].tail(20).nlargest(3)
        
        support = recent_lows.mean()
        resistance = recent_highs.mean()
        
        if trend in ['STRONG_UPTREND', 'UPTREND'] and rsi < 70:
            signal = 'BUY'
        elif trend in ['STRONG_DOWNTREND', 'DOWNTREND']:
            signal = 'SELL'
        elif trend == 'RANGING':
            if current_price < support * 1.01:
                signal = 'BUY'
            elif current_price > resistance * 0.99:
                signal = 'SELL'
            else:
                signal = 'WAIT'
        else:
            signal = 'WAIT'
        
        return {
            'trend': trend,
            'strength': strength,
            'rsi': rsi,
            'current_price': current_price,
            'ema_9': ema_9,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'support': support,
            'resistance': resistance,
            'signal': signal
        }
    
    def analyze_all_timeframes(self, symbol):
        """Analyze all timeframes and find confluence"""
        
        analysis = {}
        
        for tf in self.timeframes:
            df = self.load_timeframe_data(symbol, tf, limit=200)
            analysis[tf] = self.analyze_timeframe(df)
        
        confluence = self.calculate_confluence(analysis)
        
        return {
            'timeframe_analysis': analysis,
            'confluence': confluence
        }
    
    def calculate_confluence(self, analysis):
        """Calculate multi-timeframe confluence"""
        
        buy_signals = sum(1 for tf_data in analysis.values() if tf_data['signal'] == 'BUY')
        sell_signals = sum(1 for tf_data in analysis.values() if tf_data['signal'] == 'SELL')
        wait_signals = sum(1 for tf_data in analysis.values() if tf_data['signal'] == 'WAIT')
        
        total_tfs = len(analysis)
        
        uptrend_count = sum(1 for tf_data in analysis.values() if 'UPTREND' in tf_data['trend'])
        downtrend_count = sum(1 for tf_data in analysis.values() if 'DOWNTREND' in tf_data['trend'])
        
        avg_strength = np.mean([tf_data['strength'] for tf_data in analysis.values()])
        
        if buy_signals >= total_tfs * 0.6 and uptrend_count >= total_tfs * 0.6:
            overall_signal = 'STRONG_BUY'
            confidence = (buy_signals / total_tfs) * 100
            reasoning = f'{buy_signals}/{total_tfs} timeframes bullish. Strong multi-TF alignment.'
        
        elif buy_signals >= total_tfs * 0.4 and uptrend_count >= total_tfs * 0.5:
            overall_signal = 'BUY'
            confidence = (buy_signals / total_tfs) * 80
            reasoning = f'{buy_signals}/{total_tfs} timeframes bullish. Good confluence.'
        
        elif sell_signals >= total_tfs * 0.6:
            overall_signal = 'SELL'
            confidence = (sell_signals / total_tfs) * 100
            reasoning = f'{sell_signals}/{total_tfs} timeframes bearish. Avoid longs.'
        
        elif wait_signals >= total_tfs * 0.5:
            overall_signal = 'WAIT'
            confidence = 40
            reasoning = f'Mixed signals across timeframes. No clear direction.'
        
        else:
            overall_signal = 'WAIT'
            confidence = 30
            reasoning = 'Insufficient alignment across timeframes.'
        
        return {
            'overall_signal': overall_signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'buy_count': buy_signals,
            'sell_count': sell_signals,
            'wait_count': wait_signals,
            'uptrend_count': uptrend_count,
            'downtrend_count': downtrend_count,
            'avg_strength': avg_strength,
            'alignment_score': max(buy_signals, sell_signals) / total_tfs * 100
        }
    
    def get_best_entry_timeframe(self, analysis):
        """Determine which timeframe offers best entry based on confluence"""
        
        best_tf = None
        best_score = 0
        
        for tf, data in analysis['timeframe_analysis'].items():
            if data['signal'] == 'BUY':
                score = abs(data['strength'])
                
                if score > best_score:
                    best_score = score
                    best_tf = tf
        
        return best_tf
    
    def generate_trading_plan(self, symbol):
        """Generate complete multi-timeframe trading plan"""
        
        analysis = self.analyze_all_timeframes(symbol)
        
        confluence = analysis['confluence']
        
        if confluence['overall_signal'] in ['STRONG_BUY', 'BUY']:
            best_entry_tf = self.get_best_entry_timeframe(analysis)
            
            higher_tf_data = analysis['timeframe_analysis'].get('1h', {})
            lower_tf_data = analysis['timeframe_analysis'].get('5m', {})
            
            plan = {
                'action': 'ENTER_LONG',
                'signal_strength': confluence['overall_signal'],
                'confidence': confluence['confidence'],
                'reasoning': confluence['reasoning'],
                'best_entry_timeframe': best_entry_tf,
                'entry_price': lower_tf_data.get('current_price', 0),
                'stop_loss': lower_tf_data.get('support', 0),
                'take_profit': higher_tf_data.get('resistance', 0),
                'multi_tf_alignment': confluence['alignment_score']
            }
        
        else:
            plan = {
                'action': 'WAIT',
                'signal_strength': confluence['overall_signal'],
                'confidence': confluence['confidence'],
                'reasoning': confluence['reasoning']
            }
        
        return plan

if __name__ == '__main__':
    engine = MultiTimeframeEngine()
    
    print("\n" + "="*70)
    print("🔭 MULTI-TIMEFRAME ANALYSIS ENGINE")
    print("="*70 + "\n")
    
    plan = engine.generate_trading_plan('BTC/USDT')
    
    print(f"Action: {plan['action']}")
    print(f"Signal: {plan['signal_strength']}")
    print(f"Confidence: {plan['confidence']:.0f}%")
    print(f"Reasoning: {plan['reasoning']}")
    
    if plan['action'] != 'WAIT':
        print(f"\nEntry TF: {plan.get('best_entry_timeframe')}")
        print(f"Entry: ${plan.get('entry_price', 0):.2f}")
        print(f"Stop: ${plan.get('stop_loss', 0):.2f}")
        print(f"Target: ${plan.get('take_profit', 0):.2f}")
    
    print("\n✅ Multi-Timeframe Engine Ready")