"""
ASTER Trading Dashboard - Flask + WebSocket
Clean UI with smooth number updates, no page refreshes
"""

import sys
import os
# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import sqlite3
from datetime import datetime
from core.config import *
from tentacles.market_data.data_fetcher import DataFetcher
from tentacles.technical.indicators import TechnicalIndicators
from tentacles.technical.signal_engine import SignalEngine
from tentacles.technical.orderflow_analyzer import OrderFlowAnalyzer
from tentacles.intelligence.multi_strategy_engine import MultiStrategyEngine
from brain.ai_analyzer import AIAnalyzer
from tentacles.intelligence.ai_prediction_tracker import AIPredictionTracker
from tentacles.pattern_analysis.price_history import PriceHistoryDB
from tentacles.market_data.whale_tracker import WhaleTracker
from tentacles.technical.advanced_indicators import AdvancedIndicators
from brain.master_brain_integration import master_brain
from brain.unified_confidence_system import unified_confidence
from tentacles.astrological.astro_psychology_integration import astro_psychology

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'aster-scanner-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def enhance_advanced_signals_for_tentacles(advanced_signals, current_price, klines_1m):
    """Enhance advanced_signals with properly formatted data for unified confidence tentacles"""
    try:
        enhanced = advanced_signals.copy()
        
        # Add Bollinger Bands data for advanced indicators tentacle
        if 'bb' in advanced_signals and advanced_signals['bb']:
            bb_data = advanced_signals['bb']
            enhanced['bollinger_upper'] = bb_data.get('upper', 0)
            enhanced['bollinger_lower'] = bb_data.get('lower', 0)
            enhanced['bollinger_middle'] = bb_data.get('middle', 0)
        
        # Add candlestick pattern for advanced indicators tentacle
        if 'candlestick' in advanced_signals and advanced_signals['candlestick']:
            candlestick_data = advanced_signals['candlestick']
            enhanced['candlestick_pattern'] = candlestick_data.get('pattern', 'NONE')
        else:
            enhanced['candlestick_pattern'] = 'NONE'
            
        # Add wick analysis
        if 'wick' in advanced_signals and advanced_signals['wick']:
            wick_data = advanced_signals['wick']
            enhanced['wick_ratio'] = wick_data.get('wick_ratio', 0)
        else:
            enhanced['wick_ratio'] = 0
            
        return enhanced
    except Exception as e:
        print(f"Error enhancing advanced signals: {e}")
        return advanced_signals

def generate_cross_market_analysis(master_brain_analysis):
    """Generate cross-market analysis data for cross-market tentacle"""
    try:
        # Extract BTC cycle data for synthetic cross-market analysis
        cycle_data = master_brain_analysis.get('btc_cycle', {})
        cycle_phase = cycle_data.get('cycle_phase', 'UNKNOWN')
        
        # Generate synthetic S&P 500, DXY, VIX data based on cycle phase
        if cycle_phase in ['BULL_MARKET_PHASE_1', 'BULL_MARKET_PARABOLIC']:
            # Bull market = generally positive macro environment
            sp500_change = 0.8  # Positive S&P
            dxy_change = -0.3   # Weakening dollar
            vix_level = 18      # Lower fear
        elif cycle_phase in ['BEAR_MARKET', 'DISTRIBUTION_TOP']:
            # Bear market = generally negative macro environment
            sp500_change = -1.2  # Negative S&P
            dxy_change = 0.4     # Strengthening dollar
            vix_level = 28       # Higher fear
        else:
            # Neutral/accumulation phase
            sp500_change = 0.1
            dxy_change = 0.1
            vix_level = 22
            
        return {
            'sp500_change_24h': sp500_change,
            'dxy_change_24h': dxy_change,
            'vix_level': vix_level,
            'cycle_based': True,
            'cycle_phase': cycle_phase
        }
    except Exception as e:
        print(f"Error generating cross-market analysis: {e}")
        return {
            'sp500_change_24h': 0,
            'dxy_change_24h': 0,
            'vix_level': 20,
            'error': str(e)
        }

# Global state
fetcher = DataFetcher()
orderflow = OrderFlowAnalyzer(fetcher.aster_api)
multi_strat = MultiStrategyEngine()
pred_tracker = AIPredictionTracker()
ai = AIAnalyzer(api_key=OPENAI_API_KEY, prediction_tracker=pred_tracker)
price_history = PriceHistoryDB()
whale_tracker = WhaleTracker(whale_threshold_usd=5000)

last_ai_run = datetime.now()
cached_ai = None
active_position = None  # Track if we have an open position: {'entry_price': X, 'entry_time': Y, 'leverage': Z, 'target': T, 'stop': S, 'prediction_id': ID}
current_wallet_size = 10.0  # Default wallet size, updated from UI
max_leverage = 25  # Maximum leverage AI can use, updated from UI
last_volume_calc = datetime.now()
last_moon_check = datetime.now()

def sanitize_datetimes(obj):
    """Convert datetime objects to strings and ensure JSON serializable"""
    import numpy as np
    import pandas as pd
    
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, (np.bool_, pd.Series)):
        return bool(obj)
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, (bool, int, float, str, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_datetimes(item) for item in obj]
    else:
        # Convert any non-serializable objects to string
        return str(obj)

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
        ticker_data = market_data.get('aster_full_data', {}).get('ticker_24h', {}) or {}
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
        recent_trades = fetcher.aster_api.get_aggregated_trades(ASTER_SYMBOL, limit=50)
        whale_analysis = whale_tracker.analyze_trades(recent_trades, current_price)
        
        # Get support/resistance early (needed for wick analysis)
        try:
            support_resistance = price_history.detect_support_resistance(lookback_hours=24)
        except Exception:
            support_resistance = {'support': None, 'resistance': None}
        
        # Advanced indicators analysis
        klines_1m = market_data['ohlcv']['aster_1h']  # Will use this as proxy for patterns
        klines_5m = fetcher.aster_api.get_klines(ASTER_SYMBOL, '5m', 50)
        klines_15m = fetcher.aster_api.get_klines(ASTER_SYMBOL, '15m', 50)
        
        advanced_signals = {}
        
        # 1. Candlestick patterns
        if not klines_1m.empty:
            advanced_signals['candlestick'] = AdvancedIndicators.detect_candlestick_patterns(klines_1m.tail(10))
        
        # 2. Wick analysis
        if not klines_1m.empty:
            sr = support_resistance if support_resistance else {}
            advanced_signals['wick'] = AdvancedIndicators.analyze_wicks(
                klines_1m.tail(5), 
                support=sr.get('support'),
                resistance=sr.get('resistance')
            )
        
        # 3. Multi-timeframe confirmation
        if not klines_1m.empty and not klines_5m.empty and not klines_15m.empty:
            ma_1m = klines_1m['close'].rolling(window=20).mean().iloc[-1] if len(klines_1m) >= 20 else current_price
            ma_5m = klines_5m['close'].rolling(window=20).mean().iloc[-1] if len(klines_5m) >= 20 else current_price
            ma_15m = klines_15m['close'].rolling(window=20).mean().iloc[-1] if len(klines_15m) >= 20 else current_price
            
            advanced_signals['multi_tf'] = AdvancedIndicators.multi_timeframe_confirmation(
                current_price, current_price, current_price,
                ma_1m, ma_5m, ma_15m
            )
        
        # 4. EMA Crossover
        if not klines_1m.empty and len(klines_1m) >= 21:
            advanced_signals['ema'] = AdvancedIndicators.ema_crossover(klines_1m, fast_period=9, slow_period=21)
        
        # 5. Bollinger Bands
        if not klines_1m.empty and len(klines_1m) >= 20:
            advanced_signals['bb'] = AdvancedIndicators.bollinger_bands(klines_1m, period=20, std_dev=2.0)
        
        # 6. RSI Divergence
        if not klines_1m.empty and len(klines_1m) >= 24:
            advanced_signals['rsi'] = AdvancedIndicators.rsi_divergence(klines_1m, period=14)
        
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
        
        orderflow_analysis = orderflow.analyze_orderbook(ASTER_SYMBOL, depth=100)
        opportunities = multi_strat.analyze_all_opportunities(market_data, signal_results, orderflow_analysis)
        
        # Get pattern analysis from historical data
        try:
            recent_patterns = price_history.get_recent_patterns(hours=24)
            pattern_summary = price_history.get_learning_summary()
        except Exception:
            recent_patterns = {}
            pattern_summary = "Building pattern database..."
        
        # Get Master Brain context first
        master_brain_context = master_brain.get_enhanced_context()
        
        # Calculate Unified Confidence Score (ALL tentacles) with REAL data
        
        # Get actual technical indicators
        klines_current = market_data['ohlcv']['aster_1h'] if not market_data['ohlcv']['aster_1h'].empty else None
        current_rsi = 50  # Default
        trend_bullish = False
        price_above_ema9 = False
        price_above_ema21 = False
        
        if klines_current is not None and len(klines_current) >= 21:
            # Calculate actual RSI
            closes = klines_current['close'].values
            if len(closes) >= 14:
                deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                avg_gain = sum(gains[-14:]) / 14
                avg_loss = sum(losses[-14:]) / 14
                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    current_rsi = 100 - (100 / (1 + rs))
            
            # Calculate EMAs
            ema9 = klines_current['close'].ewm(span=9).mean().iloc[-1]
            ema21 = klines_current['close'].ewm(span=21).mean().iloc[-1]
            price_above_ema9 = current_price > ema9
            price_above_ema21 = current_price > ema21
            trend_bullish = price_above_ema9 and price_above_ema21
        
        # Enhanced Market Regime Detection with multiple indicators
        # Multiple regime factors
        regime_score = 0
        regime_indicators = {}
        
        # 1. Trend strength (EMA alignment)
        ema_alignment = 0
        if price_above_ema9 and price_above_ema21:
            ema_alignment = 2  # Strong bullish alignment
        elif price_above_ema9:
            ema_alignment = 1  # Moderate bullish
        elif not price_above_ema21:
            ema_alignment = -2  # Strong bearish
        else:
            ema_alignment = -1  # Moderate bearish
        
        regime_indicators['ema_alignment'] = ema_alignment
        regime_score += ema_alignment
        
        # 2. Volume patterns
        volume_factor = 0
        vol_multiplier = volume_trend.get('multiplier', 1.0)
        if vol_multiplier > 3.0:
            volume_factor = 2  # Very high volume
        elif vol_multiplier > 2.0:
            volume_factor = 1  # High volume
        elif vol_multiplier < 0.5:
            volume_factor = -1  # Low volume
        
        regime_indicators['volume_factor'] = volume_factor
        
        # 3. Price volatility (based on recent price changes)
        volatility_score = 0
        price_change_abs = abs(price_change_pct) if 'price_change_pct' in locals() else 0
        if price_change_abs > 5:
            volatility_score = 2  # High volatility
        elif price_change_abs > 2:
            volatility_score = 1  # Medium volatility
        elif price_change_abs < 0.5:
            volatility_score = -1  # Low volatility (ranging)
        
        regime_indicators['volatility'] = volatility_score
        
        # 4. RSI regime indicator
        rsi_regime = 0
        if current_rsi < 30 or current_rsi > 70:
            rsi_regime = 1  # Extreme readings = trending
        elif 40 <= current_rsi <= 60:
            rsi_regime = -1  # Neutral RSI = ranging
        
        regime_indicators['rsi_regime'] = rsi_regime
        
        # 5. Whale activity influence
        whale_regime = 0
        whale_buys = len(whale_analysis.get('whale_buys', []))
        whale_sells = len(whale_analysis.get('whale_sells', []))
        if whale_buys > whale_sells + 1:
            whale_regime = 1  # Whale accumulation
        elif whale_sells > whale_buys + 1:
            whale_regime = -1  # Whale distribution
            
        regime_indicators['whale_activity'] = whale_regime
        
        # Calculate final regime
        total_score = regime_score + volume_factor + volatility_score + rsi_regime + whale_regime
        
        # Determine regime based on multiple factors
        if total_score >= 4 and trend_bullish:
            market_regime_actual = 'STRONG_TRENDING_UP'
        elif total_score >= 2 and trend_bullish:
            market_regime_actual = 'TRENDING_UP'
        elif total_score <= -4 and not trend_bullish:
            market_regime_actual = 'STRONG_TRENDING_DOWN'
        elif total_score <= -2 and not trend_bullish:
            market_regime_actual = 'TRENDING_DOWN'
        elif volatility_score >= 2 or vol_multiplier > 2.5:
            market_regime_actual = 'VOLATILE_BREAKOUT'
        elif abs(total_score) <= 1 and volatility_score <= 0:
            market_regime_actual = 'RANGING'
        else:
            market_regime_actual = 'TRANSITIONING'
        
        regime_score = total_score
            
        # Add pattern library analysis for pattern recognition tentacles
        try:
            from pattern_library import pattern_library
            pattern_matches = pattern_library.get_current_matches(current_price, volume_24h_change_pct)
            pattern_analysis = {
                'pattern_matches': pattern_matches if pattern_matches else [],
                'best_pattern': pattern_matches[0] if pattern_matches else None,
                'total_patterns': len(pattern_matches) if pattern_matches else 0
            }
        except Exception as e:
            pattern_analysis = {'pattern_matches': [], 'total_patterns': 0}
        
        # Add universal patterns analysis
        try:
            from universal_pattern_discovery import universal_discovery
            current_state = {
                'rsi': current_rsi,
                'volume_ratio': (volume_24h_change_pct / 100) + 1,
                'price_change_pct': price_change_pct,
                'trend_direction': 1 if trend_bullish else 0,
                'volume_spike': 1 if volume_trend.get('spike_detected', False) else 0
            }
            universal_patterns = universal_discovery.apply_patterns_to_aster(current_state)
        except Exception as e:
            universal_patterns = []
        
        # Add MVRV analysis for on-chain tentacles
        try:
            from mvrv_integration import mvrv_tracker
            mvrv_data = mvrv_tracker.get_mvrv_analysis('BTC')  # Use BTC as proxy for crypto market
        except Exception as e:
            mvrv_data = {'mvrv_zscore': 0, 'signal': 'NEUTRAL'}
        
        # Enhanced sentiment indicators
        try:
            # Use fear/greed index from market data
            sentiment_score = sentiment.get('value', 50) if sentiment else 50
            sentiment_analysis = {
                'fear_greed_index': sentiment_score,
                'sentiment_signal': 'BULLISH' if sentiment_score > 60 else 'BEARISH' if sentiment_score < 40 else 'NEUTRAL',
                'market_mood': sentiment.get('label', 'Neutral') if sentiment else 'Neutral'
            }
        except Exception as e:
            sentiment_analysis = {'fear_greed_index': 50, 'sentiment_signal': 'NEUTRAL'}
        
        # Add perfect hindsight analysis for the final tentacle
        try:
            from perfect_hindsight_engine import perfect_hindsight
            current_conditions = {
                'price': current_price,
                'rsi': current_rsi,
                'volume_spike': volume_trend.get('spike_detected', False),
                'trend_bullish': trend_bullish,
                'funding_rate': perp.get('aster_funding', 0),
                'whale_activity': len(whale_analysis.get('whale_buys', [])) + len(whale_analysis.get('whale_sells', []))
            }
            perfect_hindsight_matches = perfect_hindsight.get_current_pattern_matches(current_conditions)
            perfect_hindsight_data = {
                'matches_found': len(perfect_hindsight_matches) if perfect_hindsight_matches else 0,
                'best_match': perfect_hindsight_matches[0] if perfect_hindsight_matches else None,
                'confidence_score': perfect_hindsight_matches[0].get('match_score', 0) if perfect_hindsight_matches else 0
            }
        except Exception as e:
            perfect_hindsight_data = {'matches_found': 0, 'confidence_score': 0}
        
        # Add volume spike intelligence
        try:
            from volume_spike_tracker import volume_tracker
            volume_intelligence = volume_tracker.get_volume_intelligence()
        except Exception as e:
            volume_intelligence = {'volume_confidence': 0, 'spike_count': 0, 'intelligence_summary': 'Volume tracker unavailable'}
        
        # Add time optimization intelligence
        try:
            from time_optimization import time_optimizer
            time_intelligence = time_optimizer.get_time_based_confidence()
        except Exception as e:
            time_intelligence = {'time_confidence': 0, 'opportunity_level': 'UNKNOWN', 'current_session': 'UNKNOWN'}

        analysis_data_for_confidence = {
            'technical': {
                'rsi': current_rsi,
                'trend_bullish': trend_bullish,
                'volume_spike': volume_trend.get('spike_detected', False),
                'price_above_ema9': price_above_ema9,
                'price_above_ema21': price_above_ema21
            },
            'volume_trend': volume_trend,
            'whale_analysis': whale_analysis,
            'master_brain': master_brain_context,
            'advanced_signals': advanced_signals,
            'pattern_summary': pattern_summary,
            'orderflow': orderflow_analysis,
            'market_regime': market_regime_actual,
            'time_context': get_time_of_day_context()['description'],
            'moon_candle': moon_candle,
            'dip_opportunity': dip_opportunity,
            'support_resistance': support_resistance,
            'recent_patterns': recent_patterns,
            'momentum': momentum,
            'perp_metrics': perp,
            'market_context': market_ctx,
            'sentiment': sentiment,
            'signal_results': signal_results,
            # NEW: Additional data sources for missing tentacles
            'pattern_analysis': pattern_analysis,
            'universal_patterns': universal_patterns,
            'mvrv_data': mvrv_data,
            'sentiment_analysis': sentiment_analysis,
            'perfect_hindsight': perfect_hindsight_data,
            'volume_intelligence': volume_intelligence,
            'time_intelligence': time_intelligence,
            'regime_indicators': regime_indicators,
            'regime_score': regime_score
        }
        
        # Get unified confidence score from ALL tentacles
        try:
            unified_confidence_result = unified_confidence.calculate_unified_confidence(
                market_data, analysis_data_for_confidence
            )
            
            # Add real-time astrological updates to unified confidence
            try:
                astrological_updates = unified_confidence.get_real_time_astrological_updates()
                unified_confidence_result['astrological_updates'] = astrological_updates
            except Exception as astro_error:
                print(f"Astrological updates error: {astro_error}")
                unified_confidence_result['astrological_updates'] = {'error': str(astro_error)}
                
        except Exception as e:
            print(f"Unified confidence calculation error: {e}")
            unified_confidence_result = {
                'unified_confidence_score': 50.0,
                'confidence_level': 'NEUTRAL',
                'signal_strength': 'WAIT',
                'reliability_score': 0.5,
                'tentacles_active': 0,
                'error': str(e)
            }
        
        # AI runs every 2 minutes and MAKES THE FINAL DECISION
        now = datetime.now()
        if (now - last_ai_run).total_seconds() >= 120 or not cached_ai:
            whale_sentiment = {'sentiment': 'NEUTRAL', 'score': 50}
            
            # Enhanced context with historical data + advanced indicators + Master Brain
            # master_brain_context already loaded above
            
            historical_context = {
                'volume_trend': volume_trend,
                'moon_candle': moon_candle,
                'dip_opportunity': dip_opportunity,
                'support_resistance': support_resistance,
                'recent_patterns': recent_patterns,
                'pattern_summary': pattern_summary,
                'whale_analysis': whale_analysis,
                'advanced_signals': advanced_signals,
                'master_brain': master_brain_context
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
        
        # Get recent whale trades for display with current price for P&L calculation
        whale_activity = whale_tracker.get_recent_whales(minutes=60, limit=5, current_price=current_price)
        if not whale_activity:
            whale_activity = [{
                'action': 'No whale trades detected',
                'amount': 'Last 60min',
                'type': 'neutral',
                'pnl': 'N/A',
                'tx_hash_short': 'N/A'
            }]
        
        # Get recent AI predictions for trade log - ONLY BUY/SELL decisions (not WAIT)
        trade_log = []
        try:
            import sqlite3
            conn = sqlite3.connect('data/ai_predictions.db')
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
        
        # Get comprehensive astrological analysis for dashboard
        try:
            detailed_astro_analysis = master_brain.get_astrological_analysis()
            
            # Add comprehensive planetary dashboard data using master astrology engine
            from tentacles.astrological.master_astro_engine import master_astro
            astro_intelligence = master_astro.get_comprehensive_analysis()
            
            # Format data for dashboard compatibility using Master Astrology Engine
            planetary_positions = astro_intelligence.get('planetary_positions', {})
            moon_analysis = astro_intelligence.get('moon_analysis', {})
            current_aspects_list = astro_intelligence.get('current_aspects', [])
            
            comprehensive_planetary = {
                'planets': planetary_positions,  # Send full planetary data as dict, not just keys
                'major_aspects': current_aspects_list,
                'fixed_stars_conjunctions': [],  # Placeholder for compatibility
                'data_source': 'master_astro_engine'
            }
            
            current_lunar = {
                'phase_icon': '🌙',
                'illumination_percent': moon_analysis.get('illumination_percent', 50),
                'moon_sign': moon_analysis.get('sign', 'Unknown'),
                'moon_degree': moon_analysis.get('degree', 0),
                'trading_impact': 'master_astro_real_time_calculation'
            }
            
            current_aspects = {
                'total_aspects': len(current_aspects_list),
                'aspect_summary': f"{len(current_aspects_list)} active aspects",
                'confidence_modifier': astro_intelligence.get('confidence_modifier', 0)
            }
            
            # Create user-friendly astrological highlights
            def get_user_friendly_moon_phase(percent):
                """Convert illumination percentage to simple explanation"""
                if percent < 5:
                    return "New Moon - A fresh start! Great time for new beginnings and setting intentions."
                elif percent < 25:
                    return "Waxing Crescent - Growing energy! Time to take action on your plans."
                elif percent < 45:
                    return "First Quarter - Decision time! Push through challenges and stay focused."
                elif percent < 55:
                    return "Waxing Gibbous - Almost there! Fine-tune your strategies and prepare for completion."
                elif percent < 95:
                    return "Full Moon - Peak energy! Maximum momentum, time for major moves."
                elif percent < 75:
                    return "Waning Gibbous - Harvest time! Enjoy the results and share your success."
                else:
                    return "Last Quarter - Release phase! Let go of what's not working, prepare for renewal."
            
            def get_simple_aspect_explanation(aspect):
                """Convert complex aspect to simple trading explanation"""
                aspect_type = aspect.get('aspect', '').lower()
                planet1 = aspect.get('planet1', 'Planet A')
                planet2 = aspect.get('planet2', 'Planet B')
                
                if 'conjunction' in aspect_type:
                    return f"{planet1} & {planet2} are joining forces - expect major moves!"
                elif 'trine' in aspect_type:
                    return f"{planet1} & {planet2} are in harmony - smooth sailing ahead!"
                elif 'square' in aspect_type:
                    return f"{planet1} & {planet2} are in tension - volatility and breakthrough moments!"
                elif 'opposition' in aspect_type:
                    return f"{planet1} & {planet2} are pulling opposite ways - potential reversal point!"
                elif 'sextile' in aspect_type:
                    return f"{planet1} & {planet2} create opportunity - good time for smart moves!"
                else:
                    return f"{planet1} & {planet2} are interacting - market influence active!"
            
            # Add user-friendly highlights
            astro_highlights = []
            
            # Moon phase highlight using Master Astrology Engine data
            moon_percent = moon_analysis.get('illumination_percent', 50)
            moon_sign = moon_analysis.get('sign', 'Unknown')
            astro_highlights.append(f"Moon in {moon_sign} - {get_user_friendly_moon_phase(moon_percent)}")
            
            # Top 3 aspects in simple language
            major_aspects = current_aspects_list[:3]
            for aspect in major_aspects:
                if aspect.get('strength', 0) > 0.5:  # Only strong aspects
                    astro_highlights.append(get_simple_aspect_explanation(aspect))
            
            # Add highlights to current_aspects for dashboard display
            current_aspects['user_friendly_highlights'] = astro_highlights
            
            # Add Master Astrology Engine data for new dashboard section
            detailed_astro_analysis.update({
                'market_sentiment': astro_intelligence.get('market_sentiment', 'Unknown'),
                'volatility_forecast': astro_intelligence.get('volatility_forecast', 'Unknown'), 
                'confidence_modifier': astro_intelligence.get('confidence_modifier', 0)
            })
        except Exception as e:
            print(f"Astrological analysis error: {e}")
            detailed_astro_analysis = {
                'available': False,
                'error': str(e),
                'lunar_phase': 'Unknown',
                'confidence': 0
            }
            comprehensive_planetary = {'error': str(e), 'planets': [], 'major_aspects': []}
            current_lunar = {'phase_icon': '❓', 'illumination_percent': 0}
            current_aspects = {'total_aspects': 0, 'aspect_summary': 'Error', 'confidence_modifier': 0}
        
        detailed_astro_analysis.update({
            'comprehensive_planetary_data': comprehensive_planetary,
            'current_lunar_detailed': {
                'phase_icon': current_lunar.get('phase_icon', '🌑'),
                'illumination_percent': current_lunar.get('illumination_percent', 0),
                'moon_sign': current_lunar.get('moon_sign', 'Unknown'),
                'moon_degree': current_lunar.get('moon_degree', 0),
                'days_to_new': current_lunar.get('days_to_new_moon', 0),
                'days_to_full': current_lunar.get('days_to_full_moon', 0),
                'lunar_strength': current_lunar.get('lunar_strength', 0),
                'trading_impact': current_lunar.get('trading_impact', 'Unknown')
            },
            'current_aspects_detailed': {
                'major_aspects': current_aspects_list,
                'aspect_summary': current_aspects.get('aspect_summary', 'No major aspects'),
                'confidence_modifier': current_aspects.get('confidence_modifier', 0),
                'total_aspects': current_aspects.get('total_aspects', 0)
            },
            'current_astrological_highlights': current_aspects.get('user_friendly_highlights', [
                f"Moon in {astro_intelligence.get('moon_sign', 'Unknown')} - Currently at {astro_intelligence.get('moon_phase_percent', 0):.1f}% illuminated"
            ])
        })
        
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
            'whale_activity': sanitize_datetimes(whale_activity),
            'trade_log': trade_log,
            'time_context': time_context['description'] + volume_info + moon_alert,
            'master_brain_summary': master_brain.get_dashboard_summary(),
            'has_active_position': active_position is not None,
            'volume_trend': sanitize_datetimes(volume_trend),
            'moon_candle': sanitize_datetimes(moon_candle),
            'entry_window_seconds': entry_window_seconds,
            'pattern_summary': pattern_summary,
            'whale_analysis': sanitize_datetimes(whale_analysis),
            'astrological_analysis': detailed_astro_analysis,
            'unified_confidence': unified_confidence_result,
            # Add missing data sources for tentacles  
            'advanced_signals': enhance_advanced_signals_for_tentacles(advanced_signals, current_price, klines_1m),
            'orderflow_analysis': sanitize_datetimes(orderflow_analysis),
            'sentiment': sanitize_datetimes(sentiment),
            'market_regime': market_regime_actual,
            'multi_timeframe_analysis': sanitize_datetimes(advanced_signals.get('multi_tf', {})),
            'cross_market': generate_cross_market_analysis(master_brain_context),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    except Exception as e:
        print(f"ERROR in get_scanner_data: {e}")
        import traceback
        traceback.print_exc()
        return None

def background_updates():
    """Background thread to push updates every 10 seconds for stability"""
    print("🔄 Background update thread started")
    while True:
        try:
            print(f"🕐 Background thread sleeping for 10 seconds... {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(10)  # Update every 10 seconds for stability
            print(f"🔄 Background thread waking up... {datetime.now().strftime('%H:%M:%S')}")
            
            with app.app_context():  # Fix: Run within Flask app context
                print("📡 Getting scanner data within app context...")
                data = get_scanner_data()
                if data:
                    print("✅ Data received, sanitizing...")
                    data = sanitize_datetimes(data)
                    print("📡 Emitting via WebSocket...")
                    socketio.emit('update', data, namespace='/')
                    print(f"📡 Update sent at {datetime.now().strftime('%H:%M:%S')}")
                else:
                    print("❌ No data received from get_scanner_data")
        except Exception as e:
            print(f"❌ Background update error: {e}")
            import traceback
            traceback.print_exc()
            # Continue running even if one update fails

@app.route('/')
def index():
    # Don't block initial page load - let WebSocket handle data
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint for initial data load"""
    try:
        data = get_scanner_data()
        if data:
            # Sanitize data before JSON serialization
            sanitized_data = sanitize_datetimes(data)
            return jsonify(sanitized_data)
        else:
            return jsonify({'error': 'Failed to fetch data'}), 500
    except Exception as e:
        print(f"API data error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chart-data')
def get_chart_data():
    """Get chart candle data directly from Aster DEX API"""
    try:
        from flask import request
        timeframe = request.args.get('timeframe', '15m')
        
        # Fetch directly from Aster API
        chart_data = fetcher.aster_api.get_klines(ASTER_SYMBOL, timeframe, 200)
        
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
def handle_connect(auth=None):
    try:
        data = get_scanner_data()
        if data:
            data = sanitize_datetimes(data)
            emit('update', data)
    except Exception as e:
        print(f"Error in handle_connect: {e}")
        pass

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
    """
    🔄 BULLETPROOF STARTUP RECOVERY
    Ensures seamless continuation after crashes/restarts
    """
    print("🔄 COMPREHENSIVE STARTUP RECOVERY...")
    print("="*60)
    
    recovery_status = {
        'price_data_backfill': False,
        'pattern_engine_check': False,
        'mvrv_data_check': False,
        'ai_learning_status': False,
        'active_position_restore': False
    }
    
    try:
        # 1. Price History Recovery
        print("1️⃣ Checking price history gaps...")
        conn = sqlite3.connect('data/price_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM price_ticks")
        last_tick = cursor.fetchone()[0]
        conn.close()
        
        if last_tick:
            last_time = datetime.fromisoformat(last_tick)
            downtime_minutes = (datetime.now() - last_time).total_seconds() / 60
            
            if downtime_minutes > 2:
                print(f"   📥 Scanner was offline for {downtime_minutes:.1f} minutes")
                print("   📊 Backfilling price data...")
                
                chart_data = fetcher.aster_api.get_klines(ASTER_SYMBOL, '1m', int(min(downtime_minutes, 1000)))
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
                    print(f"   ✅ Backfilled {backfilled} price ticks")
                
                price_history.calculate_volume_metrics()
                print("   ✅ Volume metrics recalculated")
                recovery_status['price_data_backfill'] = True
            else:
                print("   ✅ No significant downtime detected")
                recovery_status['price_data_backfill'] = True
        
        # 2. Pattern Engine Status Check
        print("\n2️⃣ Checking pattern engine status...")
        try:
            from pattern_miner import PatternMiner
            miner = PatternMiner()
            active_patterns = miner.get_active_patterns_summary()
            print(f"   📊 Active patterns: {len(active_patterns)}")
            print(f"   🎯 Win rate threshold: {miner.adaptive_params['min_win_rate']:.1%}")
            recovery_status['pattern_engine_check'] = True
        except Exception as e:
            print(f"   ⚠️ Pattern engine issue: {e}")
        
        # 3. MVRV Data Check
        print("\n3️⃣ Checking MVRV intelligence...")
        try:
            from mvrv_tracker import MVRVTracker
            mvrv = MVRVTracker()
            analysis = mvrv.get_current_analysis()
            if analysis:
                print(f"   📊 MVRV Z-Score: {analysis['zscore']:.2f}")
                print(f"   📈 Market Phase: {analysis['market_phase']}")
                recovery_status['mvrv_data_check'] = True
            else:
                print("   ⚠️ MVRV data unavailable")
        except Exception as e:
            print(f"   ⚠️ MVRV check issue: {e}")
        
        # 4. AI Learning Status
        print("\n4️⃣ Checking AI learning status...")
        conn = sqlite3.connect('data/ai_predictions.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM predictions 
            WHERE recommendation IN ('BUY_NOW', 'STRONG_BUY', 'SELL')
        """)
        trade_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE outcome = 'WIN'")
        win_count = cursor.fetchone()[0]
        
        win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0
        
        cursor.execute("SELECT MAX(timestamp) FROM predictions")
        last_prediction = cursor.fetchone()[0]
        conn.close()
        
        print(f"   📈 Total trades: {trade_count}")
        print(f"   🎯 Win rate: {win_rate:.1f}%")
        print(f"   ⏰ Last prediction: {last_prediction[:19] if last_prediction else 'None'}")
        recovery_status['ai_learning_status'] = True
        
        # 5. Active Position Recovery
        print("\n5️⃣ Checking for active positions...")
        global active_position
        if active_position:
            print(f"   💰 Active position detected:")
            print(f"      Entry: ${active_position['entry_price']:.6f}")
            print(f"      Target: ${active_position['target_price']:.6f}")
            print(f"      Stop: ${active_position['stop_price']:.6f}")
            print(f"      Leverage: {active_position['leverage']}x")
            recovery_status['active_position_restore'] = True
        else:
            print("   ✅ No active positions")
            recovery_status['active_position_restore'] = True
        
        # Recovery Summary
        print("\n" + "="*60)
        print("🏁 RECOVERY SUMMARY:")
        successful_recoveries = sum(recovery_status.values())
        total_checks = len(recovery_status)
        
        for check, status in recovery_status.items():
            status_icon = "✅" if status else "❌"
            check_name = check.replace('_', ' ').title()
            print(f"   {status_icon} {check_name}")
        
        print(f"\n🎯 Recovery Status: {successful_recoveries}/{total_checks} components restored")
        
        if successful_recoveries == total_checks:
            print("🚀 FULL RECOVERY COMPLETE - System ready for trading!")
        else:
            print("⚠️ PARTIAL RECOVERY - Some components need attention")
        
        print("="*60)
        
    except Exception as e:
        print(f"⚠️ Startup recovery encountered issue: {e}")
        print("✅ Continuing with fresh data collection...")
        import traceback
        traceback.print_exc()

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