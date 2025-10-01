"""
Whale Trade Tracker - Detect and log large trades
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
import threading

class WhaleTracker:
    def __init__(self, db_path: str = "data/whale_trades.db", whale_threshold_usd: float = 5000):
        self.db_path = db_path
        self.whale_threshold = whale_threshold_usd
        self.lock = threading.Lock()
        self.last_trade_id = None
        self._init_database()
    
    def _init_database(self):
        """Initialize whale trades database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whale_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                timestamp DATETIME NOT NULL,
                price FLOAT NOT NULL,
                quantity FLOAT NOT NULL,
                usd_value FLOAT NOT NULL,
                direction TEXT NOT NULL,
                is_buyer_maker BOOLEAN,
                transaction_hash TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_whale_timestamp 
            ON whale_trades(timestamp DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def analyze_trades(self, trades: List[Dict], current_price: float) -> Dict:
        """
        Analyze recent trades for whale activity
        trades: List of trades from Aster API
        """
        if not trades:
            return {'whale_detected': False}
        
        whale_buys = []
        whale_sells = []
        total_buy_volume = 0
        total_sell_volume = 0
        
        for trade in trades:
            qty = trade.get('qty', 0)
            price = trade.get('price', current_price)
            usd_value = qty * price
            is_buyer_maker = trade.get('is_buyer_maker', False)
            
            direction = 'SELL' if is_buyer_maker else 'BUY'
            
            if direction == 'BUY':
                total_buy_volume += usd_value
            else:
                total_sell_volume += usd_value
            
            if usd_value >= self.whale_threshold:
                # Generate transaction hash from trade ID
                trade_id = trade.get('id') or trade.get('agg_id') or f"whale_{int(trade.get('time', 0))}"
                transaction_hash = f"0x{str(trade_id).zfill(8)}{str(int(trade.get('time', 0)))[-8:]}"
                
                whale_trade = {
                    'trade_id': str(trade_id),
                    'time': datetime.fromtimestamp(trade.get('time', 0) / 1000),
                    'price': price,
                    'quantity': qty,
                    'usd_value': usd_value,
                    'direction': direction,
                    'transaction_hash': transaction_hash
                }
                
                if direction == 'BUY':
                    whale_buys.append(whale_trade)
                else:
                    whale_sells.append(whale_trade)
                
                self._log_whale_trade(
                    trade_id=whale_trade['trade_id'],
                    timestamp=whale_trade['time'],
                    price=price,
                    quantity=qty,
                    usd_value=usd_value,
                    direction=direction,
                    is_buyer_maker=is_buyer_maker,
                    transaction_hash=whale_trade['transaction_hash']
                )
        
        net_buy_pressure = total_buy_volume - total_sell_volume
        buy_pressure_pct = (net_buy_pressure / (total_buy_volume + total_sell_volume) * 100) if (total_buy_volume + total_sell_volume) > 0 else 0
        
        return {
            'whale_detected': len(whale_buys) > 0 or len(whale_sells) > 0,
            'whale_buys': whale_buys,
            'whale_sells': whale_sells,
            'total_buy_volume': total_buy_volume,
            'total_sell_volume': total_sell_volume,
            'net_buy_pressure': net_buy_pressure,
            'buy_pressure_pct': buy_pressure_pct,
            'whale_signal': 'BULLISH' if buy_pressure_pct > 20 else 'BEARISH' if buy_pressure_pct < -20 else 'NEUTRAL'
        }
    
    def _log_whale_trade(self, trade_id: str, timestamp: datetime, price: float,
                        quantity: float, usd_value: float, direction: str, is_buyer_maker: bool,
                        transaction_hash: str):
        """Log whale trade to database"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR IGNORE INTO whale_trades 
                    (trade_id, timestamp, price, quantity, usd_value, direction, is_buyer_maker, transaction_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (trade_id, timestamp, price, quantity, usd_value, direction, is_buyer_maker, transaction_hash))
                
                conn.commit()
                conn.close()
        except Exception as e:
            pass
    
    def get_recent_whales(self, minutes: int = 60, limit: int = 10, current_price: float = None) -> List[Dict]:
        """Get recent whale trades for display"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(minutes=minutes)
            
            cursor.execute("""
                SELECT timestamp, price, quantity, usd_value, direction, transaction_hash, trade_id
                FROM whale_trades
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff, limit))
            
            whales = []
            for row in cursor.fetchall():
                trade_price = row[1]
                usd_value = row[3]
                direction = row[4]
                transaction_hash = row[5] or "N/A"
                
                # Calculate P&L if current price is provided
                pnl_text = "N/A"
                if current_price and current_price > 0:
                    if direction == 'BUY':
                        pnl_pct = ((current_price - trade_price) / trade_price) * 100
                        pnl_text = f"{pnl_pct:+.1f}%"
                    else:  # SELL
                        pnl_pct = ((trade_price - current_price) / trade_price) * 100
                        pnl_text = f"{pnl_pct:+.1f}%"
                
                # Format transaction hash (show first 6 and last 4 characters)
                tx_hash_short = transaction_hash[:6] + "..." + transaction_hash[-4:] if len(transaction_hash) > 10 else transaction_hash
                
                whales.append({
                    'time': row[0],
                    'price': f"${trade_price:.6f}",
                    'quantity': f"{row[2]:,.0f}",
                    'amount': f"${usd_value:,.0f}",  # This is what the dashboard expects
                    'usd_value': f"${usd_value:,.0f}",
                    'action': direction,
                    'type': 'bullish' if direction == 'BUY' else 'bearish',
                    'pnl': pnl_text,
                    'transaction_hash': transaction_hash,
                    'tx_hash_short': tx_hash_short
                })
            
            conn.close()
            return whales
        except Exception:
            return []
    
    def get_whale_summary(self, minutes: int = 60) -> Dict:
        """Get summary of whale activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(minutes=minutes)
            
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN direction = 'BUY' THEN 1 END) as buy_count,
                    COUNT(CASE WHEN direction = 'SELL' THEN 1 END) as sell_count,
                    SUM(CASE WHEN direction = 'BUY' THEN usd_value ELSE 0 END) as buy_volume,
                    SUM(CASE WHEN direction = 'SELL' THEN usd_value ELSE 0 END) as sell_volume
                FROM whale_trades
                WHERE timestamp >= ?
            """, (cutoff,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                buy_count = row[0] or 0
                sell_count = row[1] or 0
                buy_volume = row[2] or 0
                sell_volume = row[3] or 0
                
                net_volume = buy_volume - sell_volume
                
                return {
                    'buy_count': buy_count,
                    'sell_count': sell_count,
                    'buy_volume': buy_volume,
                    'sell_volume': sell_volume,
                    'net_volume': net_volume,
                    'sentiment': 'BULLISH' if net_volume > 10000 else 'BEARISH' if net_volume < -10000 else 'NEUTRAL'
                }
            
            return {'buy_count': 0, 'sell_count': 0, 'sentiment': 'NEUTRAL'}
        except Exception:
            return {'buy_count': 0, 'sell_count': 0, 'sentiment': 'NEUTRAL'}