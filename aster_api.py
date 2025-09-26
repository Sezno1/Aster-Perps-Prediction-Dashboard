"""
Aster DEX API client for direct API access
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, List
import config

class AsterAPI:
    def __init__(self):
        self.base_url = config.ASTER_DEX_API
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make GET request to Aster API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching from Aster API {endpoint}: {e}")
            return None
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get latest price for a symbol"""
        data = self._get('/fapi/v1/ticker/price', {'symbol': symbol})
        if data and 'price' in data:
            return float(data['price'])
        return None
    
    def get_24h_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24h ticker statistics"""
        data = self._get('/fapi/v1/ticker/24hr', {'symbol': symbol})
        if data:
            return {
                'price': float(data.get('lastPrice', 0)),
                'volume': float(data.get('volume', 0)),
                'quote_volume': float(data.get('quoteVolume', 0)),
                'price_change_percent': float(data.get('priceChangePercent', 0)),
                'high': float(data.get('highPrice', 0)),
                'low': float(data.get('lowPrice', 0)),
                'open': float(data.get('openPrice', 0))
            }
        return None
    
    def get_premium_index(self, symbol: str) -> Optional[Dict]:
        """Get mark price and funding rate"""
        data = self._get('/fapi/v1/premiumIndex', {'symbol': symbol})
        if data:
            return {
                'mark_price': float(data.get('markPrice', 0)),
                'index_price': float(data.get('indexPrice', 0)),
                'funding_rate': float(data.get('lastFundingRate', 0)),
                'next_funding_time': int(data.get('nextFundingTime', 0))
            }
        return None
    
    def get_funding_rate_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get historical funding rates"""
        data = self._get('/fapi/v1/fundingRate', {'symbol': symbol, 'limit': limit})
        if data and isinstance(data, list):
            return [
                {
                    'funding_rate': float(item.get('fundingRate', 0)),
                    'funding_time': int(item.get('fundingTime', 0)),
                    'symbol': item.get('symbol')
                }
                for item in data
            ]
        return []
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Get candlestick/kline data"""
        data = self._get('/fapi/v3/klines', {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        })
        
        if data and isinstance(data, list):
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df.set_index('timestamp', inplace=True)
            
            return df
        
        return pd.DataFrame()
    
    def get_orderbook(self, symbol: str, limit: int = 100) -> Optional[Dict]:
        """Get order book depth"""
        data = self._get('/fapi/v1/depth', {'symbol': symbol, 'limit': limit})
        if data:
            return {
                'bids': [[float(p), float(q)] for p, q in data.get('bids', [])],
                'asks': [[float(p), float(q)] for p, q in data.get('asks', [])],
                'last_update_id': data.get('lastUpdateId')
            }
        return None
    
    def get_open_interest(self, symbol: str) -> Optional[Dict]:
        """Get open interest statistics"""
        data = self._get('/fapi/v1/openInterest', {'symbol': symbol})
        if data:
            return {
                'open_interest': float(data.get('openInterest', 0)),
                'symbol': data.get('symbol'),
                'time': int(data.get('time', 0))
            }
        return None
    
    def get_book_ticker(self, symbol: str) -> Optional[Dict]:
        """Get best bid/ask prices"""
        data = self._get('/fapi/v1/ticker/bookTicker', {'symbol': symbol})
        if data:
            return {
                'bid_price': float(data.get('bidPrice', 0)),
                'bid_qty': float(data.get('bidQty', 0)),
                'ask_price': float(data.get('askPrice', 0)),
                'ask_qty': float(data.get('askQty', 0))
            }
        return None
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent trades for whale detection"""
        data = self._get('/fapi/v1/trades', {'symbol': symbol, 'limit': limit})
        if data and isinstance(data, list):
            return [
                {
                    'id': item.get('id'),
                    'price': float(item.get('price', 0)),
                    'qty': float(item.get('qty', 0)),
                    'quote_qty': float(item.get('quoteQty', 0)),
                    'time': int(item.get('time', 0)),
                    'is_buyer_maker': item.get('isBuyerMaker', False)
                }
                for item in data
            ]
        return []
    
    def get_aggregated_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get aggregated trades (better for whale detection)"""
        data = self._get('/fapi/v1/aggTrades', {'symbol': symbol, 'limit': limit})
        if data and isinstance(data, list):
            return [
                {
                    'agg_id': item.get('a'),
                    'price': float(item.get('p', 0)),
                    'qty': float(item.get('q', 0)),
                    'first_trade_id': item.get('f'),
                    'last_trade_id': item.get('l'),
                    'time': int(item.get('T', 0)),
                    'is_buyer_maker': item.get('m', False)
                }
                for item in data
            ]
        return []
    
    def get_all_aster_data(self, symbol: str = config.ASTER_SYMBOL, 
                           fetch_klines_1h: bool = True,
                           fetch_klines_4h: bool = True) -> Dict:
        """Get comprehensive Aster data from DEX API"""
        print(f"Fetching data from Aster DEX API for {symbol}...")
        
        ticker_24h = self.get_24h_ticker(symbol)
        premium_index = self.get_premium_index(symbol)
        funding_history = self.get_funding_rate_history(symbol, limit=10)
        oi_data = self.get_open_interest(symbol)
        orderbook = self.get_orderbook(symbol, limit=50)
        
        klines_1h = self.get_klines(symbol, '1h', 100) if fetch_klines_1h else pd.DataFrame()
        klines_4h = self.get_klines(symbol, '4h', 100) if fetch_klines_4h else pd.DataFrame()
        
        current_price = ticker_24h['price'] if ticker_24h else None
        funding_rate = premium_index['funding_rate'] if premium_index else None
        mark_price = premium_index['mark_price'] if premium_index else None
        open_interest = oi_data['open_interest'] if oi_data else None
        
        return {
            'price': current_price,
            'mark_price': mark_price,
            'funding_rate': funding_rate,
            'open_interest': open_interest,
            'ticker_24h': ticker_24h,
            'premium_index': premium_index,
            'funding_history': funding_history,
            'orderbook': orderbook,
            'klines_1h': klines_1h,
            'klines_4h': klines_4h,
            'timestamp': datetime.now()
        }