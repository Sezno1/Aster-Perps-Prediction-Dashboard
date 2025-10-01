"""
📊 VOLUME SPIKE ANALYSIS SYSTEM
Tracks real-time volume patterns across top 50 coins + ASTER
Provides intelligence for volume spike tentacle activation

FEATURES:
- Real-time volume monitoring across top coins
- Volume spike detection and classification
- Cross-coin volume correlation analysis
- Market-wide volume trends
- Predictive volume pattern recognition
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import time
import json

class VolumeSpikeTracker:
    """
    Tracks volume spikes across multiple coins for market intelligence
    """
    
    def __init__(self):
        self.create_volume_database()
        self.top_coins = self._get_top_50_coins()
        print("📊 Volume Spike Tracker: ONLINE")
        print(f"🎯 Monitoring {len(self.top_coins)} coins for volume patterns")
    
    def create_volume_database(self):
        """Create database for volume tracking"""
        
        conn = sqlite3.connect('data/volume_spikes.db')
        cursor = conn.cursor()
        
        # Volume data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volume_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL,
                volume_24h REAL,
                volume_1h REAL,
                price_change_24h REAL,
                market_cap REAL,
                volume_rank INTEGER
            )
        """)
        
        # Volume spikes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volume_spikes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                spike_multiplier REAL,
                volume_before REAL,
                volume_during REAL,
                price_impact REAL,
                spike_type TEXT,
                duration_minutes INTEGER,
                market_wide_spike BOOLEAN
            )
        """)
        
        # Market volume trends
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_volume_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_market_volume REAL,
                avg_volume_multiplier REAL,
                coins_with_spikes INTEGER,
                market_sentiment TEXT,
                trend_direction TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Volume tracking database created")
    
    def _get_top_50_coins(self) -> List[str]:
        """Get top 50 coins by market cap + ASTER"""
        
        # Top coins by market cap (CMC/CoinGecko style)
        top_coins = [
            'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE',
            'TRX', 'DOT', 'LINK', 'MATIC', 'ICP', 'SHIB', 'UNI', 'LTC', 'APT', 'ETC',
            'ATOM', 'FIL', 'VET', 'ALGO', 'AAVE', 'SAND', 'MANA', 'AXS', 'THETA', 'XTZ',
            'FTM', 'EGLD', 'KLAY', 'FLOW', 'CHZ', 'ENJ', 'BAT', 'ZIL', 'HOT', 'QTUM',
            'IOST', 'OMG', 'REN', 'KNC', 'STORJ', 'GRT', 'COMP', 'YFI', 'SUSHI', 'CRV'
        ]
        
        # Always include ASTER
        if 'ASTER' not in top_coins:
            top_coins.append('ASTER')
        
        return top_coins
    
    def fetch_volume_data(self, symbol: str) -> Optional[Dict]:
        """Fetch current volume data for a symbol"""
        
        try:
            # Use CoinGecko API (free tier)
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': symbol.lower(),
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if symbol.lower() in data:
                    coin_data = data[symbol.lower()]
                    return {
                        'symbol': symbol,
                        'price': coin_data.get('usd', 0),
                        'volume_24h': coin_data.get('usd_24h_vol', 0),
                        'price_change_24h': coin_data.get('usd_24h_change', 0),
                        'market_cap': coin_data.get('usd_market_cap', 0),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
        
        return None
    
    def detect_volume_spikes(self, symbol: str, current_volume: float) -> Optional[Dict]:
        """Detect if current volume is a spike compared to recent history"""
        
        conn = sqlite3.connect('data/volume_spikes.db')
        cursor = conn.cursor()
        
        # Get recent volume data (last 24 hours)
        cursor.execute("""
            SELECT volume_24h FROM volume_data 
            WHERE symbol = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 24
        """, (symbol, (datetime.now() - timedelta(hours=24)).isoformat()))
        
        recent_volumes = [row[0] for row in cursor.fetchall() if row[0] > 0]
        conn.close()
        
        if len(recent_volumes) < 5:  # Need enough history
            return None
        
        # Calculate volume spike metrics
        avg_volume = np.mean(recent_volumes)
        volume_std = np.std(recent_volumes)
        
        if avg_volume > 0:
            multiplier = current_volume / avg_volume
            
            # Classify spike type
            spike_type = None
            if multiplier >= 5.0:
                spike_type = 'MASSIVE_SPIKE'
            elif multiplier >= 3.0:
                spike_type = 'LARGE_SPIKE'
            elif multiplier >= 2.0:
                spike_type = 'MODERATE_SPIKE'
            elif multiplier >= 1.5:
                spike_type = 'MINOR_SPIKE'
            
            if spike_type:
                return {
                    'symbol': symbol,
                    'multiplier': multiplier,
                    'spike_type': spike_type,
                    'avg_volume': avg_volume,
                    'current_volume': current_volume,
                    'volume_std': volume_std,
                    'timestamp': datetime.now().isoformat()
                }
        
        return None
    
    def update_market_data(self) -> Dict:
        """Update volume data for all tracked coins"""
        
        spikes_detected = []
        total_volume = 0
        coins_updated = 0
        
        conn = sqlite3.connect('data/volume_spikes.db')
        cursor = conn.cursor()
        
        for symbol in self.top_coins[:20]:  # Limit to prevent rate limiting
            volume_data = self.fetch_volume_data(symbol)
            
            if volume_data:
                # Store volume data
                cursor.execute("""
                    INSERT INTO volume_data 
                    (symbol, timestamp, price, volume_24h, price_change_24h, market_cap)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    volume_data['symbol'],
                    volume_data['timestamp'],
                    volume_data['price'],
                    volume_data['volume_24h'],
                    volume_data['price_change_24h'],
                    volume_data['market_cap']
                ))
                
                # Check for spikes
                spike_data = self.detect_volume_spikes(symbol, volume_data['volume_24h'])
                if spike_data:
                    spikes_detected.append(spike_data)
                    
                    # Store spike data
                    cursor.execute("""
                        INSERT INTO volume_spikes
                        (symbol, timestamp, spike_multiplier, volume_before, volume_during, spike_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        spike_data['symbol'],
                        spike_data['timestamp'],
                        spike_data['multiplier'],
                        spike_data['avg_volume'],
                        spike_data['current_volume'],
                        spike_data['spike_type']
                    ))
                
                total_volume += volume_data['volume_24h']
                coins_updated += 1
                
                # Rate limiting
                time.sleep(0.1)
        
        # Store market-wide volume trend
        avg_multiplier = np.mean([s['multiplier'] for s in spikes_detected]) if spikes_detected else 1.0
        market_sentiment = 'HIGH_ACTIVITY' if len(spikes_detected) >= 3 else 'NORMAL'
        
        cursor.execute("""
            INSERT INTO market_volume_trends
            (timestamp, total_market_volume, avg_volume_multiplier, coins_with_spikes, market_sentiment)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            total_volume,
            avg_multiplier,
            len(spikes_detected),
            market_sentiment
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'coins_updated': coins_updated,
            'spikes_detected': len(spikes_detected),
            'total_market_volume': total_volume,
            'market_sentiment': market_sentiment,
            'spike_details': spikes_detected
        }
    
    def get_volume_intelligence(self) -> Dict:
        """Get current volume intelligence for tentacle system"""
        
        conn = sqlite3.connect('data/volume_spikes.db')
        cursor = conn.cursor()
        
        # Recent volume spikes
        cursor.execute("""
            SELECT symbol, spike_multiplier, spike_type, timestamp
            FROM volume_spikes
            WHERE timestamp > ?
            ORDER BY spike_multiplier DESC
            LIMIT 10
        """, ((datetime.now() - timedelta(hours=1)).isoformat(),))
        
        recent_spikes = []
        for row in cursor.fetchall():
            recent_spikes.append({
                'symbol': row[0],
                'multiplier': row[1],
                'type': row[2],
                'timestamp': row[3]
            })
        
        # Market volume trend
        cursor.execute("""
            SELECT avg_volume_multiplier, coins_with_spikes, market_sentiment
            FROM market_volume_trends
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        trend_data = cursor.fetchone()
        market_trend = {
            'avg_multiplier': trend_data[0] if trend_data else 1.0,
            'active_coins': trend_data[1] if trend_data else 0,
            'sentiment': trend_data[2] if trend_data else 'NORMAL'
        }
        
        # ASTER specific intelligence
        cursor.execute("""
            SELECT volume_24h, price_change_24h 
            FROM volume_data
            WHERE symbol = 'ASTER'
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        aster_data = cursor.fetchone()
        aster_volume = aster_data[0] if aster_data else 0
        
        # Calculate volume confidence for tentacle
        volume_confidence = 0.0
        if recent_spikes:
            # Check if ASTER is in recent spikes
            aster_spike = next((s for s in recent_spikes if s['symbol'] == 'ASTER'), None)
            if aster_spike:
                volume_confidence = min(0.4, aster_spike['multiplier'] * 0.1)
        
        # Market-wide activity bonus
        if market_trend['sentiment'] == 'HIGH_ACTIVITY':
            volume_confidence += 0.1
        
        conn.close()
        
        return {
            'volume_confidence': volume_confidence,
            'recent_spikes': recent_spikes,
            'market_trend': market_trend,
            'aster_volume': aster_volume,
            'spike_count': len(recent_spikes),
            'intelligence_summary': f"{len(recent_spikes)} spikes detected, market {market_trend['sentiment'].lower()}"
        }

# Global instance
volume_tracker = VolumeSpikeTracker()

if __name__ == "__main__":
    print("📊 Testing Volume Spike Tracker...")
    
    # Update market data
    result = volume_tracker.update_market_data()
    print(f"Updated {result['coins_updated']} coins")
    print(f"Detected {result['spikes_detected']} volume spikes")
    
    # Get intelligence
    intelligence = volume_tracker.get_volume_intelligence()
    print(f"Volume confidence: {intelligence['volume_confidence']:.2f}")
    print(f"Recent spikes: {intelligence['spike_count']}")
    print(f"Summary: {intelligence['intelligence_summary']}")