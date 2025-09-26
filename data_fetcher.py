"""
Data fetching module for crypto market data
"""

import ccxt
import requests
import pandas as pd
from datetime import datetime
import time
from typing import Dict, Optional, Tuple
import config
from aster_api import AsterAPI

class DataFetcher:
    def __init__(self):
        self.binance = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        self.aster_api = AsterAPI()
        self.coingecko_base = config.COINGECKO_API
        
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Fetch OHLCV data from Binance"""
        try:
            ohlcv = self.binance.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            ticker = self.binance.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_funding_rate(self, symbol: str) -> Optional[float]:
        """Get current funding rate for perpetual futures"""
        try:
            funding = self.binance.fetch_funding_rate(symbol)
            return funding['fundingRate'] if funding else None
        except Exception as e:
            print(f"Error fetching funding rate for {symbol}: {e}")
            return None
    
    def get_open_interest(self, symbol: str) -> Optional[float]:
        """Get open interest for a symbol"""
        try:
            oi = self.binance.fetch_open_interest(symbol)
            return oi['openInterest'] if oi else None
        except Exception as e:
            print(f"Error fetching open interest for {symbol}: {e}")
            return None
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """Fetch Fear & Greed Index from Alternative.me"""
        try:
            response = requests.get(config.FEAR_GREED_API, timeout=10)
            data = response.json()
            if data and 'data' in data and len(data['data']) > 0:
                latest = data['data'][0]
                return {
                    'value': int(latest['value']),
                    'classification': latest['value_classification']
                }
            return None
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
            return None
    
    def get_coingecko_price(self, coin_id: str = 'aster-2') -> Optional[Dict]:
        """Fetch price data from CoinGecko (backup)"""
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if coin_id in data:
                return {
                    'price': data[coin_id].get('usd'),
                    'volume_24h': data[coin_id].get('usd_24h_vol'),
                    'change_24h': data[coin_id].get('usd_24h_change'),
                    'market_cap': data[coin_id].get('usd_market_cap')
                }
            return None
        except Exception as e:
            print(f"Error fetching CoinGecko data: {e}")
            return None
    
    def get_btc_dominance(self) -> Optional[float]:
        """Calculate BTC dominance"""
        try:
            url = f"{self.coingecko_base}/global"
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'data' in data and 'market_cap_percentage' in data['data']:
                return data['data']['market_cap_percentage'].get('btc')
            return None
        except Exception as e:
            print(f"Error fetching BTC dominance: {e}")
            return None
    
    def get_eth_btc_ratio(self) -> Optional[float]:
        """Calculate ETH/BTC ratio"""
        try:
            eth_price = self.get_current_price(config.ETH_SYMBOL)
            btc_price = self.get_current_price(config.BTC_SYMBOL)
            if eth_price and btc_price:
                return eth_price / btc_price
            return None
        except Exception as e:
            print(f"Error calculating ETH/BTC ratio: {e}")
            return None
    
    def get_all_market_data(self) -> Dict:
        """Fetch all required market data"""
        print("Fetching market data...")
        
        aster_data = self.aster_api.get_all_aster_data(config.ASTER_SYMBOL)
        
        btc_price = self.get_current_price(config.BTC_SYMBOL)
        eth_price = self.get_current_price(config.ETH_SYMBOL)
        bnb_price = self.get_current_price(config.BNB_SYMBOL)
        
        btc_funding = self.get_funding_rate(config.BTC_SYMBOL)
        
        eth_btc_ratio = eth_price / btc_price if eth_price and btc_price else None
        btc_dominance = self.get_btc_dominance()
        
        fear_greed = self.get_fear_greed_index()
        
        btc_1h = self.get_ohlcv(config.BTC_SYMBOL, '1h', 100)
        btc_4h = self.get_ohlcv(config.BTC_SYMBOL, '4h', 100)
        
        return {
            'prices': {
                'aster': aster_data.get('price'),
                'btc': btc_price,
                'eth': eth_price,
                'bnb': bnb_price
            },
            'perp_metrics': {
                'aster_funding': aster_data.get('funding_rate'),
                'btc_funding': btc_funding,
                'aster_oi': aster_data.get('open_interest'),
                'aster_mark_price': aster_data.get('mark_price'),
                'aster_ticker_24h': aster_data.get('ticker_24h'),
                'aster_orderbook': aster_data.get('orderbook')
            },
            'market_context': {
                'eth_btc_ratio': eth_btc_ratio,
                'btc_dominance': btc_dominance
            },
            'sentiment': fear_greed,
            'ohlcv': {
                'aster_1h': aster_data.get('klines_1h', pd.DataFrame()),
                'aster_4h': aster_data.get('klines_4h', pd.DataFrame()),
                'btc_1h': btc_1h,
                'btc_4h': btc_4h
            },
            'aster_full_data': aster_data,
            'timestamp': datetime.now()
        }