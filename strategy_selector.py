"""
Strategy Selector
Chooses between SCALP / SWING / POSITION strategies based on context
"""

from datetime import datetime

class StrategySelector:
    
    def select_strategy(self, multi_tf_analysis, cycle_position, pattern_matches, market_regime):
        """
        Select optimal strategy based on all available context
        Returns: 'SCALP', 'SWING', or 'POSITION'
        """
        
        cycle_phase = cycle_position.get('phase', '')
        days_since_halving = cycle_position.get('days_since_halving', 0)
        
        confluence_score = multi_tf_analysis.get('alignment_score', 0)
        overall_trend_strength = multi_tf_analysis.get('avg_strength', 0)
        
        regime = market_regime.get('overall_regime', 'MIXED')
        
        best_pattern = None
        if pattern_matches:
            best_pattern = max(pattern_matches, key=lambda x: x.get('win_rate', 0))
        
        if cycle_phase in ['BULL_MARKET_PARABOLIC', 'BULL_MARKET_PHASE_1']:
            if confluence_score >= 75 and overall_trend_strength > 60:
                if regime == 'STRONG_UPTREND':
                    strategy = 'POSITION'
                    leverage_range = (25, 50)
                    hold_time = 'days'
                    target_profit = (10, 50)
                    reasoning = f"Bull market + strong multi-TF trend. Hold for major move. Day {days_since_halving} post-halving = prime time."
                else:
                    strategy = 'SWING'
                    leverage_range = (15, 30)
                    hold_time = 'hours'
                    target_profit = (3, 10)
                    reasoning = "Bull market but mixed timeframes. Swing trade for good R:R."
            
            else:
                strategy = 'SCALP'
                leverage_range = (5, 15)
                hold_time = 'minutes'
                target_profit = (0.5, 2)
                reasoning = "Bull market but low confluence. Quick scalps only."
        
        elif cycle_phase == 'POST_HALVING_ACCUMULATION':
            if confluence_score >= 70:
                strategy = 'SWING'
                leverage_range = (10, 25)
                hold_time = 'hours'
                target_profit = (2, 8)
                reasoning = "Post-halving accumulation. Patient swings with decent confluence."
            else:
                strategy = 'SCALP'
                leverage_range = (5, 15)
                hold_time = 'minutes'
                target_profit = (0.5, 2)
                reasoning = "Post-halving but ranging. Scalp only when clear setups."
        
        elif cycle_phase in ['DISTRIBUTION_TOP', 'BEAR_MARKET']:
            strategy = 'SCALP'
            leverage_range = (5, 10)
            hold_time = 'minutes'
            target_profit = (0.5, 1.5)
            reasoning = f"{cycle_phase}: Defensive mode. Quick scalps only, low leverage."
        
        else:
            if regime == 'VOLATILE':
                strategy = 'SCALP'
                leverage_range = (5, 15)
                hold_time = 'minutes'
                target_profit = (0.5, 2)
                reasoning = "High volatility. Scalp the chop."
            
            elif regime == 'RANGING_MARKET':
                strategy = 'SWING'
                leverage_range = (10, 20)
                hold_time = 'hours'
                target_profit = (2, 5)
                reasoning = "Ranging market. Mean reversion swings."
            
            elif confluence_score >= 70:
                strategy = 'SWING'
                leverage_range = (15, 30)
                hold_time = 'hours'
                target_profit = (3, 10)
                reasoning = "Good multi-TF confluence. Swing for solid gains."
            
            else:
                strategy = 'SCALP'
                leverage_range = (5, 15)
                hold_time = 'minutes'
                target_profit = (0.5, 2)
                reasoning = "No clear edge. Scalp when opportunity appears."
        
        if best_pattern and best_pattern.get('win_rate', 0) >= 80:
            if strategy == 'SCALP':
                strategy = 'SWING'
                leverage_range = (leverage_range[0] + 5, leverage_range[1] + 10)
                reasoning += f" Upgraded to SWING: {best_pattern['pattern_name']} has {best_pattern['win_rate']:.0f}% win rate."
        
        return {
            'strategy': strategy,
            'leverage_min': leverage_range[0],
            'leverage_max': leverage_range[1],
            'recommended_leverage': int((leverage_range[0] + leverage_range[1]) / 2),
            'hold_time': hold_time,
            'target_profit_min': target_profit[0],
            'target_profit_max': target_profit[1],
            'reasoning': reasoning
        }

if __name__ == '__main__':
    print("✅ Strategy Selector Ready")