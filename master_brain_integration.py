"""
Master Brain Integration Helper
Add this to app.py to enhance AI with full pattern discovery context
"""

from btc_cycle_engine import BTCCycleEngine
from market_regime import MarketRegimeDetector  
from multi_timeframe_engine import MultiTimeframeEngine
from pattern_library import PatternLibrary
from strategy_selector import StrategySelector
from ccxt_aggregator import MultiExchangeAggregator

class MasterBrainIntegration:
    """
    Lightweight integration of Master Brain into existing app
    Provides enhanced context for AI without breaking existing functionality
    """
    
    def __init__(self):
        try:
            self.cycle_engine = BTCCycleEngine()
            self.regime_detector = MarketRegimeDetector()
            self.mtf_engine = MultiTimeframeEngine()
            self.pattern_lib = PatternLibrary()
            self.strategy_selector = StrategySelector()
            self.data_agg = MultiExchangeAggregator()
            self.enabled = True
            print("✅ Master Brain Integration: ONLINE")
        except Exception as e:
            self.enabled = False
            print(f"⚠️  Master Brain Integration: DISABLED ({e})")
    
    def get_enhanced_context(self):
        """
        Get enhanced market context for AI
        Returns dict with cycle, regime, patterns, etc.
        """
        
        if not self.enabled:
            return {}
        
        try:
            btc_cycle = self.cycle_engine.get_current_cycle_position()
            
            best_patterns = self.pattern_lib.get_best_patterns(min_trades=0, min_win_rate=0)
            
            enhanced_context = {
                'btc_cycle': {
                    'phase': btc_cycle['phase'],
                    'days_since_halving': btc_cycle['days_since_halving'],
                    'description': btc_cycle['phase_description'],
                    'strategy': btc_cycle['trading_strategy']
                },
                'pattern_count': len(best_patterns),
                'best_patterns': [
                    {
                        'name': p['pattern_name'],
                        'win_rate': p['win_rate'],
                        'trades': p['total_trades']
                    }
                    for p in best_patterns[:3]
                ]
            }
            
            return enhanced_context
            
        except Exception as e:
            print(f"Master Brain context error: {e}")
            return {}
    
    def get_ai_enhanced_prompt(self, market_data, signal_results, orderflow_analysis, whale_sentiment, historical_context):
        """
        Enhance AI prompt with Master Brain context
        """
        
        if not self.enabled:
            return ""
        
        try:
            context = self.get_enhanced_context()
            
            if not context:
                return ""
            
            prompt_addition = f"""

🧠 MASTER BRAIN CONTEXT:

Bitcoin 4-Year Cycle:
- Phase: {context['btc_cycle']['phase']}
- Days Since Halving: {context['btc_cycle']['days_since_halving']}
- Historical Pattern: {context['btc_cycle']['description']}
- Recommended Strategy: {context['btc_cycle']['strategy']}

Pattern Library:
- Total Patterns: {context['pattern_count']}
"""
            
            if context['best_patterns']:
                prompt_addition += "- Top Performing Patterns:\n"
                for p in context['best_patterns']:
                    prompt_addition += f"  • {p['name']}: {p['win_rate']:.0f}% win rate ({p['trades']} trades)\n"
            
            prompt_addition += "\nUse this cycle and pattern context to inform your trading decision.\n"
            
            return prompt_addition
            
        except Exception as e:
            return ""
    
    def get_dashboard_summary(self):
        """
        Get summary for dashboard display
        """
        
        if not self.enabled:
            return "Master Brain: Offline"
        
        try:
            context = self.get_enhanced_context()
            
            summary = f"🧠 Cycle: {context['btc_cycle']['phase']} (Day {context['btc_cycle']['days_since_halving']} post-halving) • {context['pattern_count']} patterns tracked"
            
            return summary
            
        except Exception as e:
            return "Master Brain: Error"

# Singleton instance
master_brain = MasterBrainIntegration()