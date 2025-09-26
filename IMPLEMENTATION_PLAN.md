# ASTER Scanner - Complete Implementation Plan

## Phase 1: Fix Volume Bug (15 min)
**Status:** CRITICAL - Data exists but not displaying
**Goal:** Make $2.7B volume show on dashboard

1. Add debug logging to track data flow
2. Check if issue is in background thread timing
3. Force fresh data fetch instead of cached
4. Test and verify volume displays correctly

---

## Phase 2: Historical Data System (1 hour)
**Status:** CRITICAL - Foundation for everything else
**Goal:** Store all price/volume history for pattern learning

### 2.1 Create Historical Database
```python
# price_history.db structure:
- price_ticks (timestamp, price, volume_1m)
- volume_metrics (timestamp, vol_5m, vol_15m, vol_1h, vol_4h, vol_24h)
- pattern_events (timestamp, type, description, outcome)
```

### 2.2 Background Data Collection
- Every 1 second: Store price + 1m volume
- Every 5 minutes: Calculate volume metrics
- Store in SQLite for fast queries

### 2.3 Historical Data Analysis Functions
```python
def get_volume_trend(timeframe='5m'):
    # Returns: increasing/decreasing/stable
    
def detect_volume_spike():
    # Returns: True if current > 2x average
    
def get_support_resistance_levels():
    # From last 24h price history
```

---

## Phase 3: Volume Trend Analysis (30 min)
**Status:** HIGH PRIORITY
**Goal:** AI knows if volume is spiking or dropping

### 3.1 Volume Comparison Module
```python
- Current 5m volume vs 1h average
- Volume spike detection (>2x average)
- Volume trend: increasing/decreasing/stable
- Pass to AI in prompt
```

### 3.2 Add to AI Prompt
```
Volume Analysis:
- 24h Volume: $2.7B (↑ increasing)
- 5m Volume: 50M ASTER (2.3x above 1h avg) ⚠️ SPIKE
- Trend: Heavy buying pressure detected
```

---

## Phase 4: Moon Candle Detection (45 min)
**Status:** HIGH VALUE
**Goal:** Catch big pumps (5%+ moves in <5 minutes)

### 4.1 Pump Detection System
```python
def detect_moon_candle():
    # Check last 5 candles for:
    # - Price increase >5% in <5 min
    # - Volume spike >3x average
    # - Strong momentum continuation
    # Returns: MOON_PUMP, NORMAL, DUMP
```

### 4.2 Add New Strategy: "Moonshot"
```python
Strategy: MOONSHOT
- Detects big pumps early (first 2-3%)
- Quick entry, 8-15% target
- Tight stop loss (2%)
- High leverage (30-40x)
- Human-speed: 30-60 second window to enter
```

### 4.3 Visual Alert System
- Dashboard shows "🌙 MOON CANDLE DETECTED"
- Big green flash on screen
- Entry/exit prices prominently displayed

---

## Phase 5: Pattern Recognition (1 hour)
**Status:** MEDIUM PRIORITY
**Goal:** Learn from past price movements

### 5.1 Pattern Database
```python
patterns = {
    'support_bounces': [], # Price bounces off support
    'resistance_breaks': [], # Breakouts
    'pump_patterns': [], # What happened before pumps
    'dump_warnings': [] # What signals dumps
}
```

### 5.2 Pattern Learning
- Every trade: Log what patterns were present
- Track which patterns led to wins
- AI uses successful patterns for decisions

### 5.3 Time-of-Day Patterns
```python
# Learn when pumps typically happen:
- Tokyo hours (0-8 UTC)
- London/NY overlap (12-16 UTC)
- Weekend patterns
- Track success rate per time period
```

---

## Phase 6: Enhanced AI Prompt (30 min)
**Status:** HIGH PRIORITY
**Goal:** Give AI all the context it needs

### 6.1 Add to AI Analysis Prompt
```
HISTORICAL CONTEXT:
- Support level: $1.85 (tested 3x today)
- Resistance: $2.10 (broke through 2h ago)
- Previous pump: +12% in 15min at 14:30 UTC
- Similar pattern detected: YES (matches pump from 6h ago)

VOLUME ANALYSIS:
- 24h: $2.7B (↑ +15% vs yesterday)
- Current 5m: 50M (⚠️ 2.3x spike)
- Trend: Heavy accumulation phase

PATTERN RECOGNITION:
- Moon candle potential: 60% (volume + momentum)
- Dip bounce setup: Support holding strong
- Breakout imminent: Price coiling at resistance

TIME CONTEXT:
- London/NY overlap (high volume period)
- Historical pump time window
```

---

## Phase 7: Human-Speed Optimization (20 min)
**Status:** IMPORTANT
**Goal:** Signals that humans can actually trade

### 7.1 Entry/Exit Timing
- Minimum 30 seconds to enter after signal
- Hold time: 2-30 minutes (human-tradeable)
- Clear "BUY NOW" alerts when detected
- Exit targets visible throughout trade

### 7.2 Dashboard Enhancements
- Big "BUY NOW" button flashes green
- Countdown timer: "Entry window: 45 seconds remaining"
- Clear profit visualization
- One-click copy trade info

---

## Phase 8: Testing & Validation (30 min)

### 8.1 Backtesting
- Test on last 7 days of ASTER data
- Measure win rate, avg profit
- Tune thresholds

### 8.2 Paper Trading
- Run for 24 hours
- Log all signals
- Calculate theoretical profit

---

## Total Implementation Time: ~5 hours

## Priority Order:
1. ✅ Fix volume bug (15 min) - CRITICAL
2. ✅ Historical data system (1h) - FOUNDATION  
3. ✅ Volume trend analysis (30 min) - HIGH VALUE
4. ✅ Moon candle detection (45 min) - USER REQUEST
5. ✅ Enhanced AI prompt (30 min) - QUICK WIN
6. ⏸ Pattern recognition (1h) - NICE TO HAVE
7. ⏸ Human-speed optimization (20 min) - POLISH

## Success Metrics:
- ✅ Volume displays correctly
- ✅ AI sees volume trends
- ✅ Moon candles detected within 30 seconds
- ✅ 70%+ accuracy on trades
- ✅ Humans can execute trades in time
