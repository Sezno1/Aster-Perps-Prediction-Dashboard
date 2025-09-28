"""
Bitcoin 4-Year Cycle Tracker
Tracks where we are in the BTC halving cycle and provides context
"""

from datetime import datetime, timedelta
import sqlite3
import pandas as pd

class BTCCycleEngine:
    
    HALVING_DATES = [
        datetime(2012, 11, 28),
        datetime(2016, 7, 9),
        datetime(2020, 5, 11),
        datetime(2024, 4, 19),
        datetime(2028, 4, 1)
    ]
    
    def __init__(self):
        self.create_db()
    
    def create_db(self):
        """Create database for cycle tracking"""
        conn = sqlite3.connect('btc_cycles.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cycle_snapshots (
                timestamp TEXT PRIMARY KEY,
                days_since_halving INTEGER,
                cycle_phase TEXT,
                btc_price REAL,
                btc_dominance REAL,
                phase_description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_current_cycle_position(self):
        """Calculate where we are in current BTC cycle"""
        now = datetime.now()
        
        last_halving = None
        next_halving = None
        
        for i, halving_date in enumerate(self.HALVING_DATES):
            if halving_date <= now:
                last_halving = halving_date
                if i + 1 < len(self.HALVING_DATES):
                    next_halving = self.HALVING_DATES[i + 1]
        
        if not last_halving:
            return None
        
        days_since_halving = (now - last_halving).days
        
        if next_halving:
            days_until_next = (next_halving - now).days
            progress_pct = (days_since_halving / (days_since_halving + days_until_next)) * 100
        else:
            progress_pct = 0
        
        phase = self.determine_cycle_phase(days_since_halving)
        
        return {
            'last_halving': last_halving,
            'next_halving': next_halving,
            'days_since_halving': days_since_halving,
            'days_until_next': days_until_next if next_halving else None,
            'cycle_progress_pct': progress_pct,
            'phase': phase['name'],
            'phase_description': phase['description'],
            'trading_strategy': phase['strategy']
        }
    
    def determine_cycle_phase(self, days_since_halving):
        """
        Determine which phase of the 4-year cycle we're in
        Based on historical patterns:
        - Months 0-6: Accumulation (sideways/slight up)
        - Months 6-18: Bull Market (major uptrend)
        - Months 18-24: Distribution (top formation, selling pressure)
        - Months 24-48: Bear Market (downtrend, capitulation)
        """
        
        if days_since_halving < 180:
            return {
                'name': 'POST_HALVING_ACCUMULATION',
                'description': 'Early post-halving. Market absorbing supply shock. Accumulation phase.',
                'strategy': 'Conservative. Build positions. Wait for confirmation. Low leverage.',
                'expected_alt_behavior': 'Alts lag BTC. Patience required.'
            }
        
        elif days_since_halving < 540:
            return {
                'name': 'BULL_MARKET_PHASE_1',
                'description': 'Bull market begins. BTC breaks ATH. Momentum building.',
                'strategy': 'Aggressive. Ride trends. Higher leverage OK. Hold winners.',
                'expected_alt_behavior': 'Alts start moving. Follow BTC with lag. Bluechips lead.'
            }
        
        elif days_since_halving < 730:
            return {
                'name': 'BULL_MARKET_PARABOLIC',
                'description': 'Parabolic phase. Peak euphoria. Alt season typically occurs here.',
                'strategy': 'Maximum aggression but watch for top signals. Take profits. Alts can 10-50x.',
                'expected_alt_behavior': 'ALT SEASON. Massive gains possible. Bluechips 5-10x, small caps 50-100x.'
            }
        
        elif days_since_halving < 900:
            return {
                'name': 'DISTRIBUTION_TOP',
                'description': 'Market topping. Distribution phase. Volatility increases.',
                'strategy': 'Defensive. Take profits. Reduce leverage. Expect fake-outs.',
                'expected_alt_behavior': 'Alts peak and start declining. Rotate profits back to stables/BTC.'
            }
        
        else:
            return {
                'name': 'BEAR_MARKET',
                'description': 'Bear market. Downtrend. Capitulation events possible.',
                'strategy': 'Cash heavy. Small positions. Wait for cycle bottom. No leverage.',
                'expected_alt_behavior': 'Alts bleed badly. Down 80-95% from tops. Survive mode.'
            }
    
    def get_historical_cycle_comparison(self, current_days):
        """
        Compare current position to same point in previous cycles
        What happened at day X after halving in past cycles?
        """
        
        comparisons = []
        
        if current_days > 0:
            for i in range(len(self.HALVING_DATES) - 2):
                halving_date = self.HALVING_DATES[i]
                target_date = halving_date + timedelta(days=current_days)
                
                comparisons.append({
                    'cycle': f"{halving_date.year}",
                    'date_at_same_point': target_date,
                    'days_after_halving': current_days
                })
        
        return comparisons
    
    def log_cycle_snapshot(self, btc_price, btc_dominance=None):
        """Log current cycle state to database"""
        cycle_pos = self.get_current_cycle_position()
        
        if not cycle_pos:
            return
        
        conn = sqlite3.connect('btc_cycles.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cycle_snapshots 
            (timestamp, days_since_halving, cycle_phase, btc_price, btc_dominance, phase_description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            cycle_pos['days_since_halving'],
            cycle_pos['phase'],
            btc_price,
            btc_dominance,
            cycle_pos['phase_description']
        ))
        
        conn.commit()
        conn.close()
    
    def get_cycle_summary(self):
        """Get complete cycle summary for AI context"""
        cycle_pos = self.get_current_cycle_position()
        
        if not cycle_pos:
            return "Unable to determine cycle position"
        
        summary = f"""
🪙 BITCOIN 4-YEAR CYCLE ANALYSIS

📅 Current Position:
   • Last Halving: {cycle_pos['last_halving'].strftime('%Y-%m-%d')}
   • Days Since Halving: {cycle_pos['days_since_halving']} days
   • Next Halving: {cycle_pos['next_halving'].strftime('%Y-%m-%d') if cycle_pos['next_halving'] else 'N/A'}
   • Cycle Progress: {cycle_pos['cycle_progress_pct']:.1f}%

🎯 Current Phase: {cycle_pos['phase']}
   • {cycle_pos['phase_description']}

📊 Trading Strategy:
   • {cycle_pos['trading_strategy']}

💡 Historical Context:
   • At this point in previous cycles, major moves typically occurred
   • Study past behavior at day {cycle_pos['days_since_halving']} to predict next 30-90 days
        """
        
        return summary

if __name__ == '__main__':
    engine = BTCCycleEngine()
    
    print("\n" + "="*70)
    print("🪙 Bitcoin 4-Year Cycle Tracker")
    print("="*70)
    
    print(engine.get_cycle_summary())
    
    cycle_pos = engine.get_current_cycle_position()
    
    print("\n📈 Historical Comparison:")
    comparisons = engine.get_historical_cycle_comparison(cycle_pos['days_since_halving'])
    for comp in comparisons:
        print(f"   • {comp['cycle']} Cycle: Day {comp['days_after_halving']} was on {comp['date_at_same_point'].strftime('%Y-%m-%d')}")
    
    print("\n✅ BTC Cycle Engine Ready")