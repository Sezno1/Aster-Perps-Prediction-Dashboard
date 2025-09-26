"""
Risk management and position sizing calculator
"""

from typing import Dict, Optional
import config

class RiskManager:
    
    @staticmethod
    def calculate_position_size(account_balance: float, 
                               entry_price: float,
                               stop_loss: float,
                               risk_percent: float = config.RISK_PER_TRADE,
                               leverage: int = 10) -> Dict:
        """
        Calculate position size based on risk management rules
        
        Args:
            account_balance: Total account balance in USDT
            entry_price: Planned entry price
            stop_loss: Stop loss price
            risk_percent: Percentage of account to risk (default 1%)
            leverage: Leverage multiplier
        
        Returns:
            Dictionary with position sizing details
        """
        
        if not entry_price or not stop_loss or entry_price <= stop_loss:
            return {
                'error': 'Invalid entry or stop loss price'
            }
        
        risk_amount = account_balance * risk_percent
        
        price_risk_percent = ((entry_price - stop_loss) / entry_price)
        
        position_size_usdt = risk_amount / price_risk_percent
        
        position_size_usdt = min(position_size_usdt, account_balance * leverage)
        
        margin_required = position_size_usdt / leverage
        
        quantity = position_size_usdt / entry_price
        
        max_loss = risk_amount
        
        liquidation_price = entry_price * (1 - (1 / leverage))
        
        risk_reward_ratios = {}
        for tp_mult in [1.5, 2.0, 3.0]:
            target_price = entry_price + (entry_price - stop_loss) * tp_mult
            potential_profit = (target_price - entry_price) * quantity
            risk_reward_ratios[f'{tp_mult}:1'] = {
                'target_price': round(target_price, 6),
                'profit': round(potential_profit, 2),
                'profit_percent': round((potential_profit / margin_required) * 100, 2)
            }
        
        return {
            'position_size_usdt': round(position_size_usdt, 2),
            'margin_required': round(margin_required, 2),
            'quantity': round(quantity, 4),
            'leverage': leverage,
            'entry_price': round(entry_price, 6),
            'stop_loss': round(stop_loss, 6),
            'liquidation_price': round(liquidation_price, 6),
            'max_loss': round(max_loss, 2),
            'risk_percent': risk_percent * 100,
            'price_risk_percent': round(price_risk_percent * 100, 2),
            'take_profit_levels': risk_reward_ratios
        }
    
    @staticmethod
    def get_leverage_from_recommendation(leverage_rec: str) -> int:
        """Extract leverage number from recommendation"""
        if '30-50x' in leverage_rec:
            return 40
        elif '10-20x' in leverage_rec:
            return 15
        elif '5-10x' in leverage_rec:
            return 7
        else:
            return 5
    
    @staticmethod
    def validate_trade_setup(signal_score: float, 
                            volatility: float,
                            funding_rate: Optional[float]) -> Dict:
        """Validate if trade setup meets safety criteria"""
        
        warnings = []
        is_safe = True
        
        if signal_score < 40:
            warnings.append("Signal strength too low")
            is_safe = False
        
        if volatility > 0.15:
            warnings.append("⚠️ Extremely high volatility - reduce position size")
        
        if funding_rate and funding_rate > 0.1:
            warnings.append("⚠️ Very high funding rate - expensive to hold longs")
            is_safe = False
        
        if signal_score >= 60 and not warnings:
            warnings.append("✅ Trade setup looks good")
        
        return {
            'is_safe': is_safe,
            'warnings': warnings
        }
    
    @staticmethod
    def calculate_trailing_stop(entry_price: float, 
                               current_price: float,
                               trail_percent: float = 0.03) -> Optional[float]:
        """Calculate trailing stop loss"""
        
        if current_price <= entry_price:
            return None
        
        trailing_stop = current_price * (1 - trail_percent)
        
        return max(entry_price, trailing_stop)