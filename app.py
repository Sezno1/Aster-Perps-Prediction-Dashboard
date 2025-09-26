"""
ASTER Trading Dashboard - Flask + WebSocket
Clean UI with smooth number updates, no page refreshes
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import sqlite3
from datetime import datetime
import config
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
from signal_engine import SignalEngine
from orderflow_analyzer import OrderFlowAnalyzer
from multi_strategy_engine import MultiStrategyEngine
from ai_analyzer import AIAnalyzer
from ai_prediction_tracker import AIPredictionTracker
from price_history import PriceHistoryDB
from whale_tracker import WhaleTracker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aster-scanner-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
fetcher = DataFetcher()
orderflow = OrderFlowAnalyzer(fetcher.aster_api)
multi_strat = MultiStrategyEngine()
pred_tracker = AIPredictionTracker()
ai = AIAnalyzer(api_key=config.OPENAI_API_KEY, prediction_tracker=pred_tracker)
price_history = PriceHistoryDB()
whale_tracker = WhaleTracker(whale_threshold_usd=5000)

last_ai_run = datetime.now()
cached_ai = None
active_position = None  # Track if we have an open position: {'entry_price': X, 'entry_time': Y, 'leverage': Z, 'target': T, 'stop': S, 'prediction_id': ID}
current_wallet_size = 10.0  # Default wallet size, updated from UI
max_leverage = 25  # Maximum leverage AI can use, updated from UI
last_volume_calc = datetime.now()
last_moon_check = datetime.now()

def get_time_of_day_context():
    """Analyze time patterns - when do different markets trade?"""
    from datetime import datetime
    import pytz
    
    now_utc = datetime.now(pytz.UTC)
    
    # Major trading sessions
    tokyo_time = now_utc.astimezone(pytz.timezone('Asia/Tokyo'))
    london_time = now_utc.astimezone(pytz.timezone('Europe/London'))
    ny_time = now_utc.astimezone(pytz.timezone('America/New_York'))
    
    context = {
        'hour_utc': now_utc.hour,
        'tokyo_hour': tokyo_time.hour,
        'london_hour': london_time.hour,
        'ny_hour': ny_time.hour,
        'tokyo_active': 0 <= tokyo_time.hour < 15,  # Tokyo 9am-midnight
        'london_active': 7 <= london_time.hour < 16,  # London 8am-5pm
        'ny_active': 8 <= ny_time.hour < 17,  # NY 9am-6pm
        'overlap_london_ny': (7 <= london_time.hour < 16) and (8 <= ny_time.hour < 17),  # Highest volume
        'weekend': now_utc.weekday() >= 5,
        'description': ''
    }
    
    # Generate description
    if context['overlap_london_ny']:
        context['description'] = "🔥 Peak hours: London/NY overlap - High volume expected"
    elif context['tokyo_active']:
        context['description'] = "🇯🇵 Asia session: Tokyo market active"
    elif context['london_active']:
        context['description'] = "🇬🇧 Europe session: London market active"
    elif context['ny_active']:
        context['description'] = "🇺🇸 US session: NY market active"
    else:
        context['description'] = "😴 Off-hours: Low volume expected"
    
    if context['weekend']:
        context['description'] += " (Weekend - crypto only)"
    
    return context

def get_scanner_data():
    """Fetch all scanner data"""
    global last_ai_run, cached_ai, active_position, current_wallet_size, max_leverage, last_volume_calc, last_moon_check
    
    try:
        market_data = fetcher.get_all_market_data()
        current_price = market_data['prices']['aster']
        
        # Log price tick to historical database
        ticker_data = market_data.get('aster_full_data', {}).get('ticker_24h', {})
        price_history.log_price_tick(
            price=current_price,
            volume_1m=ticker_data.get('volume', 0),
            mark_price=ticker_data.get('mark_price'),
            funding_rate=market_data.get('perp_metrics', {}).get('funding_rate')
        )
        
        # Calculate volume metrics every 5 minutes
        now = datetime.now()
        if (now - last_volume_calc).total_seconds() >= 300:
            volume_metrics = price_history.calculate_volume_metrics()
            last_volume_calc = now
        else:
            volume_metrics = None
        
        # Check for moon candles and dip opportunities every 30 seconds
        moon_candle = None
        dip_opportunity = None
        if (now - last_moon_check).total_seconds() >= 30:
            moon_candle = price_history.detect_moon_candle()
            dip_opportunity = price_history.detect_dip_opportunity()
            
            if moon_candle.get('detected') and moon_candle['type'] in ['MOON_CANDLE', 'PUMP']:
                price_history.log_pattern_event(
                    pattern_type=moon_candle['type'],
                    price_start=moon_candle['start_price'],
                    price_end=moon_candle['current_price'],
                    duration_seconds=moon_candle.get('duration_seconds', 0),
                    volume_spike=True,
                    description=f"{moon_candle['price_change_pct']:.1f}% move detected"
                )
            
            if dip_opportunity.get('detected'):
                price_history.log_pattern_event(
                    pattern_type='DIP_BOUNCE',
                    price_start=dip_opportunity['dip_price'],
                    price_end=dip_opportunity['current_price'],
                    duration_seconds=180,
                    volume_spike=False,
                    description=f"Dip {dip_opportunity['dip_depth']:.1f}% → Bounce {dip_opportunity['bounce_pct']:.1f}%"
                )
            
            last_moon_check = now
        
        # Get volume trend analysis (safe fallback)
        try:
            volume_trend = price_history.get_volume_trend()
        except Exception:
            volume_trend = {'spike_detected': False, 'trend': 'UNKNOWN', 'multiplier': 0}
        
        # Analyze whale trades every cycle
        recent_trades = fetcher.aster_api.get_aggregated_trades(config.ASTER_SYMBOL, limit=50)
        whale_analysis = whale_tracker.analyze_trades(recent_trades, current_price)
        
        momentum = TechnicalIndicators.get_momentum_score(
            market_data['ohlcv']['aster_1h'],
            market_data['ohlcv']['aster_4h']
        )
        perp = SignalEngine.score_perp_metrics(market_data['perp_metrics'])
        market_ctx = SignalEngine.score_market_context(
            market_data['market_context'],
            market_data['ohlcv']['btc_1h'],
            market_data['ohlcv']['btc_4h']
        )
        sentiment = SignalEngine.score_sentiment(market_data['sentiment'])
        signal_results = SignalEngine.calculate_composite_score(momentum, perp, market_ctx, sentiment)
        
        orderflow_analysis = orderflow.analyze_orderbook(config.ASTER_SYMBOL, depth=100)
        opportunities = multi_strat.analyze_all_opportunities(market_data, signal_results, orderflow_analysis)
        
        # Get support/resistance and pattern analysis from historical data
        try:
            support_resistance = price_history.detect_support_resistance(lookback_hours=24)
            recent_patterns = price_history.get_recent_patterns(hours=24)
            pattern_summary = price_history.get_learning_summary()
        except Exception:
            support_resistance = {'support': None, 'resistance': None}
            recent_patterns = {}
            pattern_summary = "Building pattern database..."
        
        # AI runs every 2 minutes and MAKES THE FINAL DECISION
        now = datetime.now()
        if (now - last_ai_run).total_seconds() >= 120 or not cached_ai:
            whale_sentiment = {'sentiment': 'NEUTRAL', 'score': 50}
            
            # Enhanced context with historical data
            historical_context = {
                'volume_trend': volume_trend,
                'moon_candle': moon_candle,
                'dip_opportunity': dip_opportunity,
                'support_resistance': support_resistance,
                'recent_patterns': recent_patterns,
                'pattern_summary': pattern_summary,
                'whale_analysis': whale_analysis
            }
            
            ai_analysis = ai.analyze_market_conditions(market_data, signal_results, orderflow_analysis, whale_sentiment, historical_context)
            prediction_id = pred_tracker.log_prediction({}, market_data, signal_results, orderflow_analysis, whale_sentiment, ai_analysis, current_wallet_size)
            cached_ai = ai_analysis
            cached_ai['prediction_id'] = prediction_id  # Store for position tracking
            last_ai_run = now
        else:
            ai_analysis = cached_ai
        
        pred_tracker.update_prediction_outcomes(current_price)
        best = opportunities['best_strategy']
        
        # Get time context for AI
        time_context = get_time_of_day_context()
        
        # AI MAKES THE FINAL DECISION - overrides strategy
        ai_recommendation = ai_analysis.get('recommendation', 'WAIT')
        is_buy_signal = ai_recommendation in ['BUY_NOW', 'STRONG_BUY']
        
        # If AI says buy, use AI's leverage recommendation but cap at user's max_leverage
        if is_buy_signal and 'leverage' in ai_analysis:
            best['leverage'] = min(max_leverage, max(10, ai_analysis['leverage']))
        else:
            best['leverage'] = min(max_leverage, best['leverage'])
        
        # Check if we should OPEN a new position
        entry_window_seconds = None
        if is_buy_signal and active_position is None:
            # AI wants to BUY - open position with 60-second entry window
            active_position = {
                'entry_price': best['entry_price'],
                'entry_time': datetime.now(),
                'leverage': best['leverage'],
                'target_price': best['exit_price'],
                'stop_price': best['stop_loss'],
                'strategy': best['strategy'],
                'prediction_id': ai_analysis.get('prediction_id'),
                'entry_window_start': datetime.now()
            }
            entry_window_seconds = 60
        elif active_position and active_position.get('entry_window_start'):
            # Calculate remaining entry window
            elapsed = (datetime.now() - active_position['entry_window_start']).total_seconds()
            entry_window_seconds = max(0, 60 - elapsed)
            if entry_window_seconds <= 0:
                # Window expired, clear the window marker
                active_position.pop('entry_window_start', None)
        
        # Check if we should CLOSE active position
        elif active_position is not None:
            exit_reason = None
            exit_price = None
            
            # We have an open position - check if we hit target or stop
            if current_price >= active_position['target_price']:
                exit_reason = "TARGET_HIT"
                exit_price = current_price
            elif current_price <= active_position['stop_price']:
                exit_reason = "STOP_LOSS"
                exit_price = current_price
            elif ai_recommendation in ['DONT_BUY', 'SELL']:
                exit_reason = "AI_CLOSE"
                exit_price = current_price
            
            # Log the actual trade result
            if exit_reason and active_position.get('prediction_id'):
                entry_time = active_position['entry_time']
                hold_time = (datetime.now() - entry_time).total_seconds() / 3600
                
                actual_profit = pred_tracker.log_actual_trade_result(
                    prediction_id=active_position['prediction_id'],
                    entry_price=active_position['entry_price'],
                    exit_price=exit_price,
                    exit_reason=exit_reason,
                    hold_time_hours=hold_time,
                    wallet_size=current_wallet_size,
                    leverage=active_position['leverage']
                )
                active_position = None
        
        # Display logic: Show GREEN while position is open, RED when no position
        display_buy_signal = active_position is not None
        
        insights = pred_tracker.get_learning_insights()
        
        # Get AI reasoning if available
        ai_reasoning = f"AI Decision: {ai_recommendation}. "
        if cached_ai and 'reasoning' in cached_ai:
            ai_reasoning += cached_ai.get('reasoning', '')
        else:
            ai_reasoning += f"Strategy: {best['strategy']}. {best['reasoning']}"
        
        # Get 24h volume from Aster ticker data
        ticker_24h = market_data.get('aster_full_data', {}).get('ticker_24h', {})
        volume_24h = ticker_24h.get('quote_volume', 0)
        
        # Add volume trend info and moon candle alert
        volume_info = ''
        if volume_trend and volume_trend['spike_detected']:
            volume_info = f" 🔥 VOLUME SPIKE: {volume_trend['multiplier']:.1f}x average"
        
        moon_alert = ''
        if moon_candle and moon_candle.get('detected') and moon_candle['type'] == 'MOON_CANDLE':
            moon_alert = f" 🌙 MOON CANDLE: +{moon_candle['price_change_pct']:.1f}% in 5min!"
        
        # Get recent whale trades for display
        whale_activity = whale_tracker.get_recent_whales(minutes=60, limit=5)
        if not whale_activity:
            whale_activity = [{'action': 'No whale trades detected', 'amount': 'Last 60min', 'type': 'neutral'}]
        
        # Get recent AI predictions for trade log - ONLY BUY/SELL decisions (not WAIT)
        trade_log = []
        try:
            import sqlite3
            conn = sqlite3.connect('ai_predictions.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, recommendation, current_price, entry_price, leverage, confidence, outcome
                FROM predictions 
                WHERE recommendation IN ('BUY_NOW', 'STRONG_BUY', 'SELL', 'CLOSE_POSITION')
                ORDER BY timestamp DESC LIMIT 10
            """)
            for row in cursor.fetchall():
                trade_log.append({
                    'time': row[0][:19] if row[0] else '',
                    'action': row[1] or 'WAIT',
                    'price': f"${row[2]:.6f}" if row[2] else 'N/A',
                    'leverage': f"{row[4]}x" if row[4] else 'N/A',
                    'confidence': f"{row[5]:.0f}%" if row[5] else 'N/A',
                    'outcome': row[6] or 'Pending'
                })
            conn.close()
        except Exception as e:
            pass
        
        # If we have an active position, use its prices for display
        if active_position:
            display_entry = active_position['entry_price']
            display_target = active_position['target_price']
            display_stop = active_position['stop_price']
            display_leverage = active_position['leverage']
            display_strategy = active_position['strategy']
        else:
            display_entry = best['entry_price']
            display_target = best['exit_price']
            display_stop = best['stop_loss']
            display_leverage = best['leverage']
            display_strategy = best['strategy']
        
        return {
            'current_price': current_price,
            'is_buy_signal': display_buy_signal,
            'buy_price': display_entry,
            'sell_price': display_target,
            'stop_price': display_stop,
            'leverage': display_leverage,
            'confidence': best['confidence'],
            'strategy': display_strategy,
            'timeframe': best['timeframe'],
            'reasoning': best['reasoning'],
            'target_profit_pct': best['target_profit_pct'],
            'signal_strength': signal_results['composite_score'],
            'orderflow_imbalance': orderflow_analysis.get('imbalance_score', 0),
            'ai_accuracy': insights['accuracy'] if insights['has_data'] else 0,
            'ai_predictions': insights['total_predictions'] if insights['has_data'] else 0,
            'ai_reasoning': ai_reasoning,
            'ai_recommendation': ai_recommendation,
            'volume_24h': volume_24h,
            'whale_activity': whale_activity,
            'trade_log': trade_log,
            'time_context': time_context['description'] + volume_info + moon_alert,
            'has_active_position': active_position is not None,
            'volume_trend': volume_trend,
            'moon_candle': moon_candle,
            'entry_window_seconds': entry_window_seconds,
            'pattern_summary': pattern_summary,
            'whale_analysis': whale_analysis,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    except Exception as e:
        return None

def background_updates():
    """Background thread to push updates every 1 second for real-time price"""
    while True:
        time.sleep(1)  # Update every 1 second for real-time accuracy
        data = get_scanner_data()
        if data:
            socketio.emit('update', data, namespace='/')

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint for initial data load"""
    data = get_scanner_data()
    return jsonify(data) if data else jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/api/chart-data')
def get_chart_data():
    """Get chart candle data directly from Aster DEX API"""
    try:
        from flask import request
        timeframe = request.args.get('timeframe', '15m')
        
        # Fetch directly from Aster API
        chart_data = fetcher.aster_api.get_klines(config.ASTER_SYMBOL, timeframe, 200)
        
        if not chart_data.empty:
            candles = []
            for timestamp, row in chart_data.iterrows():
                candles.append({
                    'time': int(timestamp.timestamp()),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close'])
                })
            return jsonify(candles)
        return jsonify([])
    except Exception as e:
        return jsonify([])

@socketio.on('connect')
def handle_connect():
    data = get_scanner_data()
    if data:
        emit('update', data)

@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('update_wallet')
def handle_wallet_update(data):
    """Update wallet size from UI"""
    global current_wallet_size
    try:
        new_wallet = float(data.get('wallet', 10.0))
        if new_wallet > 0:
            current_wallet_size = new_wallet
    except Exception as e:
        pass

@socketio.on('update_leverage')
def handle_leverage_update(data):
    """Update max leverage from UI"""
    global max_leverage
    try:
        new_leverage = int(data.get('max_leverage', 25))
        if 10 <= new_leverage <= 50:
            max_leverage = new_leverage
    except Exception as e:
        pass

def startup_recovery():
    """On startup, backfill missed data and restore state"""
    print("🔄 Checking for missed data during downtime...")
    
    try:
        conn = sqlite3.connect('price_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM price_ticks")
        last_tick = cursor.fetchone()[0]
        conn.close()
        
        if last_tick:
            last_time = datetime.fromisoformat(last_tick)
            downtime_minutes = (datetime.now() - last_time).total_seconds() / 60
            
            if downtime_minutes > 2:
                print(f"📥 Scanner was offline for {downtime_minutes:.1f} minutes")
                print("📊 Fetching historical candles to fill gaps...")
                
                chart_data = fetcher.aster_api.get_klines(config.ASTER_SYMBOL, '1m', int(min(downtime_minutes, 1000)))
                if not chart_data.empty:
                    backfilled = 0
                    for timestamp, row in chart_data.iterrows():
                        if timestamp > last_time:
                            price_history.log_price_tick(
                                price=float(row['close']),
                                volume_1m=float(row['volume']),
                                mark_price=None,
                                funding_rate=None
                            )
                            backfilled += 1
                    print(f"✅ Backfilled {backfilled} price ticks from Aster API")
                
                price_history.calculate_volume_metrics()
                print("✅ Volume metrics recalculated")
            else:
                print("✅ No significant downtime detected")
        
        conn = sqlite3.connect('ai_predictions.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM predictions 
            WHERE recommendation IN ('BUY_NOW', 'STRONG_BUY', 'SELL')
        """)
        trade_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE outcome = 'WIN'")
        win_count = cursor.fetchone()[0]
        
        win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0
        conn.close()
        
        print(f"📈 AI Learning Stats: {trade_count} trades, {win_rate:.1f}% win rate")
        
    except Exception as e:
        print(f"⚠️ Startup recovery encountered issue: {e}")
        print("✅ Continuing with fresh data collection...")

if __name__ == '__main__':
    import os
    
    print("\n" + "="*60)
    print("🚀 ASTER Scanner Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("💰 Cost: ~$0.25/day")
    print("="*60 + "\n")
    
    startup_recovery()
    
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    port = int(os.environ.get('PORT', 5001))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)