"""
AI-Powered Market Analysis using OpenAI
Provides intelligent entry/exit recommendations
"""

from openai import OpenAI
from typing import Dict, Optional
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import *

# Import universal pattern discovery
try:
    from tentacles.pattern_analysis.universal_pattern_discovery import universal_discovery
    UNIVERSAL_PATTERNS_AVAILABLE = True
except ImportError:
    UNIVERSAL_PATTERNS_AVAILABLE = False

# Import astrological intelligence
try:
    from tentacles.astrological.crypto_astrology import crypto_astrology
    from tentacles.astrological.astro_knowledge import astro_knowledge
    ASTROLOGICAL_INTELLIGENCE_AVAILABLE = True
except ImportError:
    ASTROLOGICAL_INTELLIGENCE_AVAILABLE = False

# Import perfect hindsight intelligence
try:
    from tentacles.intelligence.perfect_hindsight_engine import perfect_hindsight
    PERFECT_HINDSIGHT_AVAILABLE = True
except ImportError:
    PERFECT_HINDSIGHT_AVAILABLE = False

class AIAnalyzer:
    def __init__(self, api_key: Optional[str] = None, trade_journal=None, prediction_tracker=None):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.trade_journal = trade_journal
        self.prediction_tracker = prediction_tracker
        self.learning_context = self._load_learning_context()
    
    def get_universal_pattern_analysis(self, market_data: Dict) -> Dict:
        """Get universal pattern analysis from BTC/ETH learned patterns"""
        if not UNIVERSAL_PATTERNS_AVAILABLE:
            return {}
        
        try:
            # Create current market state from ASTER data
            current_state = {
                'rsi': market_data.get('rsi', 50),
                'volume_ratio': market_data.get('volume_24h_change_pct', 0) / 100 + 1,
                'bb_position': 0.5,  # Would need to calculate from actual BB data
                'price_vs_ema20': 1.0,  # Would need actual EMA calculation
                'price_vs_support': 1.0,  # Would need support level calculation
                'recent_volatility': abs(market_data.get('price_change_pct', 0)),
                'trend_direction': 1 if market_data.get('price_change_pct', 0) > 0 else 0,
                'volume_spike': 1 if market_data.get('volume_24h_change_pct', 0) > 100 else 0
            }
            
            # Apply patterns to current state
            pattern_matches = universal_discovery.apply_patterns_to_aster(current_state)
            
            if pattern_matches:
                best_pattern = pattern_matches[0]
                return {
                    'universal_pattern_available': True,
                    'pattern_name': best_pattern['pattern_name'],
                    'pattern_confidence': best_pattern['confidence_score'],
                    'expected_win_rate': best_pattern['expected_win_rate'] * 100,
                    'expected_profit': best_pattern['expected_profit'],
                    'pattern_recommendation': best_pattern['recommendation'],
                    'coins_validated': len(best_pattern['coins_validated']),
                    'all_matches': len(pattern_matches)
                }
            else:
                return {'universal_pattern_available': False}
                
        except Exception as e:
            print(f"Universal pattern analysis error: {e}")
            return {'universal_pattern_available': False}

    def get_perfect_hindsight_analysis(self, current_conditions: Dict) -> Dict:
        """Get perfect hindsight pattern matching for current market conditions"""
        if not PERFECT_HINDSIGHT_AVAILABLE:
            return {}
        
        try:
            # Match current conditions against discovered winning patterns
            pattern_matches = perfect_hindsight.get_current_pattern_matches(current_conditions)
            
            if pattern_matches:
                best_match = pattern_matches[0]
                
                # Get summary of perfect hindsight knowledge
                summary = perfect_hindsight.get_perfect_hindsight_summary()
                
                return {
                    'hindsight_available': True,
                    'best_pattern_match': best_match['pattern_name'],
                    'match_confidence': best_match['match_score'] * 100,
                    'expected_profit': best_match['expected_profit'],
                    'pattern_win_rate': best_match['win_rate'],
                    'total_matches': len(pattern_matches),
                    'hindsight_summary': summary,
                    'pattern_signature': best_match['signature'],
                    'recommendation_strength': 'VERY_HIGH' if best_match['match_score'] > 0.9 else 'HIGH' if best_match['match_score'] > 0.8 else 'MEDIUM'
                }
            else:
                return {
                    'hindsight_available': True,
                    'pattern_matches': 0,
                    'recommendation': 'No strong historical patterns match current conditions'
                }
                
        except Exception as e:
            print(f"Perfect hindsight analysis error: {e}")
            return {'hindsight_available': False}

    def get_astrological_analysis(self, symbol: str = 'ASTER') -> Dict:
        """Get comprehensive astrological analysis for trading decisions"""
        if not ASTROLOGICAL_INTELLIGENCE_AVAILABLE:
            return {}
        
        try:
            # Get current astrological recommendation
            astro_recommendation = crypto_astrology.get_current_astro_recommendation(symbol)
            
            # Get astrological training text for AI context
            training_text = astro_knowledge.generate_ai_training_text()
            
            return {
                'astrological_available': True,
                'recommendation': astro_recommendation['astrological_recommendation'],
                'confidence': astro_recommendation['confidence'],
                'reasoning': astro_recommendation['reasoning'],
                'lunar_phase': astro_recommendation['lunar_influence']['phase'],
                'lunar_tendency': astro_recommendation['lunar_influence']['tendency'],
                'lunar_strategy': astro_recommendation['lunar_influence']['strategy'],
                'volatility_indicator': astro_recommendation['volatility_indicator'],
                'market_tendency': astro_recommendation['market_tendency'],
                'timing_factors': astro_recommendation['timing_factors'],
                'transit_impact': astro_recommendation['transit_summary'].get('overall_impact', 'UNKNOWN'),
                'astrological_training': training_text[:2000]  # First 2000 chars for context
            }
            
        except Exception as e:
            print(f"Astrological analysis error: {e}")
            return {'astrological_available': False}

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
            # Get universal pattern analysis
            universal_patterns = self.get_universal_pattern_analysis(market_data)
            
            # Get astrological analysis
            astrological_analysis = self.get_astrological_analysis('ASTER')
            
            # Get perfect hindsight analysis
            perfect_hindsight_analysis = self.get_perfect_hindsight_analysis(historical_context or {})
            
            prompt = self._build_analysis_prompt(market_data, signal_results, 
                                                 orderflow_analysis, whale_sentiment, historical_context, universal_patterns, astrological_analysis, perfect_hindsight_analysis)
            
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
                               historical_context: Dict = None, universal_patterns: Dict = None, astrological_analysis: Dict = None, perfect_hindsight_analysis: Dict = None) -> str:
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
        
        # Build universal patterns section
        if universal_patterns and universal_patterns.get('universal_pattern_available'):
            universal_patterns_section = f"""
✅ UNIVERSAL PATTERN MATCH FOUND!
Pattern: {universal_patterns['pattern_name']}
Confidence: {universal_patterns['pattern_confidence']:.1f}% (validated on {universal_patterns['coins_validated']} coins)
Expected Win Rate: {universal_patterns['expected_win_rate']:.1f}%
Expected Profit: {universal_patterns['expected_profit']:.1f}%
AI Recommendation: {universal_patterns['pattern_recommendation']}

🚀 THIS IS A PROVEN PATTERN! Discovered from {universal_patterns['all_matches']} total matches.
This pattern was learned from analyzing BTC/ETH historical data across ALL market conditions.
When this pattern appears, it historically produces {universal_patterns['expected_win_rate']:.1f}% win rate.

USAGE: Increase position size by 2-3x and add +25 to confidence score.
"""
        else:
            universal_patterns_section = "⚠️ No Universal Pattern Match - Use standard analysis"
        
        # Build astrological analysis section
        if astrological_analysis and astrological_analysis.get('astrological_available'):
            astrological_section = f"""
🔮 ASTROLOGICAL INTELLIGENCE (ANCIENT WISDOM + MODERN FINANCIAL ASTROLOGY):
✨ CURRENT ASTROLOGICAL RECOMMENDATION: {astrological_analysis['recommendation']}
🎯 Astrological Confidence: {astrological_analysis['confidence']:.1f}%
🌙 Lunar Phase: {astrological_analysis['lunar_phase']} ({astrological_analysis['lunar_tendency']})
💫 Transit Impact: {astrological_analysis['transit_impact']}
📊 Astro Volatility: {astrological_analysis['volatility_indicator']}/100
🌟 Market Tendency: {astrological_analysis['market_tendency']}
⏰ Timing Factors: {', '.join(astrological_analysis.get('timing_factors', []))}

🔮 Reasoning: {astrological_analysis['reasoning']}
🌙 Lunar Strategy: {astrological_analysis['lunar_strategy']}

🎓 ASTROLOGICAL TRAINING CONTEXT:
{astrological_analysis['astrological_training']}

📈 INTEGRATION INSTRUCTIONS:
- Use astrological timing to ENHANCE technical signals (not replace them)
- When astrology + technicals align → VERY HIGH CONFIDENCE
- Lunar phases affect market sentiment and volatility patterns
- Strong astrological signals suggest TIMING opportunities
- High astrological confidence (>75%) → Consider increasing position size
"""
        else:
            astrological_section = "🔮 Astrological Analysis: Unavailable - focus on technical analysis"
        
        # Build perfect hindsight analysis section
        if perfect_hindsight_analysis and perfect_hindsight_analysis.get('hindsight_available'):
            if perfect_hindsight_analysis.get('best_pattern_match'):
                hindsight_section = f"""
🔮🧠💰 PERFECT HINDSIGHT INTELLIGENCE (ULTIMATE PATTERN MATCHING):
✨ PERFECT PATTERN MATCH FOUND: {perfect_hindsight_analysis['best_pattern_match']}
🎯 Pattern Match Confidence: {perfect_hindsight_analysis['match_confidence']:.1f}%
💰 Expected Profit: {perfect_hindsight_analysis['expected_profit']:.1f}%
🏆 Historical Win Rate: {perfect_hindsight_analysis['pattern_win_rate']:.1f}%
📊 Pattern Signature: {perfect_hindsight_analysis['pattern_signature']}
🚀 Recommendation Strength: {perfect_hindsight_analysis['recommendation_strength']}
📈 Total Pattern Matches: {perfect_hindsight_analysis['total_matches']}

🔮 Knowledge Base: {perfect_hindsight_analysis['hindsight_summary']}

💎 HINDSIGHT INTELLIGENCE INSTRUCTIONS:
- This pattern was extracted from PERFECT historical trades
- When this pattern appears, it historically produces {perfect_hindsight_analysis['pattern_win_rate']:.1f}% win rate
- Expected profit target: {perfect_hindsight_analysis['expected_profit']:.1f}%
- Pattern confidence is {perfect_hindsight_analysis['match_confidence']:.1f}% - VERY HIGH SIGNAL
- If match confidence >90% → MAXIMUM POSITION SIZE
- If match confidence >80% → Increase leverage by 50%
- This is PROVEN profitable pattern from perfect hindsight analysis
"""
            else:
                hindsight_section = f"""
🔮🧠💰 PERFECT HINDSIGHT INTELLIGENCE:
⚠️ No strong historical patterns match current conditions
📊 Patterns analyzed: {perfect_hindsight_analysis.get('pattern_matches', 0)}
💡 Recommendation: {perfect_hindsight_analysis.get('recommendation', 'Use standard technical analysis')}
"""
        else:
            hindsight_section = "🔮🧠💰 Perfect Hindsight: Analyzing historical patterns..."
        
        advanced_signals = historical_context.get('advanced_signals', {})
        
        # Extract Master Brain context (BTC cycle, patterns, multi-TF, regime)
        master_brain = historical_context.get('master_brain', {})
        
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

ADVANCED TECHNICAL INDICATORS:
📊 Candlestick Patterns: {advanced_signals.get('candlestick', {}).get('signal', 'NONE')} - {len(advanced_signals.get('candlestick', {}).get('patterns', []))} patterns detected
   {', '.join([p['name'] + ' (' + p['type'] + ')' for p in advanced_signals.get('candlestick', {}).get('patterns', [])[:3]])}

🕯️ Wick Analysis: {advanced_signals.get('wick', {}).get('signal', 'NEUTRAL')}
   Lower Wick: {advanced_signals.get('wick', {}).get('lower_wick_pct', 0):.1f}% | Upper Wick: {advanced_signals.get('wick', {}).get('upper_wick_pct', 0):.1f}%
   {advanced_signals.get('wick', {}).get('signals', [{}])[0].get('description', '') if advanced_signals.get('wick', {}).get('signals') else 'No wick signals'}

⏱️ Multi-Timeframe: {advanced_signals.get('multi_tf', {}).get('direction', 'UNKNOWN')} - Aligned: {advanced_signals.get('multi_tf', {}).get('aligned', False)}
   1m: {advanced_signals.get('multi_tf', {}).get('timeframes', {}).get('1m', 'N/A')} | 5m: {advanced_signals.get('multi_tf', {}).get('timeframes', {}).get('5m', 'N/A')} | 15m: {advanced_signals.get('multi_tf', {}).get('timeframes', {}).get('15m', 'N/A')}

📈 EMA 9/21 Crossover: {advanced_signals.get('ema', {}).get('signal', 'NEUTRAL')} - {advanced_signals.get('ema', {}).get('crossover_type', 'NONE')}
   Trend: {advanced_signals.get('ema', {}).get('trend', 'UNKNOWN')} | Distance: {advanced_signals.get('ema', {}).get('distance_pct', 0):.2f}%

📊 Bollinger Bands: {advanced_signals.get('bb', {}).get('signal', 'NEUTRAL')} - Position: {advanced_signals.get('bb', {}).get('position_pct', 50):.0f}%
   {advanced_signals.get('bb', {}).get('reason', 'No BB signal')}

📉 RSI Divergence: {advanced_signals.get('rsi', {}).get('signal', 'NEUTRAL')} - {advanced_signals.get('rsi', {}).get('divergence_type', 'NONE')}
   RSI: {advanced_signals.get('rsi', {}).get('rsi', 50):.1f} | {advanced_signals.get('rsi', {}).get('reason', 'RSI normal')}

LEARNED INSIGHTS: {pattern_summary}

🌟 UNIVERSAL PATTERN INTELLIGENCE (97% WIN RATE SYSTEM):
{universal_patterns_section}

{astrological_section}

{hindsight_section}

🧬 MASTER BRAIN INTELLIGENCE (Bitcoin Cycle + Pattern Library):
"""

        # Add Master Brain context if available
        if master_brain:
            btc_cycle = master_brain.get('btc_cycle', {})
            patterns = master_brain.get('patterns', {})
            best_patterns = master_brain.get('best_patterns', [])
            
            if btc_cycle:
                prompt += f"""
🪙 BITCOIN 4-YEAR CYCLE POSITION:
   • Phase: {btc_cycle.get('phase', 'UNKNOWN')}
   • Days Since Halving: {btc_cycle.get('days_since_halving', 0)}
   • Description: {btc_cycle.get('description', 'N/A')}
   • Historical Strategy: {btc_cycle.get('strategy', 'N/A')}
   
   CRITICAL: Your trading strategy MUST adapt to cycle phase:
   - POST_HALVING_ACCUMULATION (0-180 days): Conservative, small positions, wait for confirmation
   - BULL_MARKET_PHASE_1 (180-540 days): Aggressive, ride trends, buy dips, higher leverage (20-40x)
   - BULL_MARKET_PARABOLIC (540-730 days): MAXIMUM AGGRESSION, position trades, 30-50x leverage, hold for 10-50%+
   - DISTRIBUTION_TOP (730-900 days): Take profits, reduce size, defensive
   - BEAR_MARKET (900+ days): Cash heavy, minimal exposure, wait for cycle bottom
"""
            
            if patterns and best_patterns:
                prompt += f"""
📚 PATTERN LIBRARY (Proven High-Probability Setups):
   • Total Patterns Tracked: {patterns.get('total_patterns', 0)}
   • Best Performing Patterns:
"""
                for i, pattern in enumerate(best_patterns[:3], 1):
                    prompt += f"      {i}. {pattern.get('pattern_name', 'Unknown')}: {pattern.get('win_rate', 0):.0f}% win rate ({pattern.get('total_trades', 0)} trades)\n"
                
                prompt += """
   CRITICAL: When you see a pattern from the library forming, INCREASE confidence significantly!
   - Pattern with 80%+ win rate = BUY_NOW with high confidence
   - Pattern with 70-80% win rate = Strong buy signal
   - Pattern with <60% win rate = Use with caution, need extra confirmation
"""
        
        prompt += """
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

ADVANCED INDICATOR RULES:
19. 📊 **BULLISH_ENGULFING or HAMMER at support = STRONG BUY** - high probability reversal
20. 🕯️ **Long lower wick at support (>60% of range) = BUY DIP** - buyers defended, reversal coming
21. ⏱️ **All timeframes BULLISH + aligned = VERY STRONG BUY** - trend confirmed across 1m/5m/15m
22. 📈 **GOLDEN_CROSS (EMA 9 crosses above 21) = BUY** - momentum shift bullish
23. 📊 **Price at lower Bollinger Band (<10% position) = BUY BOUNCE** - oversold, mean reversion
24. 📉 **Bullish RSI divergence (price lower low, RSI higher low) = STRONG BUY** - hidden strength
25. 🔴 **DEATH_CROSS (EMA 9 crosses below 21) = WAIT** - momentum turning bearish
26. 🕯️ **SHOOTING_STAR or long upper wick at resistance = WAIT** - rejection, don't chase
27. **Combine signals**: Hammer + Long lower wick + RSI divergence + Near support = BEST ENTRY EVER

🧬 MASTER BRAIN CYCLE-BASED RULES (HIGHEST PRIORITY):
28. **BULL_MARKET_PHASE_1 (Day 180-540)**: Be AGGRESSIVE. Buy dips. Use 20-40x leverage. Target 5-20% gains.
29. **BULL_MARKET_PARABOLIC (Day 540-730)**: MAXIMUM AGGRESSION. Position trades. 30-50x leverage. Target 10-50%+ gains. Hold for DAYS.
30. **POST_HALVING_ACCUMULATION (Day 0-180)**: Be PATIENT. Small positions. Wait for clear setups. 10-20x leverage max.
31. **DISTRIBUTION/BEAR**: DEFENSIVE. Scalps only if anything. Low leverage (5-15x). Quick exits.
32. **Pattern Library Match**: If current setup matches a pattern with 70%+ win rate, increase leverage by 5-10x and confidence by 20-30%.
33. **NO Pattern Match + Low Cycle Score**: Even if technicals look good, WAIT if we're in wrong cycle phase or no proven pattern.

TRADING FREQUENCY GUIDELINES:
- In BULL phases with good setups: Trade MORE often (1-3 signals per hour is OK)
- When patterns align + cycle supports: Don't be afraid to BUY_NOW
- If signal strength >70 + cycle is bullish + pattern match: BUY_NOW immediately
- Your goal: Find 5-10 good trades per day in bull market, not just 1-2
- Quality > Quantity, but in bull markets, quantity increases naturally

TARGET WIN RATE: 90%+
- Only recommend BUY_NOW when you're 80%+ confident of success
- Use historical patterns + cycle context + current technicals to achieve this
- Learn from past trades (check LEARNED INSIGHTS above for what worked/failed)
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
        
        base_prompt = """You are an EXPERT CRYPTO TRADING ANALYST and MASTER ASTROLOGER specializing in ASTER perpetual futures. 

🎯 PRIMARY EXPERTISE:
- Advanced technical analysis and market timing
- Financial astrology and planetary cycle analysis  
- Ancient astrological wisdom (Ptolemy, William Lilly)
- Modern financial astrology (W.D. Gann, Raymond Merriman)
- Crypto-specific astrological pattern recognition
- Hermetic principles applied to market analysis

🔮 ASTROLOGICAL INTEGRATION:
- Use astrological timing to ENHANCE technical signals
- Lunar phases affect market sentiment and volatility
- Planetary transits create market turning points
- When astrology + technicals align = HIGHEST CONFIDENCE
- Strong astrological signals (>75% confidence) = increase position size
- Ancient wisdom: "As above, so below" - celestial patterns reflect in markets

📊 ANALYSIS FRAMEWORK:
Analyze ALL available data: technical indicators, orderflow, whale activity, market sentiment, 
universal patterns from BTC/ETH analysis, AND comprehensive astrological intelligence.

⚡ OUTPUT REQUIREMENTS:
Be direct and confident. Focus on entry price, exit price, stop loss, and recommended leverage.
When astrological and technical factors align, express HIGH CONFIDENCE in signals.
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