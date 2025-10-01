"""
Master Brain Integration Helper
Add this to app.py to enhance AI with full pattern discovery context
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tentacles.market_data.btc_cycle_engine import BTCCycleEngine
from tentacles.market_data.market_regime import MarketRegimeDetector  
from tentacles.technical.multi_timeframe_engine import MultiTimeframeEngine
from tentacles.pattern_analysis.pattern_library import PatternLibrary
from tentacles.intelligence.strategy_selector import StrategySelector
from tentacles.market_data.ccxt_aggregator import MultiExchangeAggregator
from tentacles.market_data.mvrv_tracker import MVRVIntegration

# Import astrological intelligence
try:
    from tentacles.astrological.crypto_astrology import crypto_astrology
    ASTROLOGY_AVAILABLE = True
except ImportError:
    ASTROLOGY_AVAILABLE = False

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
            self.mvrv_integration = MVRVIntegration()
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
            mvrv_context = self.mvrv_integration.get_mvrv_context()
            
            # Get astrological context
            astro_context = {}
            if ASTROLOGY_AVAILABLE:
                try:
                    astro_analysis = crypto_astrology.get_current_astro_recommendation('ASTER')
                    astro_context = {
                        'available': True,
                        'recommendation': astro_analysis['astrological_recommendation'],
                        'confidence': astro_analysis['confidence'],
                        'lunar_phase': astro_analysis['lunar_influence']['phase'],
                        'volatility_indicator': astro_analysis['volatility_indicator'],
                        'market_tendency': astro_analysis['market_tendency'],
                        'summary': crypto_astrology.get_dashboard_summary('ASTER')
                    }
                except Exception as e:
                    astro_context = {'available': False, 'error': str(e)}
            else:
                astro_context = {'available': False, 'reason': 'Astrology module not available'}
            
            enhanced_context = {
                'btc_cycle': {
                    'phase': btc_cycle['phase'],
                    'days_since_halving': btc_cycle['days_since_halving'],
                    'description': btc_cycle['phase_description'],
                    'strategy': btc_cycle['trading_strategy']
                },
                'mvrv_analysis': mvrv_context,
                'astrological_analysis': astro_context,
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
    
    def get_astrological_analysis(self):
        """Get astrological analysis for dashboard display"""
        
        if not ASTROLOGY_AVAILABLE:
            return {'available': False, 'reason': 'Astrology module not available'}
        
        try:
            astro_analysis = crypto_astrology.get_current_astro_recommendation('ASTER')
            return {
                'available': True,
                'recommendation': astro_analysis['astrological_recommendation'],
                'confidence': astro_analysis['confidence'],
                'lunar_phase': astro_analysis['lunar_influence']['phase'],
                'volatility_indicator': astro_analysis['volatility_indicator'],
                'market_tendency': astro_analysis['market_tendency'],
                'reasoning': astro_analysis['reasoning']
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
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
            
            # Add MVRV summary if available
            mvrv_summary = ""
            if context.get('mvrv_analysis') and context['mvrv_analysis']:
                mvrv = context['mvrv_analysis']
                zscore = mvrv.get('mvrv_zscore', 0)
                phase = mvrv.get('market_phase', '').replace('_', ' ')
                mvrv_summary = f" • MVRV: {zscore:.1f} ({phase})"
            
            summary = f"🧠 Cycle: {context['btc_cycle']['phase']} (Day {context['btc_cycle']['days_since_halving']} post-halving) • {context['pattern_count']} patterns tracked{mvrv_summary}"
            
            return summary
            
        except Exception as e:
            return "Master Brain: Error"

# Singleton instance
master_brain = MasterBrainIntegration()