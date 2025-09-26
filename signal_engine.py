"""
Signal scoring and recommendation engine
"""

from typing import Dict, Tuple, Optional
import config
from indicators import TechnicalIndicators

class SignalEngine:
    
    @staticmethod
    def score_perp_metrics(perp_data: Dict) -> Dict:
        """Score perpetual futures metrics"""
        score = 0
        signals = []
        
        aster_funding = perp_data.get('aster_funding')
        btc_funding = perp_data.get('btc_funding')
        aster_oi = perp_data.get('aster_oi')
        
        if aster_funding is not None:
            if aster_funding < 0:
                score += 40
                signals.append(f"🔥 Negative funding rate: {aster_funding*100:.4f}% (shorts paying longs)")
            elif aster_funding < 0.01:
                score += 20
                signals.append(f"Low funding rate: {aster_funding*100:.4f}%")
            elif aster_funding > 0.05:
                score -= 30
                signals.append(f"⚠️ High funding rate: {aster_funding*100:.4f}% (overleveraged longs)")
            else:
                score += 10
        else:
            if btc_funding is not None:
                if btc_funding < 0:
                    score += 20
                    signals.append(f"BTC funding negative: {btc_funding*100:.4f}%")
                elif btc_funding > 0.05:
                    score -= 15
        
        if aster_oi:
            score += 10
            signals.append(f"Open interest: ${aster_oi:,.0f}")
        
        normalized_score = min(100, max(0, score))
        
        return {
            'score': normalized_score,
            'signals': signals,
            'details': {
                'aster_funding': f"{aster_funding*100:.4f}%" if aster_funding else "N/A",
                'btc_funding': f"{btc_funding*100:.4f}%" if btc_funding else "N/A",
                'aster_oi': f"${aster_oi:,.0f}" if aster_oi else "N/A"
            }
        }
    
    @staticmethod
    def score_market_context(market_data: Dict, btc_1h, btc_4h) -> Dict:
        """Score market context (BTC/ETH correlation)"""
        score = 0
        signals = []
        
        eth_btc_ratio = market_data.get('eth_btc_ratio')
        btc_dominance = market_data.get('btc_dominance')
        
        if not btc_1h.empty:
            btc_rsi_1h = TechnicalIndicators.calculate_rsi(btc_1h)
            if not btc_rsi_1h.empty:
                btc_rsi_val = btc_rsi_1h.iloc[-1]
                if btc_rsi_val > 50:
                    score += 25
                    signals.append(f"BTC bullish (RSI: {btc_rsi_val:.1f})")
                elif btc_rsi_val < 40:
                    score -= 15
                    signals.append(f"⚠️ BTC weak (RSI: {btc_rsi_val:.1f})")
        
        if eth_btc_ratio:
            score += 20
            signals.append(f"ETH/BTC ratio: {eth_btc_ratio:.6f}")
        
        if btc_dominance:
            if btc_dominance < 55:
                score += 25
                signals.append(f"🚀 Low BTC dominance: {btc_dominance:.1f}% (altseason)")
            elif btc_dominance > 60:
                score -= 20
                signals.append(f"⚠️ High BTC dominance: {btc_dominance:.1f}%")
            else:
                score += 10
        
        normalized_score = min(100, max(0, score))
        
        return {
            'score': normalized_score,
            'signals': signals,
            'details': {
                'eth_btc_ratio': f"{eth_btc_ratio:.6f}" if eth_btc_ratio else "N/A",
                'btc_dominance': f"{btc_dominance:.2f}%" if btc_dominance else "N/A"
            }
        }
    
    @staticmethod
    def score_sentiment(sentiment_data: Dict) -> Dict:
        """Score market sentiment"""
        score = 50
        signals = []
        
        if sentiment_data:
            fg_value = sentiment_data.get('value')
            fg_class = sentiment_data.get('classification')
            
            if fg_value:
                if fg_value < 25:
                    score = 80
                    signals.append(f"🔥 Extreme Fear ({fg_value}) - buy opportunity")
                elif fg_value < 45:
                    score = 70
                    signals.append(f"Fear ({fg_value}) - good entry zone")
                elif fg_value > 75:
                    score = 20
                    signals.append(f"⚠️ Extreme Greed ({fg_value}) - risky")
                else:
                    score = 50
                    signals.append(f"Neutral sentiment ({fg_value})")
        else:
            signals.append("Sentiment data unavailable")
        
        return {
            'score': score,
            'signals': signals,
            'details': sentiment_data if sentiment_data else {}
        }
    
    @staticmethod
    def calculate_composite_score(momentum_result: Dict, perp_result: Dict, 
                                 market_result: Dict, sentiment_result: Dict) -> Dict:
        """Calculate weighted composite signal score"""
        
        momentum_score = momentum_result['score']
        perp_score = perp_result['score']
        market_score = market_result['score']
        sentiment_score = sentiment_result['score']
        
        composite = (
            momentum_score * config.SIGNAL_WEIGHTS['momentum'] +
            perp_score * config.SIGNAL_WEIGHTS['perp_metrics'] +
            market_score * config.SIGNAL_WEIGHTS['market_context'] +
            sentiment_score * config.SIGNAL_WEIGHTS['sentiment']
        )
        
        leverage_rec = SignalEngine.get_leverage_recommendation(composite)
        action = SignalEngine.get_action_recommendation(composite)
        
        all_signals = (
            momentum_result.get('signals', []) +
            perp_result.get('signals', []) +
            market_result.get('signals', []) +
            sentiment_result.get('signals', [])
        )
        
        return {
            'composite_score': round(composite, 1),
            'momentum_score': round(momentum_score, 1),
            'perp_score': round(perp_score, 1),
            'market_score': round(market_score, 1),
            'sentiment_score': round(sentiment_score, 1),
            'leverage_recommendation': leverage_rec,
            'action': action,
            'signals': all_signals,
            'breakdown': {
                'momentum': momentum_result,
                'perp': perp_result,
                'market': market_result,
                'sentiment': sentiment_result
            }
        }
    
    @staticmethod
    def get_leverage_recommendation(score: float) -> str:
        """Get leverage recommendation based on score"""
        for key, (min_score, max_score, rec) in config.LEVERAGE_RECOMMENDATIONS.items():
            if min_score <= score <= max_score:
                return rec
        return "WAIT"
    
    @staticmethod
    def get_action_recommendation(score: float) -> str:
        """Get action recommendation"""
        if score >= 80:
            return "🚀 STRONG LONG"
        elif score >= 60:
            return "📈 MODERATE LONG"
        elif score >= 40:
            return "⚠️ WEAK SIGNAL - Consider waiting"
        else:
            return "🛑 NO ENTRY - Wait for better setup"
    
    @staticmethod
    def calculate_stop_loss(current_price: float, df, 
                           atr_multiplier: float = 2.0) -> Tuple[Optional[float], Optional[float]]:
        """Calculate suggested stop loss level"""
        if df.empty or not current_price:
            return None, None
        
        levels = TechnicalIndicators.detect_support_resistance(df)
        support = levels.get('support')
        
        recent_low = df['low'].tail(20).min()
        
        stop_loss = min(support, recent_low) if support else recent_low
        
        stop_loss = stop_loss * 0.98
        
        risk_percent = ((current_price - stop_loss) / current_price) * 100
        
        return stop_loss, risk_percent