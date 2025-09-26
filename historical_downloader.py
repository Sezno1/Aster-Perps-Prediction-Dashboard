"""
Historical Data Downloader - Fetch all ASTER price history
Downloads complete historical data from Aster DEX and stores in database
"""

import time
from datetime import datetime, timedelta
import config
from aster_api import AsterAPI
from price_history import PriceHistoryDB

class HistoricalDownloader:
    def __init__(self):
        self.api = AsterAPI()
        self.db = PriceHistoryDB()
    
    def download_all_history(self, symbol: str = config.ASTER_SYMBOL):
        """
        Download complete historical data from Aster DEX
        Strategy: Start with daily candles, then fill gaps with smaller timeframes
        """
        print("\n" + "="*60)
        print("📥 DOWNLOADING COMPLETE ASTER HISTORY")
        print("="*60 + "\n")
        
        # Step 1: Get all daily candles (fastest way to get full history)
        print("📊 Step 1: Downloading daily candles...")
        daily_data = self.api.get_klines(symbol, '1d', 1000)
        
        if daily_data.empty:
            print("❌ Failed to fetch daily data")
            return
        
        print(f"✅ Downloaded {len(daily_data)} daily candles")
        print(f"📅 Range: {daily_data.index[0]} → {daily_data.index[-1]}")
        
        earliest_date = daily_data.index[0]
        latest_date = daily_data.index[-1]
        total_days = (latest_date - earliest_date).days
        
        print(f"📈 Total history: {total_days} days\n")
        
        # Step 2: Fill with 1-hour candles for better granularity
        print("📊 Step 2: Downloading hourly candles (this may take a while)...")
        
        # Aster API limit is 1000 candles per request
        # 1000 hours = ~41 days per batch
        current_end = latest_date
        batch_size_hours = 1000
        total_batches = (total_days // 41) + 1
        batch_num = 0
        total_candles = 0
        
        while current_end > earliest_date:
            batch_num += 1
            print(f"  Batch {batch_num}/{total_batches}: Fetching up to {current_end.strftime('%Y-%m-%d %H:%M')}...", end='')
            
            hourly_data = self.api.get_klines(symbol, '1h', batch_size_hours)
            
            if not hourly_data.empty:
                # Store in database
                for timestamp, row in hourly_data.iterrows():
                    self.db.log_price_tick(
                        price=float(row['close']),
                        volume_1m=float(row['volume']),
                        mark_price=None,
                        funding_rate=None
                    )
                    total_candles += 1
                
                current_end = hourly_data.index[0] - timedelta(hours=1)
                print(f" ✅ {len(hourly_data)} candles")
            else:
                print(" ⚠️ No data, moving on")
                break
            
            # Rate limit protection
            time.sleep(0.5)
        
        print(f"\n✅ Downloaded {total_candles} total hourly candles\n")
        
        # Step 3: Fill recent data with 1-minute candles (last 16 hours)
        print("📊 Step 3: Downloading recent 1-minute candles...")
        
        # Get last 1000 minutes (~16.6 hours)
        minute_data = self.api.get_klines(symbol, '1m', 1000)
        
        if not minute_data.empty:
            minute_candles = 0
            for timestamp, row in minute_data.iterrows():
                self.db.log_price_tick(
                    price=float(row['close']),
                    volume_1m=float(row['volume']),
                    mark_price=None,
                    funding_rate=None
                )
                minute_candles += 1
            
            print(f"✅ Downloaded {minute_candles} minute candles")
            print(f"📅 Recent range: {minute_data.index[0]} → {minute_data.index[-1]}\n")
        
        # Step 4: Calculate volume metrics and patterns
        print("📊 Step 4: Calculating volume metrics and patterns...")
        self.db.calculate_volume_metrics()
        print("✅ Volume metrics calculated\n")
        
        print("📊 Step 5: Detecting support/resistance levels...")
        sr = self.db.detect_support_resistance(lookback_hours=24*7)  # Last week
        if sr['support']:
            print(f"✅ Support: ${sr['support']:.6f} ({sr['support_tests']} tests)")
            print(f"✅ Resistance: ${sr['resistance']:.6f} ({sr['resistance_tests']} tests)\n")
        
        print("="*60)
        print("✅ HISTORICAL DOWNLOAD COMPLETE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"   • Total days: {total_days}")
        print(f"   • Hourly candles: {total_candles}")
        print(f"   • Minute candles: {minute_candles if minute_data is not None else 0}")
        print(f"   • Database: price_history.db")
        print("\n🚀 Scanner will now use all historical data for decisions!\n")

if __name__ == '__main__':
    downloader = HistoricalDownloader()
    downloader.download_all_history()