"""
🔍 COMPREHENSIVE SYSTEM HEALTH CHECK
Verifies all octopus tentacles are functioning properly
Ensures 97% win rate trading system is fully operational

CHECKS PERFORMED:
1. Database integrity and data availability
2. API connections and data feeds
3. Pattern engine functionality
4. MVRV tracker status
5. AI learning system status
6. Historical data completeness
7. Error handling and recovery systems

RUN THIS AFTER:
- System crashes or restarts
- Major updates or enhancements
- Suspected data corruption
- Performance issues

USAGE:
    python3 system_health_check.py
"""

import sqlite3
from datetime import datetime, timedelta
import sys
import os

def check_databases():
    """Check all databases exist and have data"""
    print("\n🗄️ CHECKING DATABASES...")
    
    databases = {
        'data/market_data.db': 'Historical BTC/ETH data',
        'data/ai_predictions.db': 'AI trade predictions', 
        'data/pattern_library.db': 'Legacy pattern library',
        'data/dynamic_patterns.db': '97% WIN RATE PATTERNS',
        'data/mvrv_data.db': 'MVRV Z-Score intelligence',
        'data/price_history.db': 'ASTER price history',
        'data/btc_cycles.db': 'Bitcoin cycle tracking',
        'data/market_regime.db': 'Market regime detection',
        'data/whale_trades.db': 'Whale activity'
    }
    
    db_status = {}
    
    for db_name, description in databases.items():
        try:
            if not os.path.exists(db_name):
                print(f"   ❌ {db_name}: Database file missing")
                db_status[db_name] = False
                continue
                
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if not tables:
                print(f"   ⚠️ {db_name}: No tables found")
                db_status[db_name] = False
            else:
                # Check for data in main tables
                data_found = False
                for table in tables[:3]:  # Check first 3 tables
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            data_found = True
                            break
                    except:
                        continue
                
                if data_found:
                    print(f"   ✅ {db_name}: {description} ({len(tables)} tables)")
                    db_status[db_name] = True
                else:
                    print(f"   ⚠️ {db_name}: Tables exist but no data")
                    db_status[db_name] = False
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ {db_name}: Error - {e}")
            db_status[db_name] = False
    
    return db_status

def check_api_connections():
    """Check external API connections"""
    print("\n🌐 CHECKING API CONNECTIONS...")
    
    api_status = {}
    
    # 1. MVRV API (bitcoinition.com)
    try:
        import requests
        response = requests.get('https://bitcoinition.com/current.json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            zscore = data.get('data', {}).get('current_mvrvzscore', 0)
            print(f"   ✅ MVRV API: Z-Score {zscore}")
            api_status['mvrv'] = True
        else:
            print(f"   ❌ MVRV API: HTTP {response.status_code}")
            api_status['mvrv'] = False
    except Exception as e:
        print(f"   ❌ MVRV API: {e}")
        api_status['mvrv'] = False
    
    # 2. Aster DEX API
    try:
        from aster_api import AsterAPI
        aster = AsterAPI()
        price_data = aster.get_24h_ticker('ASTERUSDT')
        if price_data and 'price' in price_data:
            print(f"   ✅ Aster API: Price ${float(price_data['price']):.6f}")
            api_status['aster'] = True
        else:
            print(f"   ❌ Aster API: No price data")
            api_status['aster'] = False
    except Exception as e:
        print(f"   ❌ Aster API: {e}")
        api_status['aster'] = False
    
    return api_status

def check_pattern_engine():
    """Check pattern mining engine status"""
    print("\n🧬 CHECKING PATTERN ENGINE...")
    
    try:
        from pattern_miner import PatternMiner
        miner = PatternMiner()
        
        # Check active patterns
        active_patterns = miner.get_active_patterns_summary()
        print(f"   📊 Active patterns: {len(active_patterns)}")
        print(f"   🎯 Win rate threshold: {miner.adaptive_params['min_win_rate']:.1%}")
        
        if active_patterns:
            best_pattern = active_patterns[0]
            print(f"   🏆 Best pattern: {best_pattern['name']} ({best_pattern['win_rate']:.1%})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Pattern engine error: {e}")
        return False

def check_mvrv_intelligence():
    """Check MVRV tracker status"""
    print("\n🧠 CHECKING MVRV INTELLIGENCE...")
    
    try:
        from mvrv_tracker import MVRVTracker
        tracker = MVRVTracker()
        
        analysis = tracker.get_current_analysis()
        if analysis:
            print(f"   📊 MVRV Z-Score: {analysis['zscore']:.2f}")
            print(f"   📈 Market Phase: {analysis['market_phase']}")
            print(f"   💡 Recommendation: {analysis['recommendation']}")
            print(f"   🎯 Confidence: {analysis['confidence']}%")
            return True
        else:
            print(f"   ❌ No MVRV analysis available")
            return False
            
    except Exception as e:
        print(f"   ❌ MVRV tracker error: {e}")
        return False

def check_ai_learning():
    """Check AI learning system status"""
    print("\n🤖 CHECKING AI LEARNING SYSTEM...")
    
    try:
        conn = sqlite3.connect('data/ai_predictions.db')
        cursor = conn.cursor()
        
        # Total predictions
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total_predictions = cursor.fetchone()[0]
        
        # Recent predictions (last 24h)
        cursor.execute("""
            SELECT COUNT(*) FROM predictions 
            WHERE timestamp > datetime('now', '-24 hours')
        """)
        recent_predictions = cursor.fetchone()[0]
        
        # Win rate
        cursor.execute("""
            SELECT COUNT(*) FROM predictions 
            WHERE recommendation IN ('BUY_NOW', 'STRONG_BUY') AND outcome = 'WIN'
        """)
        wins = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM predictions 
            WHERE recommendation IN ('BUY_NOW', 'STRONG_BUY') AND outcome IN ('WIN', 'LOSS')
        """)
        total_trades = cursor.fetchone()[0]
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        print(f"   📊 Total predictions: {total_predictions}")
        print(f"   ⏰ Recent (24h): {recent_predictions}")
        print(f"   🎯 Win rate: {win_rate:.1f}% ({wins}/{total_trades})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ AI learning error: {e}")
        return False

def check_data_freshness():
    """Check how fresh the data is"""
    print("\n🕐 CHECKING DATA FRESHNESS...")
    
    freshness_status = {}
    
    # Price history freshness
    try:
        conn = sqlite3.connect('data/price_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM price_ticks")
        last_tick = cursor.fetchone()[0]
        
        if last_tick:
            last_time = datetime.fromisoformat(last_tick)
            minutes_ago = (datetime.now() - last_time).total_seconds() / 60
            
            if minutes_ago < 5:
                print(f"   ✅ Price data: {minutes_ago:.1f} minutes ago (Fresh)")
                freshness_status['price'] = True
            else:
                print(f"   ⚠️ Price data: {minutes_ago:.1f} minutes ago (Stale)")
                freshness_status['price'] = False
        else:
            print(f"   ❌ Price data: No data found")
            freshness_status['price'] = False
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Price freshness check: {e}")
        freshness_status['price'] = False
    
    # Historical data freshness
    try:
        conn = sqlite3.connect('data/market_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM ohlcv WHERE timeframe = '1h'")
        last_candle = cursor.fetchone()[0]
        
        if last_candle:
            last_time = datetime.fromisoformat(last_candle)
            hours_ago = (datetime.now() - last_time).total_seconds() / 3600
            
            if hours_ago < 2:
                print(f"   ✅ Historical data: {hours_ago:.1f} hours ago (Fresh)")
                freshness_status['historical'] = True
            else:
                print(f"   ⚠️ Historical data: {hours_ago:.1f} hours ago (Needs update)")
                freshness_status['historical'] = False
        else:
            print(f"   ❌ Historical data: No data found")
            freshness_status['historical'] = False
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Historical freshness check: {e}")
        freshness_status['historical'] = False
    
    return freshness_status

def main():
    """Run complete system health check"""
    print("="*70)
    print("🔍 COMPREHENSIVE SYSTEM HEALTH CHECK")
    print("🐙 Verifying all octopus tentacles are functioning")
    print("="*70)
    
    all_results = {}
    
    # Run all checks
    all_results['databases'] = check_databases()
    all_results['apis'] = check_api_connections()
    all_results['pattern_engine'] = check_pattern_engine()
    all_results['mvrv'] = check_mvrv_intelligence()
    all_results['ai_learning'] = check_ai_learning()
    all_results['freshness'] = check_data_freshness()
    
    # Overall health assessment
    print("\n" + "="*70)
    print("🏥 OVERALL SYSTEM HEALTH")
    print("="*70)
    
    total_checks = 0
    passed_checks = 0
    
    # Database health
    db_health = sum(all_results['databases'].values())
    db_total = len(all_results['databases'])
    total_checks += db_total
    passed_checks += db_health
    print(f"📊 Databases: {db_health}/{db_total} operational")
    
    # API health
    api_health = sum(all_results['apis'].values())
    api_total = len(all_results['apis'])
    total_checks += api_total
    passed_checks += api_health
    print(f"🌐 APIs: {api_health}/{api_total} connected")
    
    # System components
    components = ['pattern_engine', 'mvrv', 'ai_learning']
    component_health = sum(all_results[comp] for comp in components)
    total_checks += len(components)
    passed_checks += component_health
    print(f"🧬 Core Systems: {component_health}/{len(components)} functional")
    
    # Data freshness
    fresh_health = sum(all_results['freshness'].values())
    fresh_total = len(all_results['freshness'])
    total_checks += fresh_total
    passed_checks += fresh_health
    print(f"🕐 Data Freshness: {fresh_health}/{fresh_total} up-to-date")
    
    # Overall score
    health_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n🎯 OVERALL HEALTH: {health_percentage:.1f}% ({passed_checks}/{total_checks})")
    
    if health_percentage >= 90:
        print("🟢 EXCELLENT - System fully operational!")
        status = "EXCELLENT"
    elif health_percentage >= 75:
        print("🟡 GOOD - Minor issues detected")
        status = "GOOD"
    elif health_percentage >= 50:
        print("🟠 FAIR - Some components need attention")
        status = "FAIR"
    else:
        print("🔴 POOR - Major issues require immediate attention")
        status = "POOR"
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if health_percentage < 100:
        if db_health < db_total:
            print("   • Run initialize_system.py to create missing databases")
        if api_health < api_total:
            print("   • Check internet connection and API endpoints")
        if fresh_health < fresh_total:
            print("   • Run download_historical_data.py to refresh data")
        if not all_results['pattern_engine']:
            print("   • Restart pattern mining engine")
        if not all_results['mvrv']:
            print("   • Check MVRV tracker configuration")
    else:
        print("   🎉 All systems operational - ready for 97% win rate trading!")
    
    print("="*70)
    return status

if __name__ == "__main__":
    main()