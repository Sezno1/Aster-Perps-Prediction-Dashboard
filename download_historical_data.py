"""
Download complete historical dataset for BTC, ETH, and save to databases
Run this once to populate historical data
"""

import sqlite3
import pandas as pd
from ccxt_aggregator import MultiExchangeAggregator
from datetime import datetime
import time

def create_market_data_db():
    """Create database for storing historical market data"""
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ohlcv (
            symbol TEXT,
            timeframe TEXT,
            timestamp TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            PRIMARY KEY (symbol, timeframe, timestamp)
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_symbol_tf_time 
        ON ohlcv(symbol, timeframe, timestamp)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ market_data.db created")

def save_ohlcv_to_db(symbol, timeframe, df):
    """Save OHLCV dataframe to database"""
    if df.empty:
        return
    
    conn = sqlite3.connect('market_data.db')
    
    records = []
    for timestamp, row in df.iterrows():
        records.append((
            symbol,
            timeframe,
            timestamp.isoformat(),
            float(row['open']),
            float(row['high']),
            float(row['low']),
            float(row['close']),
            float(row['volume'])
        ))
    
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR REPLACE INTO ohlcv (symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    
    conn.commit()
    conn.close()
    print(f"   ✅ Saved {len(records)} records to DB")

def download_all_historical_data():
    """Main function to download all historical data"""
    
    print("\n" + "="*70)
    print("🚀 HISTORICAL DATA DOWNLOAD - Building Pattern Discovery Database")
    print("="*70 + "\n")
    
    create_market_data_db()
    
    agg = MultiExchangeAggregator()
    
    symbols = ['BTC/USDT', 'ETH/USDT']
    
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    
    days_map = {
        '1m': 30,
        '5m': 90,
        '15m': 180,
        '30m': 365,
        '1h': 730,
        '4h': 1460,
        '1d': 1460
    }
    
    for symbol in symbols:
        print(f"\n{'='*70}")
        print(f"📥 Downloading {symbol}")
        print(f"{'='*70}\n")
        
        for tf in timeframes:
            days = days_map.get(tf, 365)
            
            df = agg.get_historical_ohlcv(symbol, tf, days, 'binance')
            
            if not df.empty:
                save_ohlcv_to_db(symbol, tf, df)
            
            time.sleep(1)
    
    print("\n" + "="*70)
    print("✅ HISTORICAL DATA DOWNLOAD COMPLETE")
    print("="*70 + "\n")
    
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT symbol, timeframe, COUNT(*) FROM ohlcv GROUP BY symbol, timeframe')
    results = cursor.fetchall()
    
    print("📊 Data Summary:")
    for symbol, tf, count in results:
        print(f"   {symbol} {tf}: {count:,} candles")
    
    conn.close()

if __name__ == '__main__':
    download_all_historical_data()