"""
AI-Powered Market Analysis using OpenAI
Provides intelligent entry/exit recommendations
"""

from openai import OpenAI
from typing import Dict, Optional
import json
from datetime import datetime
import config

class AIAnalyzer:
    def __init__(self, api_key: Optional[str] = None, trade_journal=None, prediction_tracker=None):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.trade_journal = trade_journal
        self.prediction_tracker = prediction_tracker
        self.learning_context = self._load_learning_context()
    
    def analyze_market_conditions(self, market_data: Dict, signal_results: Dict, 
                                  orderflow_analysis: Dict, whale_sentiment: Dict,
                                  historical_context: Dict = None) -> Dict:
        """
        Use AI to analyze all market data and provide clear entry/exit recommendations
        Learns from past trade performance to improve over time
        """
        if not self.client:
            return self._fallback_analysis(signal_results, orderflow_analysis, whale_sentiment)
        
        try:
            prompt = self._build_analysis_prompt(market_data, signal_results, 
                                                 orderflow_analysis, whale_sentiment, historical_context)
            
            system_prompt = self._build_system_prompt_with_learning()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            ai_response = response.choices[0].message.content
            analysis = json.loads(ai_response)
            
            return {
                'recommendation': analysis.get('recommendation', 'WAIT'),
                'entry_price': analysis.get('entry_price'),
                'exit_price': analysis.get('exit_price'),
                'stop_loss': analysis.get('stop_loss'),
                'leverage': analysis.get('leverage', 10),
                'confidence': analysis.get('confidence', 50),
                'reasoning': analysis.get('reasoning', ''),
                'key_factors': analysis.get('key_factors', []),
                'timeframe': analysis.get('timeframe', 'Short-term (1-24h)'),
                'risk_level': analysis.get('risk_level', 'MEDIUM'),
                'ai_powered': True
            }
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_analysis(signal_results, orderflow_analysis, whale_sentiment)
    
    def _build_analysis_prompt(self, market_data: Dict, signal_results: Dict,
                               orderflow_analysis: Dict, whale_sentiment: Dict,
                               historical_context: Dict = None) -> str:
        """Build comprehensive prompt for AI analysis"""
        
        current_price = market_data['prices']['aster']
        btc_price = market_data['prices']['btc']
        funding_rate = market_data['perp_metrics'].get('aster_funding', 0)
        
        # Extract historical context
        if not historical_context:
            historical_context = {}
        volume_trend = historical_context.get('volume_trend', {})
        moon_candle = historical_context.get('moon_candle', {})
        dip_opportunity = historical_context.get('dip_opportunity', {})
        support_resistance = historical_context.get('support_resistance', {})
        recent_patterns = historical_context.get('recent_patterns', {})
        pattern_summary = historical_context.get('pattern_summary', '')
        whale_analysis = historical_context.get('whale_analysis', {})
        
        orderflow_direction = orderflow_analysis.get('prediction', {}).get('direction', 'NEUTRAL')
        orderflow_confidence = orderflow_analysis.get('prediction', {}).get('confidence', 0)
        imbalance = orderflow_analysis.get('imbalance_score', 0)
        
        whale_sent = whale_sentiment.get('sentiment', 'NEUTRAL')
        whale_score = whale_sentiment.get('score', 50)
        
        prompt = f"""Analyze ASTER/USDT perpetual futures and provide trading recommendation:

CURRENT MARKET DATA:
- ASTER Price: ${current_price:.6f}
- BTC Price: ${btc_price:,.2f}
- 24h Change: {market_data['perp_metrics'].get('aster_ticker_24h', {}).get('price_change_percent', 0):.2f}%
- Funding Rate: {funding_rate:.4f}% (negative = longs pay shorts, bullish for longs)

TECHNICAL SIGNALS (0-100 scale):
- Overall Signal Strength: {signal_results['composite_score']:.1f}/100
- Momentum Score: {signal_results['momentum_score']:.1f}/100
- Perp Metrics Score: {signal_results['perp_score']:.1f}/100
- Market Context: {signal_results['market_score']:.1f}/100
- Current Recommendation: {signal_results['action']}

ORDERFLOW ANALYSIS (1-15 min prediction):
- Direction: {orderflow_direction}
- Confidence: {orderflow_confidence:.0f}%
- Order Imbalance: {imbalance:.1f} (positive = buy pressure)
- Bid/Ask Ratio: {orderflow_analysis.get('bid_ask_metrics', {}).get('bid_ask_ratio', 1):.2f}

WHALE SENTIMENT:
- Sentiment: {whale_sent}
- Score: {whale_score:.0f}/100
- Top Traders Win Rate: {whale_sentiment.get('avg_win_rate', 0):.1f}%

HISTORICAL DATA ANALYSIS:
- Volume Trend (5m vs 1h): {volume_trend.get('trend', 'UNKNOWN')}
- Volume Spike Detected: {volume_trend.get('spike_detected', False)} ({volume_trend.get('multiplier', 0):.1f}x average)
- Support Level (24h): ${support_resistance.get('support', 0):.6f} ({support_resistance.get('support_tests', 0)} tests)
- Resistance Level (24h): ${support_resistance.get('resistance', 0):.6f} ({support_resistance.get('resistance_tests', 0)} tests)
- Moon Candle Alert: {moon_candle.get('type', 'NONE') if moon_candle and moon_candle.get('detected') else 'NONE'}
- 🎯 DIP OPPORTUNITY: {dip_opportunity.get('signal', 'NONE') if dip_opportunity and dip_opportunity.get('detected') else 'NO_DIP'}

PATTERN RECOGNITION (Last 24h):
- Recent Trend: {recent_patterns.get('trend', 'UNKNOWN')} ({recent_patterns.get('price_change_1h', 0):.2f}% last hour)
- Volatility: {recent_patterns.get('volatility', 'UNKNOWN')} ({recent_patterns.get('volatility_pct', 0):.2f}%)
- Moon Candles Detected: {recent_patterns.get('moon_candles_24h', 0)}
- Pumps Detected: {recent_patterns.get('pumps_24h', 0)}
- Dumps Detected: {recent_patterns.get('dumps_24h', 0)}

WHALE ACTIVITY (Real-time trades):
- 🐋 Whale Detected: {whale_analysis.get('whale_detected', False)}
- Whale Buys: {len(whale_analysis.get('whale_buys', []))} (>${whale_analysis.get('whale_threshold', 5000)})
- Whale Sells: {len(whale_analysis.get('whale_sells', []))} 
- Buy Pressure: {whale_analysis.get('buy_pressure_pct', 0):.1f}% ({whale_analysis.get('whale_signal', 'NEUTRAL')})
- Net Volume: ${whale_analysis.get('net_buy_pressure', 0):,.0f}

LEARNED INSIGHTS: {pattern_summary}

PROVIDE JSON RESPONSE:
{{
    "recommendation": "BUY_NOW" or "WAIT" or "NO_TRADE",
    "entry_price": (suggested entry price in float),
    "exit_price": (target exit price in float),
    "stop_loss": (stop loss price in float),
    "leverage": (recommended 1-50),
    "confidence": (0-100),
    "reasoning": "2-3 sentence explanation",
    "key_factors": ["factor1", "factor2", "factor3"],
    "timeframe": "Short-term (1-24h)" or "Medium-term (1-3 days)",
    "risk_level": "LOW" or "MEDIUM" or "HIGH"
}}

Consider:
1. Signal strength > 70 = potential entry
2. Orderflow direction alignment
3. Whale sentiment confirmation
4. Funding rate (negative is bullish for longs)
5. Risk:reward ratio should be at least 1:2
6. Volume spike (>2x) = increased volatility, higher profit potential
7. Moon candle detection = strong momentum, consider higher leverage (30-40x)
8. Price near support = good entry, near resistance = take profit
9. Entry at support with volume spike = ideal scalp setup
10. HIGH volatility (>1%) = good for scalping with 20-30x leverage
11. LOW volatility (<0.5%) = wait for breakout or reduce leverage to 10-15x
12. Multiple moon candles in 24h = sustained momentum, aggressive entries OK
13. BULLISH trend + volume spike + near support = STRONG BUY signal
14. 🎯 **DIP_BOUNCE detected = STRONG BUY** - price just bounced from dip, likely to continue up
15. Buy dips aggressively when: dip >0.3% + bounce >0.2% + near support = BEST ENTRY
16. 🐋 **Whale buys + BULLISH signal = VERY STRONG BUY** - follow the whales
17. Multiple whale buys (>2) + positive buy pressure (>20%) = institutional interest, aggressive entry
18. Whale sells (>2) + negative buy pressure (<-20%) = distribution, WAIT or reduce size
"""
        
        return prompt
    
    def _fallback_analysis(self, signal_results: Dict, orderflow_analysis: Dict, 
                          whale_sentiment: Dict) -> Dict:
        """Fallback rule-based analysis when AI unavailable"""
        
        composite_score = signal_results['composite_score']
        orderflow_direction = orderflow_analysis.get('prediction', {}).get('direction', 'NEUTRAL')
        whale_score = whale_sentiment.get('score', 50)
        
        confidence = (composite_score + whale_score) / 2
        
        recommendation = "WAIT"
        leverage = 10
        reasoning = []
        
        if composite_score >= 75 and orderflow_direction == "BULLISH" and whale_score >= 60:
            recommendation = "BUY_NOW"
            leverage = 20
            reasoning.append("Strong technical signals aligned with bullish orderflow")
            reasoning.append("Whale sentiment is positive")
        elif composite_score >= 60 and orderflow_direction in ["BULLISH", "NEUTRAL"]:
            recommendation = "BUY_NOW"
            leverage = 10
            reasoning.append("Moderate signal strength with acceptable risk")
        else:
            recommendation = "WAIT"
            reasoning.append("Signals not strong enough for entry")
            if composite_score < 50:
                reasoning.append("Technical indicators show weakness")
            if orderflow_direction == "BEARISH":
                reasoning.append("Orderflow shows selling pressure")
        
        return {
            'recommendation': recommendation,
            'entry_price': None,
            'exit_price': None,
            'stop_loss': None,
            'leverage': leverage,
            'confidence': confidence,
            'reasoning': " ".join(reasoning),
            'key_factors': [
                f"Signal: {composite_score:.0f}/100",
                f"Orderflow: {orderflow_direction}",
                f"Whales: {whale_score:.0f}/100"
            ],
            'timeframe': 'Short-term (1-24h)',
            'risk_level': 'MEDIUM' if confidence > 60 else 'HIGH',
            'ai_powered': False
        }
    
    def _load_learning_context(self) -> Dict:
        """Load learning insights from past trades"""
        if not self.trade_journal:
            return {}
        
        try:
            perf_stats = self.trade_journal.get_performance_stats()
            
            if perf_stats['total_trades'] < 5:
                return {}
            
            winning_trades, best_conditions = self.trade_journal.analyze_best_conditions()
            
            return {
                'total_trades': perf_stats['total_trades'],
                'win_rate': perf_stats['win_rate'],
                'avg_roi': perf_stats['avg_roi'],
                'profit_factor': perf_stats.get('profit_factor', 1),
                'best_conditions': best_conditions if best_conditions else {},
                'has_learning_data': True
            }
        except:
            return {}
    
    def _build_system_prompt_with_learning(self) -> str:
        """Build system prompt that includes learning from past performance"""
        
        base_prompt = """You are an expert crypto trading analyst specializing in ASTER perpetual futures. 
Analyze market data and provide clear, actionable trading decisions. 
Be direct and confident. Focus on entry price, exit price, stop loss, and recommended leverage.
Consider: technical indicators, orderflow, whale activity, and market sentiment.
Output valid JSON only."""
        
        self_learning_context = ""
        if self.prediction_tracker:
            self_learning_context = self.prediction_tracker.generate_ai_learning_context()
        
        if self_learning_context:
            return base_prompt + "\n\n" + self_learning_context
        
        if not self.learning_context or not self.learning_context.get('has_learning_data'):
            return base_prompt
        
        learning_section = f"""

LEARNING FROM PAST PERFORMANCE:
You have analyzed {self.learning_context['total_trades']} trades with the following results:
- Win Rate: {self.learning_context['win_rate']:.1f}%
- Average ROI: {self.learning_context['avg_roi']:.1f}%
- Profit Factor: {self.learning_context['profit_factor']:.2f}
"""
        
        if self.learning_context.get('best_conditions'):
            best = self.learning_context['best_conditions']
            learning_section += f"""
PATTERNS THAT WORKED BEST:
- Signal Score: {best.get('avg_signal_score', 0):.0f}/100
- Best Leverage: {best.get('best_leverage', 10)}x
- Avg Funding Rate: {best.get('avg_funding_rate', 0):.4f}%

ADJUST YOUR RECOMMENDATIONS based on these learned patterns. 
If current conditions match successful past trades, increase confidence.
If conditions match failed trades, be more conservative."""
        
        if self.learning_context['win_rate'] < 50:
            learning_section += """

IMPORTANT: Recent win rate is below 50%. Be MORE CONSERVATIVE:
- Only recommend BUY when signal strength > 80
- Use lower leverage
- Wider stop losses"""
        elif self.learning_context['win_rate'] > 70:
            learning_section += """

POSITIVE: Recent win rate is strong. Current strategy is working well.
Continue with similar approach but don't become overconfident."""
        
        return base_prompt + learning_section
    
    def update_learning_from_trade(self, trade_outcome: Dict):
        """Update learning context when a trade completes"""
        if self.trade_journal:
            self.learning_context = self._load_learning_context()
    
    def get_learning_summary(self) -> str:
        """Get human-readable learning summary"""
        if not self.learning_context or not self.learning_context.get('has_learning_data'):
            return "🆕 No trade history yet - AI will learn from your trades!"
        
        trades = self.learning_context['total_trades']
        win_rate = self.learning_context['win_rate']
        avg_roi = self.learning_context['avg_roi']
        
        performance_emoji = "🟢" if win_rate >= 60 else "🟡" if win_rate >= 50 else "🔴"
        
        summary = f"""{performance_emoji} **AI Learning Active**
- Learned from: {trades} trades
- Win Rate: {win_rate:.1f}%
- Avg ROI: {avg_roi:.1f}%

AI is adapting recommendations based on your trading history."""
        
        return summary