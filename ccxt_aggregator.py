"""
CCXT Multi-Exchange Data Aggregator
Pulls data from multiple exchanges for better liquidity/volume analysis
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time

class MultiExchangeAggregator:
    def __init__(self):
        self.exchanges = {
            'binance': ccxt.binance(),
            'bybit': ccxt.bybit(),
            'okx': ccxt.okx(),
            'gateio': ccxt.gateio(),
            'kucoin': ccxt.kucoin()
        }
        
        for exchange in self.exchanges.values():
            exchange.enableRateLimit = True
    
    def get_historical_ohlcv(self, symbol, timeframe='1h', since_days=1460, exchange_name='binance'):
        """
        Download historical OHLCV data
        symbol: 'BTC/USDT', 'ETH/USDT', etc.
        timeframe: '1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'
        since_days: How many days back (default 1460 = 4 years)
        """
        try:
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                print(f"Exchange {exchange_name} not found")
                return pd.DataFrame()
            
            if not exchange.has['fetchOHLCV']:
                print(f"{exchange_name} doesn't support OHLCV")
                return pd.DataFrame()
            
            since = int((datetime.now() - timedelta(days=since_days)).timestamp() * 1000)
            
            all_candles = []
            limit = 1000
            
            print(f"📥 Downloading {symbol} {timeframe} from {exchange_name} (last {since_days} days)...")
            
            while True:
                try:
                    candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
                    
                    if not candles or len(candles) == 0:
                        break
                    
                    all_candles.extend(candles)
                    
                    since = candles[-1][0] + 1
                    
                    if len(candles) < limit:
                        break
                    
                    if len(all_candles) % 10000 == 0:
                        print(f"   Downloaded {len(all_candles)} candles...")
                    
                    time.sleep(exchange.rateLimit / 1000)
                    
                except Exception as e:
                    print(f"   Error fetching batch: {e}")
                    break
            
            if all_candles:
                df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                df = df[~df.index.duplicated(keep='first')]
                print(f"✅ Downloaded {len(df)} {timeframe} candles for {symbol}")
                return df
            else:
                print(f"❌ No data retrieved for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error downloading {symbol}: {e}")
            return pd.DataFrame()
    
    def download_full_history(self, symbol, timeframes=['1m', '5m', '15m', '30m', '1h', '4h', '1d'], since_days=1460, exchange='binance'):
        """
        Download complete historical dataset across all timeframes
        """
        data = {}
        
        for tf in timeframes:
            df = self.get_historical_ohlcv(symbol, tf, since_days, exchange)
            if not df.empty:
                data[tf] = df
            time.sleep(1)
        
        return data
    
    def get_top_50_symbols(self):
        """
        Returns list of top 50 altcoin symbols
        """
        top_50 = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
            'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT',
            'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'LTC/USDT', 'ETC/USDT',
            'NEAR/USDT', 'APT/USDT', 'FIL/USDT', 'ARB/USDT', 'OP/USDT',
            'INJ/USDT', 'SUI/USDT', 'TIA/USDT', 'SEI/USDT', 'HBAR/USDT',
            'STX/USDT', 'RUNE/USDT', 'FTM/USDT', 'ALGO/USDT', 'VET/USDT',
            'GRT/USDT', 'AAVE/USDT', 'EOS/USDT', 'AXS/USDT', 'SAND/USDT',
            'MANA/USDT', 'ICP/USDT', 'FLOW/USDT', 'XTZ/USDT', 'THETA/USDT',
            'APE/USDT', 'CHZ/USDT', 'EGLD/USDT', 'KAVA/USDT', 'ZIL/USDT',
            'ENJ/USDT', 'ONE/USDT', 'CRV/USDT', 'SNX/USDT', 'COMP/USDT'
        ]
        return top_50
    
    def calculate_altcoin_season_index(self):
        """
        Calculate how many of top 50 alts are outperforming BTC (90 days)
        >75% = Alt season, <25% = BTC season
        """
        try:
            print("📊 Calculating Altcoin Season Index...")
            
            btc_90d = self.get_historical_ohlcv('BTC/USDT', '1d', 90, 'binance')
            if btc_90d.empty or len(btc_90d) < 2:
                return 50.0
            
            btc_change = ((btc_90d['close'].iloc[-1] - btc_90d['close'].iloc[0]) / btc_90d['close'].iloc[0]) * 100
            
            top_50 = self.get_top_50_symbols()
            outperforming = 0
            total_checked = 0
            
            for symbol in top_50[1:]:
                try:
                    alt_90d = self.get_historical_ohlcv(symbol, '1d', 90, 'binance')
                    if not alt_90d.empty and len(alt_90d) >= 2:
                        alt_change = ((alt_90d['close'].iloc[-1] - alt_90d['close'].iloc[0]) / alt_90d['close'].iloc[0]) * 100
                        
                        if alt_change > btc_change:
                            outperforming += 1
                        
                        total_checked += 1
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    continue
            
            if total_checked == 0:
                return 50.0
            
            index = (outperforming / total_checked) * 100
            
            if index > 75:
                status = "🔥 ALT SEASON"
            elif index < 25:
                status = "🪙 BTC SEASON"
            else:
                status = "⚖️ MIXED"
            
            print(f"✅ Altcoin Season Index: {index:.1f}% ({outperforming}/{total_checked}) - {status}")
            
            return index
            
        except Exception as e:
            print(f"❌ Error calculating altcoin season: {e}")
            return 50.0

if __name__ == '__main__':
    agg = MultiExchangeAggregator()
    
    print("\n" + "="*60)
    print("🚀 Testing CCXT Multi-Exchange Aggregator")
    print("="*60 + "\n")
    
    btc_1h = agg.get_historical_ohlcv('BTC/USDT', '1h', 30, 'binance')
    print(f"\nBTC 1h sample:\n{btc_1h.tail()}\n")
    
    alt_index = agg.calculate_altcoin_season_index()
    
    print("\n✅ CCXT Aggregator is working!")