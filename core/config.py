"""
Configuration file for ASTER Perp Long Signal Dashboard
"""
import os
from dotenv import load_dotenv

load_dotenv()

ASTER_SYMBOL = "ASTERUSDT"
BTC_SYMBOL = "BTCUSDT"
ETH_SYMBOL = "ETHUSDT"
BNB_SYMBOL = "BNBUSDT"

EXCHANGES = {
    'binance': 'binance',
    'bybit': 'bybit',
    'coingecko': 'coingecko'
}

TIMEFRAMES = {
    '1h': '1h',
    '4h': '4h'
}

RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_BULLISH_ZONE = (40, 60)

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

STOCH_PERIOD = 14
STOCH_SMOOTH = 3
STOCH_OVERSOLD = 20

SIGNAL_WEIGHTS = {
    'momentum': 0.4,
    'perp_metrics': 0.3,
    'market_context': 0.2,
    'sentiment': 0.1
}

LEVERAGE_RECOMMENDATIONS = {
    'strong': (80, 100, '30-50x'),
    'moderate': (60, 79, '10-20x'),
    'weak': (40, 59, '5-10x'),
    'no_entry': (0, 39, 'WAIT')
}

RISK_PER_TRADE = 0.01
DASHBOARD_UPDATE_INTERVAL = 60

FEAR_GREED_API = "https://api.alternative.me/fng/"
COINGECKO_API = "https://api.coingecko.com/api/v3"
ASTER_DEX_API = "https://fapi.asterdex.com"
ASTER_WEBSOCKET = "wss://fstream.asterdex.com"

ASTER_API_KEY = os.getenv("ASTER_API_KEY")
ASTER_API_SECRET = os.getenv("ASTER_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")