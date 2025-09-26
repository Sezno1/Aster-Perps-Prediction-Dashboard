"""
Multi-Strategy Trading Engine
Always finds opportunities: scalping, momentum, dip-buying
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class MultiStrategyEngine:
    def __init__(self):
        self.strategies = ['scalping', 'momentum', 'dip_buying', 'breakout']
    
    def analyze_all_opportunities(self, market_data: Dict, signal_results: Dict, 
                                  orderflow_analysis: Dict) -> Dict:
        """
        ALWAYS find trading opportunities across multiple strategies
        Returns the best available entry for each strategy type
        """
        current_price = market_data['prices']['aster']
        df_1h = market_data['ohlcv']['aster_1h']
        df_4h = market_data['ohlcv']['aster_4h']
        
        opportunities = {
            'scalping': self._analyze_scalping(current_price, df_1h, orderflow_analysis),
            'momentum': self._analyze_momentum(current_price, df_1h, df_4h, signal_results),
            'dip_buying': self._analyze_dip_buying(current_price, df_1h, df_4h),
            'breakout': self._analyze_breakout(current_price, df_1h, orderflow_analysis)
        }
        
        best_opportunity = self._select_best_opportunity(opportunities)
        
        return {
            'all_opportunities': opportunities,
            'best_strategy': best_opportunity,
            'always_active': True
        }
    
    def _analyze_scalping(self, current_price: float, df: pd.DataFrame, 
                         orderflow: Dict) -> Dict:
        """
        Scalping: Quick 1-3% moves, high frequency
        Entry: Micro dips with reversal confirmation
        """
        if df.empty or len(df) < 5:
            return {'active': False, 'confidence': 0}
        
        recent = df.tail(5)
        
        price_range_5min = (recent['high'].max() - recent['low'].min()) / recent['close'].iloc[-1]
        
        rsi = self._quick_rsi(df, period=7)
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        imbalance = orderflow.get('imbalance_score', 0)
        
        is_micro_dip = (
            recent['close'].iloc[-1] < recent['close'].iloc[-3] and
            recent['close'].iloc[-1] > recent['low'].iloc[-1] * 1.002
        )
        
        has_reversal_signal = (
            imbalance > 10 or
            (current_rsi < 45 and rsi.iloc[-1] > rsi.iloc[-2])
        )
        
        confidence = 0
        if is_micro_dip:
            confidence += 30
        if has_reversal_signal:
            confidence += 25
        if imbalance > 20:
            confidence += 25
        if 30 < current_rsi < 50:
            confidence += 20
        
        target_profit = 0.015
        stop_loss_pct = 0.008
        
        entry_price = current_price * 0.998
        exit_price = entry_price * (1 + target_profit)
        stop_loss = entry_price * (1 - stop_loss_pct)
        
        return {
            'active': True,
            'strategy': 'SCALPING',
            'confidence': min(confidence, 100),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'leverage': 20 if confidence > 60 else 15,
            'target_profit_pct': target_profit * 100,
            'timeframe': '5-30 minutes',
            'reasoning': self._scalping_reasoning(is_micro_dip, has_reversal_signal, imbalance, current_rsi)
        }
    
    def _analyze_momentum(self, current_price: float, df_1h: pd.DataFrame, 
                         df_4h: pd.DataFrame, signal_results: Dict) -> Dict:
        """
        Momentum: Catch strong moves, 5-15% targets
        Entry: Breakout confirmations with volume
        """
        if df_1h.empty or len(df_1h) < 20:
            return {'active': False, 'confidence': 0}
        
        signal_score = signal_results['composite_score']
        
        rsi_1h = self._quick_rsi(df_1h, period=14).iloc[-1] if len(df_1h) >= 14 else 50
        
        recent_volume = df_1h['volume'].tail(5).mean()
        avg_volume = df_1h['volume'].tail(20).mean()
        volume_surge = recent_volume / avg_volume if avg_volume > 0 else 1
        
        price_momentum = ((df_1h['close'].iloc[-1] - df_1h['close'].iloc[-10]) / 
                         df_1h['close'].iloc[-10] * 100) if len(df_1h) >= 10 else 0
        
        is_strong_momentum = (
            price_momentum > 2 and
            volume_surge > 1.3 and
            rsi_1h > 50
        )
        
        confidence = 0
        if signal_score > 60:
            confidence += 30
        if is_strong_momentum:
            confidence += 35
        if volume_surge > 1.5:
            confidence += 20
        if rsi_1h > 55:
            confidence += 15
        
        target_profit = 0.08
        stop_loss_pct = 0.03
        
        entry_price = current_price * 1.002
        exit_price = entry_price * (1 + target_profit)
        stop_loss = entry_price * (1 - stop_loss_pct)
        
        return {
            'active': True,
            'strategy': 'MOMENTUM',
            'confidence': min(confidence, 100),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'leverage': 25 if confidence > 70 else 15,
            'target_profit_pct': target_profit * 100,
            'timeframe': '2-8 hours',
            'reasoning': self._momentum_reasoning(signal_score, is_strong_momentum, volume_surge, price_momentum)
        }
    
    def _analyze_dip_buying(self, current_price: float, df_1h: pd.DataFrame, 
                           df_4h: pd.DataFrame) -> Dict:
        """
        Dip Buying: Buy at bottom of dips for 3-8% bounce
        Entry: Oversold + support levels + reversal candles
        """
        if df_1h.empty or len(df_1h) < 20:
            return {'active': False, 'confidence': 0}
        
        rsi = self._quick_rsi(df_1h, period=14)
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        recent_5 = df_1h.tail(5)
        price_drop = ((recent_5['close'].iloc[-1] - recent_5['high'].max()) / 
                     recent_5['high'].max() * 100)
        
        is_green_candle = df_1h['close'].iloc[-1] > df_1h['open'].iloc[-1]
        
        support_level = df_1h['low'].tail(20).min()
        near_support = abs(current_price - support_level) / current_price < 0.015
        
        is_dip_bottom = (
            current_rsi < 40 and
            price_drop < -3 and
            is_green_candle
        )
        
        confidence = 0
        if current_rsi < 35:
            confidence += 40
        elif current_rsi < 45:
            confidence += 25
        
        if price_drop < -5:
            confidence += 30
        elif price_drop < -3:
            confidence += 20
        
        if is_green_candle:
            confidence += 15
        
        if near_support:
            confidence += 15
        
        target_profit = 0.05
        stop_loss_pct = 0.025
        
        entry_price = current_price * 0.995
        exit_price = entry_price * (1 + target_profit)
        stop_loss = support_level * 0.995
        
        return {
            'active': True,
            'strategy': 'DIP_BUYING',
            'confidence': min(confidence, 100),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'leverage': 20 if confidence > 65 else 12,
            'target_profit_pct': target_profit * 100,
            'timeframe': '1-4 hours',
            'reasoning': self._dip_buying_reasoning(current_rsi, price_drop, is_green_candle, near_support)
        }
    
    def _analyze_breakout(self, current_price: float, df: pd.DataFrame, 
                         orderflow: Dict) -> Dict:
        """
        Breakout: Price breaking resistance, targeting 10-20%
        Entry: Volume confirmation + strong orderflow
        """
        if df.empty or len(df) < 20:
            return {'active': False, 'confidence': 0}
        
        recent_high = df['high'].tail(20).max()
        near_breakout = current_price >= recent_high * 0.995
        
        volume_surge = df['volume'].iloc[-1] / df['volume'].tail(10).mean() if df['volume'].tail(10).mean() > 0 else 1
        
        imbalance = orderflow.get('imbalance_score', 0)
        
        bid_ask_ratio = orderflow.get('bid_ask_metrics', {}).get('bid_ask_ratio', 1)
        
        is_breakout_setup = (
            near_breakout and
            volume_surge > 1.4 and
            imbalance > 15
        )
        
        confidence = 0
        if near_breakout:
            confidence += 35
        if volume_surge > 1.8:
            confidence += 30
        elif volume_surge > 1.4:
            confidence += 20
        if imbalance > 20:
            confidence += 25
        if bid_ask_ratio > 1.2:
            confidence += 10
        
        target_profit = 0.12
        stop_loss_pct = 0.04
        
        entry_price = recent_high * 1.001
        exit_price = entry_price * (1 + target_profit)
        stop_loss = entry_price * (1 - stop_loss_pct)
        
        return {
            'active': True,
            'strategy': 'BREAKOUT',
            'confidence': min(confidence, 100),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'leverage': 30 if confidence > 75 else 20,
            'target_profit_pct': target_profit * 100,
            'timeframe': '4-24 hours',
            'reasoning': self._breakout_reasoning(near_breakout, volume_surge, imbalance, is_breakout_setup)
        }
    
    def _select_best_opportunity(self, opportunities: Dict) -> Dict:
        """Select the best opportunity from all strategies"""
        best = None
        best_score = 0
        
        for strategy_name, opp in opportunities.items():
            if opp.get('active') and opp.get('confidence', 0) > best_score:
                best_score = opp['confidence']
                best = opp.copy()
                best['strategy_name'] = strategy_name
        
        if not best:
            return opportunities['scalping']
        
        return best
    
    def _quick_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI quickly"""
        if len(df) < period + 1:
            return pd.Series([50] * len(df))
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50)
    
    def _scalping_reasoning(self, is_dip, has_reversal, imbalance, rsi):
        reasons = []
        if is_dip:
            reasons.append("Micro-dip detected")
        if has_reversal:
            reasons.append("Reversal signal confirmed")
        if imbalance > 20:
            reasons.append(f"Strong buy pressure ({imbalance:.0f})")
        if 30 < rsi < 50:
            reasons.append(f"RSI oversold recovery ({rsi:.0f})")
        return " • ".join(reasons) if reasons else "Small profit opportunity"
    
    def _momentum_reasoning(self, signal, is_strong, volume, momentum):
        reasons = []
        if signal > 70:
            reasons.append(f"Strong technical signal ({signal:.0f})")
        if is_strong:
            reasons.append(f"Momentum building (+{momentum:.1f}%)")
        if volume > 1.5:
            reasons.append(f"Volume surge ({volume:.1f}x)")
        return " • ".join(reasons) if reasons else "Momentum opportunity"
    
    def _dip_buying_reasoning(self, rsi, drop, green_candle, support):
        reasons = []
        if rsi < 35:
            reasons.append(f"Heavily oversold (RSI {rsi:.0f})")
        elif rsi < 45:
            reasons.append(f"Oversold (RSI {rsi:.0f})")
        if drop < -5:
            reasons.append(f"Deep dip ({drop:.1f}%)")
        if green_candle:
            reasons.append("Reversal candle formed")
        if support:
            reasons.append("Near strong support")
        return " • ".join(reasons) if reasons else "Dip-buying opportunity"
    
    def _breakout_reasoning(self, near_break, volume, imbalance, setup):
        reasons = []
        if near_break:
            reasons.append("At resistance level")
        if volume > 1.8:
            reasons.append(f"Huge volume ({volume:.1f}x)")
        elif volume > 1.4:
            reasons.append(f"High volume ({volume:.1f}x)")
        if imbalance > 20:
            reasons.append(f"Strong buying ({imbalance:.0f})")
        if setup:
            reasons.append("Breakout imminent")
        return " • ".join(reasons) if reasons else "Breakout opportunity"