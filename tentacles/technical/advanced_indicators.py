"""
Advanced Technical Indicators
Candlestick patterns, wick analysis, multi-timeframe, MA crossovers, Bollinger Bands, RSI divergence
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class AdvancedIndicators:
    
    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> Dict:
        """
        Detect common candlestick patterns
        df must have: open, high, low, close columns
        """
        if len(df) < 3:
            return {'patterns': [], 'signal': 'NEUTRAL'}
        
        patterns = []
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        body = abs(last['close'] - last['open'])
        range_size = last['high'] - last['low']
        upper_wick = last['high'] - max(last['open'], last['close'])
        lower_wick = min(last['open'], last['close']) - last['low']
        
        # Hammer (bullish reversal)
        if (lower_wick > body * 2 and 
            upper_wick < body * 0.3 and 
            last['close'] > last['open']):
            patterns.append({
                'name': 'HAMMER',
                'type': 'BULLISH',
                'strength': 'STRONG',
                'description': 'Long lower wick at support = reversal'
            })
        
        # Inverted Hammer (bullish reversal)
        if (upper_wick > body * 2 and 
            lower_wick < body * 0.3 and
            last['close'] > last['open']):
            patterns.append({
                'name': 'INVERTED_HAMMER',
                'type': 'BULLISH',
                'strength': 'MODERATE',
                'description': 'Long upper wick, buying pressure building'
            })
        
        # Shooting Star (bearish reversal)
        if (upper_wick > body * 2 and 
            lower_wick < body * 0.3 and
            last['close'] < last['open']):
            patterns.append({
                'name': 'SHOOTING_STAR',
                'type': 'BEARISH',
                'strength': 'STRONG',
                'description': 'Rejection at resistance, sell pressure'
            })
        
        # Doji (indecision)
        if body < range_size * 0.1:
            patterns.append({
                'name': 'DOJI',
                'type': 'NEUTRAL',
                'strength': 'MODERATE',
                'description': 'Indecision, potential reversal'
            })
        
        # Bullish Engulfing
        if (last['close'] > last['open'] and 
            prev['close'] < prev['open'] and
            last['close'] > prev['open'] and 
            last['open'] < prev['close']):
            patterns.append({
                'name': 'BULLISH_ENGULFING',
                'type': 'BULLISH',
                'strength': 'VERY_STRONG',
                'description': 'Strong reversal, buyers took control'
            })
        
        # Bearish Engulfing
        if (last['close'] < last['open'] and 
            prev['close'] > prev['open'] and
            last['close'] < prev['open'] and 
            last['open'] > prev['close']):
            patterns.append({
                'name': 'BEARISH_ENGULFING',
                'type': 'BEARISH',
                'strength': 'VERY_STRONG',
                'description': 'Strong reversal, sellers took control'
            })
        
        # Determine overall signal
        bullish_count = sum(1 for p in patterns if p['type'] == 'BULLISH')
        bearish_count = sum(1 for p in patterns if p['type'] == 'BEARISH')
        
        if bullish_count > bearish_count:
            signal = 'BULLISH'
        elif bearish_count > bullish_count:
            signal = 'BEARISH'
        else:
            signal = 'NEUTRAL'
        
        return {
            'patterns': patterns,
            'signal': signal,
            'pattern_count': len(patterns)
        }
    
    @staticmethod
    def analyze_wicks(df: pd.DataFrame, support: float = None, resistance: float = None) -> Dict:
        """
        Analyze wick patterns for reversal signals
        Long lower wick at support = bullish
        Long upper wick at resistance = bearish
        """
        if len(df) < 1:
            return {'signal': 'NEUTRAL'}
        
        last = df.iloc[-1]
        
        body = abs(last['close'] - last['open'])
        range_size = last['high'] - last['low']
        upper_wick = last['high'] - max(last['open'], last['close'])
        lower_wick = min(last['open'], last['close']) - last['low']
        
        signals = []
        
        # Long lower wick (>60% of range)
        if lower_wick > range_size * 0.6:
            if support and abs(last['low'] - support) / support < 0.01:  # Within 1% of support
                signals.append({
                    'type': 'LONG_LOWER_WICK_AT_SUPPORT',
                    'signal': 'BULLISH',
                    'strength': 'VERY_STRONG',
                    'description': f'Long lower wick at support ${support:.6f} = strong buy'
                })
            else:
                signals.append({
                    'type': 'LONG_LOWER_WICK',
                    'signal': 'BULLISH',
                    'strength': 'MODERATE',
                    'description': 'Buyers defended lower prices'
                })
        
        # Long upper wick (>60% of range)
        if upper_wick > range_size * 0.6:
            if resistance and abs(last['high'] - resistance) / resistance < 0.01:  # Within 1% of resistance
                signals.append({
                    'type': 'LONG_UPPER_WICK_AT_RESISTANCE',
                    'signal': 'BEARISH',
                    'strength': 'VERY_STRONG',
                    'description': f'Rejection at resistance ${resistance:.6f} = sell pressure'
                })
            else:
                signals.append({
                    'type': 'LONG_UPPER_WICK',
                    'signal': 'BEARISH',
                    'strength': 'MODERATE',
                    'description': 'Sellers rejected higher prices'
                })
        
        # Determine overall signal
        bullish = sum(1 for s in signals if s['signal'] == 'BULLISH')
        bearish = sum(1 for s in signals if s['signal'] == 'BEARISH')
        
        return {
            'signals': signals,
            'signal': 'BULLISH' if bullish > bearish else 'BEARISH' if bearish > bullish else 'NEUTRAL',
            'lower_wick_pct': (lower_wick / range_size * 100) if range_size > 0 else 0,
            'upper_wick_pct': (upper_wick / range_size * 100) if range_size > 0 else 0
        }
    
    @staticmethod
    def multi_timeframe_confirmation(price_1m: float, price_5m: float, price_15m: float,
                                     ma_1m: float, ma_5m: float, ma_15m: float) -> Dict:
        """
        Check if all timeframes align (1m, 5m, 15m)
        Requires price above MA on all timeframes for bullish confirmation
        """
        bullish_1m = price_1m > ma_1m
        bullish_5m = price_5m > ma_5m
        bullish_15m = price_15m > ma_15m
        
        aligned = bullish_1m == bullish_5m == bullish_15m
        direction = 'BULLISH' if bullish_1m else 'BEARISH'
        
        if aligned:
            strength = 'STRONG' if direction == 'BULLISH' else 'WEAK'
        else:
            strength = 'MIXED'
            direction = 'NEUTRAL'
        
        return {
            'aligned': aligned,
            'direction': direction,
            'strength': strength,
            'timeframes': {
                '1m': 'BULLISH' if bullish_1m else 'BEARISH',
                '5m': 'BULLISH' if bullish_5m else 'BEARISH',
                '15m': 'BULLISH' if bullish_15m else 'BEARISH'
            },
            'confidence': 100 if aligned else 50
        }
    
    @staticmethod
    def ema_crossover(df: pd.DataFrame, fast_period: int = 9, slow_period: int = 21) -> Dict:
        """
        EMA 9/21 crossover detection
        Bullish: Fast crosses above slow
        Bearish: Fast crosses below slow
        """
        if len(df) < slow_period:
            return {'signal': 'NEUTRAL', 'crossover': False}
        
        # Calculate EMAs
        ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
        
        current_fast = ema_fast.iloc[-1]
        current_slow = ema_slow.iloc[-1]
        prev_fast = ema_fast.iloc[-2]
        prev_slow = ema_slow.iloc[-2]
        
        # Detect crossover
        bullish_cross = prev_fast <= prev_slow and current_fast > current_slow
        bearish_cross = prev_fast >= prev_slow and current_fast < current_slow
        
        # Determine trend
        trend = 'BULLISH' if current_fast > current_slow else 'BEARISH'
        distance_pct = abs((current_fast - current_slow) / current_slow * 100)
        
        return {
            'signal': 'BULLISH' if bullish_cross else 'BEARISH' if bearish_cross else 'NEUTRAL',
            'crossover': bullish_cross or bearish_cross,
            'crossover_type': 'GOLDEN_CROSS' if bullish_cross else 'DEATH_CROSS' if bearish_cross else 'NONE',
            'trend': trend,
            'ema_fast': current_fast,
            'ema_slow': current_slow,
            'distance_pct': distance_pct,
            'strength': 'STRONG' if distance_pct > 1 else 'MODERATE' if distance_pct > 0.5 else 'WEAK'
        }
    
    @staticmethod
    def bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict:
        """
        Bollinger Bands - Buy at lower band, sell at upper band
        """
        if len(df) < period:
            return {'signal': 'NEUTRAL'}
        
        # Calculate Bollinger Bands
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        current_price = df['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_sma = sma.iloc[-1]
        
        # Calculate position within bands
        band_width = current_upper - current_lower
        position_pct = ((current_price - current_lower) / band_width * 100) if band_width > 0 else 50
        
        # Detect touches/bounces
        near_lower = position_pct < 10  # Within 10% of lower band
        near_upper = position_pct > 90  # Within 10% of upper band
        at_middle = 40 < position_pct < 60
        
        # Generate signal
        if near_lower:
            signal = 'BULLISH'
            reason = 'Price at lower band, oversold, expect bounce'
            strength = 'STRONG'
        elif near_upper:
            signal = 'BEARISH'
            reason = 'Price at upper band, overbought, expect pullback'
            strength = 'STRONG'
        elif at_middle:
            signal = 'NEUTRAL'
            reason = 'Price at middle, no edge'
            strength = 'WEAK'
        else:
            signal = 'NEUTRAL'
            reason = 'Price in mid-range'
            strength = 'MODERATE'
        
        return {
            'signal': signal,
            'reason': reason,
            'strength': strength,
            'upper_band': current_upper,
            'lower_band': current_lower,
            'sma': current_sma,
            'current_price': current_price,
            'position_pct': position_pct,
            'band_width': band_width,
            'near_lower': near_lower,
            'near_upper': near_upper
        }
    
    @staticmethod
    def rsi_divergence(df: pd.DataFrame, period: int = 14) -> Dict:
        """
        RSI Divergence Detection
        Bullish: Price makes lower low, RSI makes higher low (reversal)
        Bearish: Price makes higher high, RSI makes lower high (reversal)
        """
        if len(df) < period + 10:
            return {'signal': 'NEUTRAL', 'divergence': False}
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Get recent price and RSI lows/highs (last 10 candles)
        recent_prices = df['close'].iloc[-10:]
        recent_rsi = rsi.iloc[-10:]
        
        # Find local minima and maxima
        price_lows = []
        rsi_lows = []
        price_highs = []
        rsi_highs = []
        
        for i in range(1, len(recent_prices) - 1):
            # Local low
            if recent_prices.iloc[i] < recent_prices.iloc[i-1] and recent_prices.iloc[i] < recent_prices.iloc[i+1]:
                price_lows.append(recent_prices.iloc[i])
                rsi_lows.append(recent_rsi.iloc[i])
            
            # Local high
            if recent_prices.iloc[i] > recent_prices.iloc[i-1] and recent_prices.iloc[i] > recent_prices.iloc[i+1]:
                price_highs.append(recent_prices.iloc[i])
                rsi_highs.append(recent_rsi.iloc[i])
        
        # Detect bullish divergence (price lower low, RSI higher low)
        bullish_div = False
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            if price_lows[-1] < price_lows[-2] and rsi_lows[-1] > rsi_lows[-2]:
                bullish_div = True
        
        # Detect bearish divergence (price higher high, RSI lower high)
        bearish_div = False
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            if price_highs[-1] > price_highs[-2] and rsi_highs[-1] < rsi_highs[-2]:
                bearish_div = True
        
        current_rsi = rsi.iloc[-1]
        
        # Determine signal
        if bullish_div:
            signal = 'BULLISH'
            reason = 'Bullish divergence: Price lower low, RSI higher low = reversal likely'
            strength = 'VERY_STRONG'
        elif bearish_div:
            signal = 'BEARISH'
            reason = 'Bearish divergence: Price higher high, RSI lower high = reversal likely'
            strength = 'VERY_STRONG'
        elif current_rsi < 30:
            signal = 'BULLISH'
            reason = 'RSI oversold (<30), bounce expected'
            strength = 'MODERATE'
        elif current_rsi > 70:
            signal = 'BEARISH'
            reason = 'RSI overbought (>70), pullback expected'
            strength = 'MODERATE'
        else:
            signal = 'NEUTRAL'
            reason = 'RSI in normal range'
            strength = 'WEAK'
        
        return {
            'signal': signal,
            'reason': reason,
            'strength': strength,
            'divergence': bullish_div or bearish_div,
            'divergence_type': 'BULLISH' if bullish_div else 'BEARISH' if bearish_div else 'NONE',
            'rsi': current_rsi,
            'oversold': current_rsi < 30,
            'overbought': current_rsi > 70
        }