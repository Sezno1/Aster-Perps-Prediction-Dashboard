"""
System Initialization Script
Run this ONCE to:
1. Create all databases
2. Seed pattern library
3. Download historical data (BTC/ETH)
4. Test all components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tentacles.pattern_analysis.pattern_library import PatternLibrary
from tentacles.market_data.btc_cycle_engine import BTCCycleEngine
from tentacles.market_data.market_regime import MarketRegimeDetector
from tentacles.market_data.download_historical_data import download_all_historical_data

def initialize_complete_system():
    print("\n" + "="*70)
    print("🚀 INITIALIZING PATTERN DISCOVERY TRADING SYSTEM")
    print("="*70 + "\n")
    
    print("Step 1: Creating databases...")
    try:
        cycle_engine = BTCCycleEngine()
        print("   ✅ btc_cycles.db created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    try:
        regime_detector = MarketRegimeDetector()
        print("   ✅ market_regime.db created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    try:
        pattern_lib = PatternLibrary()
        print("   ✅ pattern_library.db created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\nStep 2: Seeding Pattern Library with proven setups...")
    try:
        pattern_lib.seed_initial_patterns()
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\nStep 3: Downloading historical data...")
    print("   This will take 5-10 minutes. Downloading BTC + ETH across all timeframes...\n")
    
    try:
        response = input("   Download historical data now? (y/n): ")
        if response.lower() == 'y':
            download_all_historical_data()
        else:
            print("   ⏭️  Skipped. You can run download_historical_data.py later.")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\nStep 4: Testing BTC Cycle Engine...")
    try:
        cycle_position = cycle_engine.get_current_cycle_position()
        print(f"   ✅ Current cycle phase: {cycle_position['phase']}")
        print(f"   ✅ Days since halving: {cycle_position['days_since_halving']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ SYSTEM INITIALIZATION COMPLETE")
    print("="*70)
    
    print("\n📋 Next Steps:")
    print("   1. Run pattern_miner.py to discover patterns from historical data")
    print("   2. Run master_brain.py to see complete market analysis")
    print("   3. Integrate master_brain into app.py for live trading")
    print("\n")

if __name__ == '__main__':
    initialize_complete_system()