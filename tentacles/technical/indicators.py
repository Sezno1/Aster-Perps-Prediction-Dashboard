"""
Technical indicators calculation module
"""

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from typing import Dict, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.config import *

class TechnicalIndicators:
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = RSI_PERIOD) -> pd.Series:
        """Calculate RSI indicator"""
        if df.empty:
            return pd.Series()
        rsi = RSIIndicator(close=df['close'], window=period)
        return rsi.rsi()
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        if df.empty:
            return pd.Series(), pd.Series(), pd.Series()
        macd = MACD(
            close=df['close'],
            window_fast=MACD_FAST,
            window_slow=MACD_SLOW,
            window_sign=MACD_SIGNAL
        )
        return macd.macd(), macd.macd_signal(), macd.macd_diff()
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        if df.empty:
            return pd.Series(), pd.Series()
        stoch = StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=STOCH_PERIOD,
            smooth_window=STOCH_SMOOTH
        )
        return stoch.stoch(), stoch.stoch_signal()
    
    @staticmethod
    def get_momentum_score(df_1h: pd.DataFrame, df_4h: pd.DataFrame) -> Dict:
        """Calculate momentum score from multiple indicators"""
        score = 0
        max_score = 100
        details = {}
        
        if df_1h.empty or df_4h.empty:
            return {'score': 0, 'details': {}, 'signals': []}
        
        rsi_1h = TechnicalIndicators.calculate_rsi(df_1h)
        rsi_4h = TechnicalIndicators.calculate_rsi(df_4h)
        
        macd_1h, macd_signal_1h, macd_hist_1h = TechnicalIndicators.calculate_macd(df_1h)
        macd_4h, macd_signal_4h, macd_hist_4h = TechnicalIndicators.calculate_macd(df_4h)
        
        stoch_1h, stoch_signal_1h = TechnicalIndicators.calculate_stochastic(df_1h)
        stoch_4h, stoch_signal_4h = TechnicalIndicators.calculate_stochastic(df_4h)
        
        signals = []
        
        if not rsi_1h.empty and not rsi_4h.empty:
            rsi_1h_val = rsi_1h.iloc[-1]
            rsi_4h_val = rsi_4h.iloc[-1]
            details['rsi_1h'] = round(rsi_1h_val, 2)
            details['rsi_4h'] = round(rsi_4h_val, 2)
            
            if RSI_BULLISH_ZONE[0] <= rsi_1h_val <= RSI_BULLISH_ZONE[1]:
                score += 15
                signals.append("RSI 1h in bullish zone")
            elif rsi_1h_val < RSI_OVERSOLD:
                score += 20
                signals.append("RSI 1h oversold - bounce potential")
            elif rsi_1h_val > RSI_OVERBOUGHT:
                score -= 20
                signals.append("⚠️ RSI 1h overbought")
            
            if RSI_BULLISH_ZONE[0] <= rsi_4h_val <= RSI_BULLISH_ZONE[1]:
                score += 15
                signals.append("RSI 4h in bullish zone")
        
        if not macd_hist_1h.empty and not macd_hist_4h.empty:
            macd_hist_1h_val = macd_hist_1h.iloc[-1]
            macd_hist_4h_val = macd_hist_4h.iloc[-1]
            details['macd_hist_1h'] = round(macd_hist_1h_val, 6)
            details['macd_hist_4h'] = round(macd_hist_4h_val, 6)
            
            if macd_hist_1h_val > 0:
                score += 20
                signals.append("MACD 1h bullish crossover")
            
            if macd_hist_4h_val > 0:
                score += 20
                signals.append("MACD 4h bullish crossover")
            
            if len(macd_hist_1h) >= 2:
                if macd_hist_1h.iloc[-2] < 0 and macd_hist_1h_val > 0:
                    score += 15
                    signals.append("🚀 MACD 1h fresh bullish cross")
        
        if not stoch_1h.empty and not stoch_signal_1h.empty:
            stoch_1h_val = stoch_1h.iloc[-1]
            stoch_signal_1h_val = stoch_signal_1h.iloc[-1]
            details['stoch_1h'] = round(stoch_1h_val, 2)
            
            if stoch_1h_val < STOCH_OVERSOLD and stoch_1h_val > stoch_signal_1h_val:
                score += 15
                signals.append("Stochastic oversold reversal")
        
        normalized_score = min(100, max(0, score))
        
        return {
            'score': normalized_score,
            'details': details,
            'signals': signals
        }
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame, period: int = 20) -> float:
        """Calculate price volatility (standard deviation of returns)"""
        if df.empty or len(df) < period:
            return 0.0
        returns = df['close'].pct_change()
        volatility = returns.std() * np.sqrt(period)
        return volatility
    
    @staticmethod
    def detect_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Dict:
        """Detect support and resistance levels"""
        if df.empty or len(df) < lookback:
            return {'support': None, 'resistance': None}
        
        recent_data = df.tail(lookback)
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()
        
        return {
            'support': support,
            'resistance': resistance
        }