"""
System Health Check - Verify all octopus tentacles are functioning
Run this to ensure the complete system is operational
"""

import sqlite3
from datetime import datetime
import sys

def check_databases():
    """Check all databases exist and have data"""
    print("\n🗄️  CHECKING DATABASES...")
    
    databases = {
        'market_data.db': 'Historical BTC/ETH data',
        'ai_predictions.db': 'AI trade predictions',
        'pattern_library.db': 'Pattern library',
        'price_history.db': 'ASTER price history',
        'btc_cycles.db': 'Bitcoin cycle tracking',
        'market_regime.db': 'Market regime detection',
        'whale_trades.db': 'Whale activity'
    }
    
    for db_name, description in databases.items():
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if tables:
                print(f"   ✅ {db_name}: {len(tables)} tables - {description}")
            else:
                print(f"   ⚠️  {db_name}: No tables found")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ {db_name}: Error - {e}")

def check_historical_data():
    """Check if we have historical data"""
    print("\n📊 CHECKING HISTORICAL DATA...")
    
    try:
        conn = sqlite3.connect('market_data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT symbol, timeframe, COUNT(*) FROM ohlcv GROUP BY symbol, timeframe")
        results = cursor.fetchall()
        
        if results:
            print(f"   ✅ {len(results)} symbol/timeframe pairs:")
            total_candles = 0
            for symbol, tf, count in results:
                print(f"      • {symbol} {tf}: {count:,} candles")
                total_candles += count
            print(f"   📈 TOTAL: {total_candles:,} historical candles")
        else:
            print(f"   ⚠️  No historical data found")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_pattern_library():
    """Check pattern library status"""
    print("\n📚 CHECKING PATTERN LIBRARY...")
    
    try:
        conn = sqlite3.connect('pattern_library.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM patterns")
        pattern_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT pattern_name, total_trades, win_rate, profit_factor 
            FROM patterns 
            WHERE total_trades > 0
            ORDER BY win_rate DESC
        """)
        patterns_with_data = cursor.fetchall()
        
        print(f"   ✅ {pattern_count} patterns in library")
        
        if patterns_with_data:
            print(f"   📊 Patterns with trade data:")
            for name, trades, win_rate, pf in patterns_with_data:
                print(f"      • {name}: {trades} trades, {win_rate:.0f}% win rate, {pf:.2f} PF")
        else:
            print(f"   ℹ️  No patterns have trade data yet (need to start trading!)")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_btc_cycle():
    """Check BTC cycle engine"""
    print("\n🪙 CHECKING BTC CYCLE ENGINE...")
    
    try:
        from btc_cycle_engine import BTCCycleEngine
        
        engine = BTCCycleEngine()
        cycle_pos = engine.get_current_cycle_position()
        
        if cycle_pos:
            print(f"   ✅ BTC Cycle Engine: OPERATIONAL")
            print(f"      • Phase: {cycle_pos['phase']}")
            print(f"      • Days Since Halving: {cycle_pos['days_since_halving']}")
            print(f"      • Strategy: {cycle_pos['trading_strategy'][:50]}...")
        else:
            print(f"   ❌ BTC Cycle Engine: Unable to determine position")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_master_brain():
    """Check Master Brain integration"""
    print("\n🧬 CHECKING MASTER BRAIN...")
    
    try:
        from master_brain_integration import master_brain
        
        if master_brain.enabled:
            print(f"   ✅ Master Brain: ONLINE")
            
            context = master_brain.get_enhanced_context()
            
            if context:
                print(f"      • BTC Cycle: {context.get('btc_cycle', {}).get('phase', 'Unknown')}")
                print(f"      • Pattern Count: {context.get('pattern_count', 0)}")
                print(f"      • Summary: {master_brain.get_dashboard_summary()}")
        else:
            print(f"   ⚠️  Master Brain: OFFLINE")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_ai_predictions():
    """Check AI prediction tracking"""
    print("\n🧠 CHECKING AI PREDICTION TRACKING...")
    
    try:
        conn = sqlite3.connect('ai_predictions.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total_predictions = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*), 
                   SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN outcome = 'LOSS' THEN 1 ELSE 0 END)
            FROM predictions 
            WHERE recommendation IN ('BUY_NOW', 'STRONG_BUY')
        """)
        result = cursor.fetchone()
        total_trades, wins, losses = result[0], result[1] or 0, result[2] or 0
        
        if total_trades > 0:
            win_rate = (wins / total_trades) * 100
            print(f"   ✅ {total_predictions} total predictions logged")
            print(f"   📊 {total_trades} actual trades")
            print(f"      • Wins: {wins}")
            print(f"      • Losses: {losses}")
            print(f"      • Win Rate: {win_rate:.1f}%")
        else:
            print(f"   ℹ️  {total_predictions} predictions logged, no completed trades yet")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_components():
    """Check if all Python components can import"""
    print("\n🐙 CHECKING OCTOPUS TENTACLES (Components)...")
    
    components = {
        'data_fetcher': 'Real-time price data',
        'aster_api': 'Aster DEX API',
        'indicators': 'Technical indicators',
        'advanced_indicators': 'Advanced indicators',
        'orderflow_analyzer': 'Order flow analysis',
        'whale_tracker': 'Whale tracking',
        'price_history': 'Price history & patterns',
        'btc_cycle_engine': 'Bitcoin cycle tracking',
        'market_regime': 'Market regime detection',
        'multi_timeframe_engine': 'Multi-timeframe analysis',
        'pattern_library': 'Pattern library',
        'pattern_miner': 'Pattern discovery',
        'strategy_selector': 'Strategy selection',
        'backtest_engine': 'Backtesting',
        'master_brain': 'Master Brain coordinator',
        'master_brain_integration': 'Master Brain integration',
        'ai_analyzer': 'AI decision engine',
        'ai_prediction_tracker': 'Prediction tracking',
        'ccxt_aggregator': 'Multi-exchange data'
    }
    
    working = 0
    broken = 0
    
    for module_name, description in components.items():
        try:
            __import__(module_name)
            print(f"   ✅ {module_name}: {description}")
            working += 1
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
            broken += 1
    
    print(f"\n   📊 {working}/{len(components)} tentacles operational")
    if broken > 0:
        print(f"   ⚠️  {broken} tentacles need attention")

def run_health_check():
    """Run complete health check"""
    print("\n" + "="*70)
    print("🐙 ASTER TRADING SYSTEM - HEALTH CHECK")
    print("="*70)
    
    check_databases()
    check_historical_data()
    check_pattern_library()
    check_btc_cycle()
    check_master_brain()
    check_ai_predictions()
    check_components()
    
    print("\n" + "="*70)
    print("✅ HEALTH CHECK COMPLETE")
    print("="*70 + "\n")
    
    print("📊 Dashboard: http://localhost:5001")
    print("🧠 Master Brain: python3 master_brain.py")
    print("⛏️  Pattern Mining: python3 pattern_miner.py")
    print("\n")

if __name__ == '__main__':
    run_health_check()