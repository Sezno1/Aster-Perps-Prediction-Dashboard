"""
MASTER BRAIN - Integrated Pattern Discovery Trading System
Combines all engines: Cycles, Patterns, Multi-TF, Regime, Strategy Selection
This is the central intelligence that makes final trading decisions
"""

from btc_cycle_engine import BTCCycleEngine
from market_regime import MarketRegimeDetector
from multi_timeframe_engine import MultiTimeframeEngine
from pattern_library import PatternLibrary
from strategy_selector import StrategySelector
from ccxt_aggregator import MultiExchangeAggregator
from datetime import datetime
import json

class MasterBrain:
    
    def __init__(self):
        print("\n🧠 Initializing Master Brain...")
        
        self.cycle_engine = BTCCycleEngine()
        self.regime_detector = MarketRegimeDetector()
        self.mtf_engine = MultiTimeframeEngine()
        self.pattern_lib = PatternLibrary()
        self.strategy_selector = StrategySelector()
        self.data_agg = MultiExchangeAggregator()
        
        print("✅ Master Brain Online\n")
    
    def analyze_complete_market_context(self, symbol='ASTER/USDT'):
        """
        Complete market analysis combining all intelligence sources
        This is what gets fed to the AI for decision making
        """
        
        print(f"\n{'='*70}")
        print(f"🧠 MASTER BRAIN ANALYSIS: {symbol}")
        print(f"{'='*70}\n")
        
        btc_cycle = self.cycle_engine.get_current_cycle_position()
        
        print(f"📅 BTC Cycle: {btc_cycle['phase']}")
        print(f"   Days since halving: {btc_cycle['days_since_halving']}")
        print(f"   Cycle progress: {btc_cycle['cycle_progress_pct']:.1f}%")
        print(f"   Strategy: {btc_cycle['trading_strategy']}\n")
        
        print(f"📊 Altcoin Season Index: Calculating...")
        alt_season_index = self.data_agg.calculate_altcoin_season_index()
        
        if alt_season_index > 75:
            alt_season_status = "🔥 ALT SEASON - Maximum aggression on alts"
        elif alt_season_index > 50:
            alt_season_status = "⚖️ MIXED - Selective alt trading"
        else:
            alt_season_status = "🪙 BTC SEASON - Alts lagging, be defensive"
        
        print(f"   Status: {alt_season_status}\n")
        
        print(f"🔭 Multi-Timeframe Analysis...")
        mtf_analysis = self.mtf_engine.analyze_all_timeframes('BTC/USDT')
        
        confluence = mtf_analysis['confluence']
        print(f"   Overall Signal: {confluence['overall_signal']}")
        print(f"   Confidence: {confluence['confidence']:.0f}%")
        print(f"   Alignment Score: {confluence['alignment_score']:.0f}%")
        print(f"   Reasoning: {confluence['reasoning']}\n")
        
        print(f"📈 Market Regime Detection...")
        market_data = {}
        for tf in ['1m', '5m', '15m', '1h', '4h']:
            df = self.mtf_engine.load_timeframe_data('BTC/USDT', tf, 200)
            if not df.empty:
                market_data[tf] = df
        
        regime_analysis = self.regime_detector.detect_multi_timeframe_regime('BTC/USDT', market_data)
        print(f"   Overall Regime: {regime_analysis['overall_regime']}")
        print(f"   Strategy: {regime_analysis['strategy']}")
        print(f"   Alignment: {regime_analysis['alignment_score']:.0f}%\n")
        
        print(f"📚 Pattern Library Check...")
        best_patterns = self.pattern_lib.get_best_patterns(min_trades=0, min_win_rate=0)
        print(f"   Patterns in library: {len(best_patterns)}")
        
        active_patterns = []
        for pattern in best_patterns[:3]:
            print(f"   • {pattern['pattern_name']}: {pattern['win_rate']:.0f}% win rate")
            active_patterns.append(pattern)
        
        print(f"\n🎯 Strategy Selection...")
        strategy = self.strategy_selector.select_strategy(
            confluence,
            btc_cycle,
            active_patterns,
            regime_analysis
        )
        
        print(f"   Selected Strategy: {strategy['strategy']}")
        print(f"   Leverage: {strategy['leverage_min']}-{strategy['leverage_max']}x (Recommended: {strategy['recommended_leverage']}x)")
        print(f"   Hold Time: {strategy['hold_time']}")
        print(f"   Target Profit: {strategy['target_profit_min']}-{strategy['target_profit_max']}%")
        print(f"   Reasoning: {strategy['reasoning']}\n")
        
        complete_context = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            
            'btc_cycle': {
                'phase': btc_cycle['phase'],
                'days_since_halving': btc_cycle['days_since_halving'],
                'cycle_progress_pct': btc_cycle['cycle_progress_pct'],
                'description': btc_cycle['phase_description'],
                'trading_strategy': btc_cycle['trading_strategy']
            },
            
            'altcoin_season': {
                'index': alt_season_index,
                'status': alt_season_status
            },
            
            'multi_timeframe': {
                'overall_signal': confluence['overall_signal'],
                'confidence': confluence['confidence'],
                'alignment_score': confluence['alignment_score'],
                'reasoning': confluence['reasoning'],
                'buy_count': confluence['buy_count'],
                'uptrend_count': confluence['uptrend_count']
            },
            
            'market_regime': {
                'overall_regime': regime_analysis['overall_regime'],
                'strategy': regime_analysis['strategy'],
                'alignment_score': regime_analysis['alignment_score']
            },
            
            'patterns': {
                'best_patterns': active_patterns,
                'total_patterns': len(best_patterns)
            },
            
            'selected_strategy': strategy,
            
            'final_recommendation': self.make_final_decision(
                confluence, btc_cycle, alt_season_index, regime_analysis, strategy
            )
        }
        
        print(f"{'='*70}")
        print(f"🎯 FINAL RECOMMENDATION: {complete_context['final_recommendation']['action']}")
        print(f"   Confidence: {complete_context['final_recommendation']['confidence']:.0f}%")
        print(f"   {complete_context['final_recommendation']['reasoning']}")
        print(f"{'='*70}\n")
        
        return complete_context
    
    def make_final_decision(self, confluence, btc_cycle, alt_season_index, regime_analysis, strategy):
        """
        Make final trading decision based on all inputs
        """
        
        score = 0
        reasons = []
        
        if confluence['overall_signal'] in ['STRONG_BUY', 'BUY']:
            score += 30
            reasons.append(f"Multi-TF {confluence['overall_signal']}")
        
        if btc_cycle['phase'] in ['BULL_MARKET_PHASE_1', 'BULL_MARKET_PARABOLIC']:
            score += 25
            reasons.append(f"Bull cycle phase")
        
        if alt_season_index > 60:
            score += 20
            reasons.append(f"Alt season active ({alt_season_index:.0f}%)")
        
        if regime_analysis['overall_regime'] in ['STRONG_UPTREND']:
            score += 15
            reasons.append("Strong uptrend regime")
        
        if confluence['alignment_score'] > 70:
            score += 10
            reasons.append(f"High TF alignment ({confluence['alignment_score']:.0f}%)")
        
        if score >= 70:
            action = 'STRONG_BUY'
            confidence = min(score, 95)
        elif score >= 50:
            action = 'BUY'
            confidence = score
        elif score >= 30:
            action = 'WAIT_FOR_SETUP'
            confidence = 50
        else:
            action = 'WAIT'
            confidence = 30
        
        reasoning = " • ".join(reasons) if reasons else "No clear edge detected"
        
        return {
            'action': action,
            'confidence': confidence,
            'score': score,
            'reasoning': reasoning,
            'strategy': strategy['strategy'],
            'leverage': strategy['recommended_leverage'],
            'target_profit_range': (strategy['target_profit_min'], strategy['target_profit_max'])
        }
    
    def export_ai_context(self, context):
        """
        Export complete context in format optimized for AI consumption
        """
        
        ai_prompt = f"""
You are an expert crypto trader analyzing ASTER perpetual futures.

MACRO CONTEXT (Bitcoin 4-Year Cycle):
- Current Phase: {context['btc_cycle']['phase']}
- Days Since Halving: {context['btc_cycle']['days_since_halving']}
- Cycle Progress: {context['btc_cycle']['cycle_progress_pct']:.1f}%
- Historical Pattern: {context['btc_cycle']['description']}
- Recommended Approach: {context['btc_cycle']['trading_strategy']}

ALTCOIN MARKET CONTEXT:
- Altcoin Season Index: {context['altcoin_season']['index']:.1f}%
- Market Status: {context['altcoin_season']['status']}

MULTI-TIMEFRAME TECHNICAL ANALYSIS:
- Overall Signal: {context['multi_timeframe']['overall_signal']}
- Confidence: {context['multi_timeframe']['confidence']:.0f}%
- Timeframe Alignment: {context['multi_timeframe']['alignment_score']:.0f}%
- Analysis: {context['multi_timeframe']['reasoning']}
- Bullish Timeframes: {context['multi_timeframe']['buy_count']}/7
- Trending Up Timeframes: {context['multi_timeframe']['uptrend_count']}/7

MARKET REGIME:
- Current Regime: {context['market_regime']['overall_regime']}
- Optimal Strategy: {context['market_regime']['strategy']}
- Regime Alignment: {context['market_regime']['alignment_score']:.0f}%

PATTERN ANALYSIS:
- Known Patterns: {context['patterns']['total_patterns']}
- Best Performing Patterns:
"""
        
        for pattern in context['patterns']['best_patterns'][:3]:
            ai_prompt += f"\n  • {pattern['pattern_name']}: {pattern['win_rate']:.0f}% win rate over {pattern['total_trades']} trades"
        
        ai_prompt += f"""

RECOMMENDED STRATEGY:
- Type: {context['selected_strategy']['strategy']}
- Leverage Range: {context['selected_strategy']['leverage_min']}-{context['selected_strategy']['leverage_max']}x
- Recommended Leverage: {context['selected_strategy']['recommended_leverage']}x
- Expected Hold Time: {context['selected_strategy']['hold_time']}
- Target Profit: {context['selected_strategy']['target_profit_min']}-{context['selected_strategy']['target_profit_max']}%
- Strategic Reasoning: {context['selected_strategy']['reasoning']}

SYSTEM RECOMMENDATION:
- Action: {context['final_recommendation']['action']}
- Confidence: {context['final_recommendation']['confidence']:.0f}%
- Score: {context['final_recommendation']['score']}/100
- Reasoning: {context['final_recommendation']['reasoning']}

Based on this complete multi-dimensional analysis, provide your final trading decision with specific entry, stop-loss, and take-profit levels.
"""
        
        return ai_prompt

if __name__ == '__main__':
    brain = MasterBrain()
    
    context = brain.analyze_complete_market_context('ASTER/USDT')
    
    ai_prompt = brain.export_ai_context(context)
    
    print("\n" + "="*70)
    print("📝 AI CONTEXT PROMPT")
    print("="*70)
    print(ai_prompt)
    
    with open('master_brain_context.json', 'w') as f:
        json.dump(context, f, indent=2)
    
    print("\n✅ Context exported to master_brain_context.json")