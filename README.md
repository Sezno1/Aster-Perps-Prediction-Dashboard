# ASTER Perpetual Futures Trading Dashboard

AI-powered paper trading dashboard for ASTER/USDT perpetual futures with real-time signal detection, pattern recognition, and machine learning.

## Features

- **Real-time Price Tracking** - 1-second updates for accurate market data
- **AI-Powered Signal Detection** - OpenAI GPT-4 analyzes market conditions and generates BUY/WAIT signals
- **Historical Pattern Learning** - Tracks all price movements, volume spikes, moon candles, and dip opportunities
- **Paper Trading** - Simulates trades with virtual positions, tracking P&L and learning from outcomes
- **Interactive Charts** - Live candlestick charts with multiple timeframes (1m - 1w)
- **Volume Analysis** - Detects volume spikes (>2x average) and trend changes
- **Dip Detection** - Identifies dip-bounce opportunities for optimal entry timing
- **Moon Candle Alerts** - Catches >5% price moves in <5 minutes
- **Audio Notifications** - Browser alert sounds when new trade signals trigger
- **User Controls** - Adjustable wallet size and leverage limits (10-50x)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sezno1/Aster-Perps-Prediction-Dashboard.git
cd Aster-Perps-Prediction-Dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
ASTER_API_KEY=your_aster_api_key_here
ASTER_API_SECRET=your_aster_api_secret_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Get API Keys:**
- **Aster DEX**: https://www.asterdex.com/account/api
- **OpenAI**: https://platform.openai.com/api-keys

### 4. Run the Dashboard

```bash
python app.py
```

Open your browser to: **http://localhost:5001**

## How It Works

### Paper Trading Logic

1. **SCANNING** - AI analyzes market data every 2 minutes, calculating signal strength (0-100)
2. **NEW BUY SIGNAL** - When signal strength >70 and conditions align, AI triggers BUY signal
3. **ENTRY WINDOW** - 60-second countdown gives you time to execute manually if desired
4. **POSITION OPEN** - Entry price, target, and stop-loss are locked and displayed
5. **POSITION CLOSE** - Automatically closes when target hit, stop-loss hit, or AI recommends exit
6. **LEARNING** - AI logs expected vs actual results to improve future predictions

### AI Decision Making

The AI considers:
- Technical indicators (RSI, MACD, momentum)
- Order flow analysis (bid/ask imbalance)
- Volume trends (5m vs 1h comparison)
- Support/resistance levels (24h history)
- Moon candles and dip-bounce patterns
- Historical win rate and past performance
- Time-of-day context (Tokyo/London/NY sessions)

### Pattern Recognition

The system automatically detects and logs:
- **Volume Spikes**: >2x average volume = increased volatility
- **Moon Candles**: >5% price moves in <5 minutes
- **Dip Bounces**: >0.3% dip followed by >0.2% bounce
- **Support/Resistance**: Price levels with 3+ tests

## Project Structure

```
├── app.py                     # Flask server + WebSocket backend
├── config.py                  # Configuration (reads from .env)
├── data_fetcher.py           # API data fetching
├── aster_api.py              # Aster DEX API client
├── indicators.py             # Technical indicators (RSI, MACD, etc.)
├── signal_engine.py          # Signal scoring logic
├── orderflow_analyzer.py     # Order book analysis
├── multi_strategy_engine.py  # Multi-strategy comparison
├── ai_analyzer.py            # OpenAI integration for decisions
├── ai_prediction_tracker.py  # Track AI predictions and outcomes
├── price_history.py          # Historical data database
├── templates/
│   └── dashboard.html        # Frontend UI
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore file
└── requirements.txt          # Python dependencies
```

## Databases (Auto-Created)

- **price_history.db** - All price ticks, volume metrics, patterns
- **ai_predictions.db** - AI predictions and trade outcomes
- **trade_journal.db** - Trade history (legacy)
- **leaderboard_data.db** - Whale tracker (placeholder)

## Cost

- **OpenAI API**: ~$0.25/day (GPT-4o-mini at 30 calls/hour)
- **Aster API**: Free tier available

## Troubleshooting

### Port 5001 Already in Use

```bash
lsof -ti:5001 | xargs kill -9
python app.py
```

### Missing Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### API Key Errors

Make sure your `.env` file exists and contains valid API keys. Check that `python-dotenv` is installed:

```bash
pip install python-dotenv
```

## Features in Development

- ✅ Real-time price updates (1 second)
- ✅ AI-powered signal detection
- ✅ Historical pattern learning
- ✅ Paper trading with position tracking
- ✅ Volume spike detection
- ✅ Moon candle alerts
- ✅ Dip-bounce detection
- ✅ Audio trade notifications
- ✅ User-controlled leverage limits
- 🔄 Multi-coin support (coming soon)
- 🔄 Live trading integration (coming soon)

## Contributing

Pull requests welcome! For major changes, please open an issue first.

## License

MIT

## Disclaimer

**This is a paper trading tool for educational purposes only.** It does not execute real trades. Always do your own research before trading with real money. Cryptocurrency trading carries significant risk.

## Support

For issues or questions, please open a GitHub issue at:
https://github.com/Sezno1/Aster-Perps-Prediction-Dashboard/issues
