"""
Order Flow & Order Book Analysis Module
Real-time bid/ask pressure, large order detection, and short-term prediction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from aster_api import AsterAPI

class OrderFlowAnalyzer:
    def __init__(self, aster_api: AsterAPI):
        self.aster_api = aster_api
        self.orderbook_history = []
        self.max_history = 50
    
    def analyze_orderbook(self, symbol: str, depth: int = 100) -> Dict:
        """Comprehensive orderbook analysis"""
        orderbook = self.aster_api.get_orderbook(symbol, limit=depth)
        
        if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
            return self._empty_analysis()
        
        bids = orderbook['bids']
        asks = orderbook['asks']
        
        bid_ask_analysis = self._calculate_bid_ask_metrics(bids, asks)
        
        large_orders = self._detect_large_orders(bids, asks)
        
        imbalance_score = self._calculate_imbalance_score(bids, asks)
        
        support_resistance = self._find_key_levels(bids, asks)
        
        prediction = self._predict_short_term_direction(
            imbalance_score, 
            bid_ask_analysis,
            large_orders
        )
        
        self._store_orderbook_snapshot({
            'timestamp': datetime.now(),
            'bid_volume': bid_ask_analysis['total_bid_volume'],
            'ask_volume': bid_ask_analysis['total_ask_volume'],
            'imbalance': imbalance_score,
            'spread': bid_ask_analysis['spread']
        })
        
        return {
            'timestamp': datetime.now(),
            'bid_ask_metrics': bid_ask_analysis,
            'large_orders': large_orders,
            'imbalance_score': imbalance_score,
            'support_resistance': support_resistance,
            'prediction': prediction,
            'orderbook_strength': self._calculate_orderbook_strength(bids, asks)
        }
    
    def _calculate_bid_ask_metrics(self, bids: List, asks: List) -> Dict:
        """Calculate bid/ask pressure metrics"""
        if not bids or not asks:
            return {}
        
        best_bid = bids[0][0] if len(bids) > 0 else 0
        best_ask = asks[0][0] if len(asks) > 0 else 0
        spread = best_ask - best_bid
        spread_percent = (spread / best_bid * 100) if best_bid > 0 else 0
        
        total_bid_volume = sum([qty for price, qty in bids])
        total_ask_volume = sum([qty for price, qty in asks])
        
        bid_liquidity_5 = sum([qty for price, qty in bids[:5]])
        ask_liquidity_5 = sum([qty for price, qty in asks[:5]])
        
        bid_liquidity_20 = sum([qty for price, qty in bids[:20]])
        ask_liquidity_20 = sum([qty for price, qty in asks[:20]])
        
        bid_ask_ratio = total_bid_volume / total_ask_volume if total_ask_volume > 0 else 0
        
        weighted_bid_price = sum([p * q for p, q in bids]) / total_bid_volume if total_bid_volume > 0 else 0
        weighted_ask_price = sum([p * q for p, q in asks]) / total_ask_volume if total_ask_volume > 0 else 0
        
        return {
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': spread,
            'spread_percent': spread_percent,
            'total_bid_volume': total_bid_volume,
            'total_ask_volume': total_ask_volume,
            'bid_ask_ratio': bid_ask_ratio,
            'bid_liquidity_top5': bid_liquidity_5,
            'ask_liquidity_top5': ask_liquidity_5,
            'bid_liquidity_top20': bid_liquidity_20,
            'ask_liquidity_top20': ask_liquidity_20,
            'weighted_bid_price': weighted_bid_price,
            'weighted_ask_price': weighted_ask_price,
            'mid_price': (best_bid + best_ask) / 2
        }
    
    def _detect_large_orders(self, bids: List, asks: List, 
                            percentile: float = 90) -> Dict:
        """Detect large orders (walls) in orderbook"""
        if not bids or not asks:
            return {'bid_walls': [], 'ask_walls': []}
        
        all_bid_volumes = [qty for _, qty in bids]
        all_ask_volumes = [qty for _, qty in asks]
        
        bid_threshold = np.percentile(all_bid_volumes, percentile) if len(all_bid_volumes) > 0 else 0
        ask_threshold = np.percentile(all_ask_volumes, percentile) if len(all_ask_volumes) > 0 else 0
        
        bid_walls = [
            {'price': price, 'volume': qty, 'type': 'bid'}
            for price, qty in bids
            if qty >= bid_threshold and bid_threshold > 0
        ]
        
        ask_walls = [
            {'price': price, 'volume': qty, 'type': 'ask'}
            for price, qty in asks
            if qty >= ask_threshold and ask_threshold > 0
        ]
        
        return {
            'bid_walls': bid_walls[:5],
            'ask_walls': ask_walls[:5],
            'bid_wall_count': len(bid_walls),
            'ask_wall_count': len(ask_walls),
            'strongest_bid_wall': max(bid_walls, key=lambda x: x['volume']) if bid_walls else None,
            'strongest_ask_wall': max(ask_walls, key=lambda x: x['volume']) if ask_walls else None
        }
    
    def _calculate_imbalance_score(self, bids: List, asks: List) -> float:
        """Calculate orderbook imbalance score (-100 to +100)"""
        if not bids or not asks:
            return 0
        
        total_bid_volume = sum([qty for _, qty in bids])
        total_ask_volume = sum([qty for _, qty in asks])
        
        top_bid_volume = sum([qty for _, qty in bids[:10]])
        top_ask_volume = sum([qty for _, qty in asks[:10]])
        
        total_imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
        
        top_imbalance = (top_bid_volume - top_ask_volume) / (top_bid_volume + top_ask_volume) if (top_bid_volume + top_ask_volume) > 0 else 0
        
        weighted_imbalance = (total_imbalance * 0.6) + (top_imbalance * 0.4)
        
        imbalance_score = weighted_imbalance * 100
        
        return imbalance_score
    
    def _find_key_levels(self, bids: List, asks: List, 
                        cluster_threshold: float = 0.001) -> Dict:
        """Find key support/resistance levels from orderbook"""
        if not bids or not asks:
            return {'support_levels': [], 'resistance_levels': []}
        
        bid_clusters = self._find_volume_clusters(bids, cluster_threshold)
        ask_clusters = self._find_volume_clusters(asks, cluster_threshold)
        
        support_levels = sorted(bid_clusters, key=lambda x: x['volume'], reverse=True)[:3]
        resistance_levels = sorted(ask_clusters, key=lambda x: x['volume'], reverse=True)[:3]
        
        return {
            'support_levels': support_levels,
            'resistance_levels': resistance_levels
        }
    
    def _find_volume_clusters(self, orders: List, threshold: float) -> List[Dict]:
        """Find price levels with clustered volume"""
        if not orders:
            return []
        
        clusters = []
        current_cluster = {'price': orders[0][0], 'volume': orders[0][1], 'count': 1}
        
        for i in range(1, len(orders)):
            price, volume = orders[i]
            
            if abs(price - current_cluster['price']) / current_cluster['price'] <= threshold:
                current_cluster['volume'] += volume
                current_cluster['count'] += 1
                current_cluster['price'] = (current_cluster['price'] + price) / 2
            else:
                if current_cluster['count'] >= 2:
                    clusters.append(current_cluster.copy())
                current_cluster = {'price': price, 'volume': volume, 'count': 1}
        
        if current_cluster['count'] >= 2:
            clusters.append(current_cluster)
        
        return clusters
    
    def _predict_short_term_direction(self, imbalance_score: float, 
                                     bid_ask_metrics: Dict,
                                     large_orders: Dict) -> Dict:
        """Predict short-term price direction (1-15 min)"""
        score = 0
        reasons = []
        
        if imbalance_score > 20:
            score += 30
            reasons.append(f"Strong buy pressure (imbalance: {imbalance_score:.1f})")
        elif imbalance_score < -20:
            score -= 30
            reasons.append(f"Strong sell pressure (imbalance: {imbalance_score:.1f})")
        elif imbalance_score > 10:
            score += 15
            reasons.append(f"Moderate buy pressure (imbalance: {imbalance_score:.1f})")
        elif imbalance_score < -10:
            score -= 15
            reasons.append(f"Moderate sell pressure (imbalance: {imbalance_score:.1f})")
        
        if bid_ask_metrics.get('bid_ask_ratio', 1) > 1.3:
            score += 20
            reasons.append(f"Bid dominance (ratio: {bid_ask_metrics['bid_ask_ratio']:.2f})")
        elif bid_ask_metrics.get('bid_ask_ratio', 1) < 0.7:
            score -= 20
            reasons.append(f"Ask dominance (ratio: {bid_ask_metrics['bid_ask_ratio']:.2f})")
        
        bid_walls = large_orders.get('bid_wall_count', 0)
        ask_walls = large_orders.get('ask_wall_count', 0)
        
        if bid_walls > ask_walls and bid_walls > 2:
            score += 15
            reasons.append(f"Multiple bid walls detected ({bid_walls})")
        elif ask_walls > bid_walls and ask_walls > 2:
            score -= 15
            reasons.append(f"Multiple ask walls detected ({ask_walls})")
        
        if bid_ask_metrics.get('spread_percent', 0) < 0.05:
            score += 5
            reasons.append("Tight spread (high liquidity)")
        elif bid_ask_metrics.get('spread_percent', 0) > 0.2:
            score -= 5
            reasons.append("Wide spread (low liquidity)")
        
        direction = "BULLISH" if score > 20 else "BEARISH" if score < -20 else "NEUTRAL"
        confidence = min(abs(score), 100)
        
        return {
            'direction': direction,
            'score': score,
            'confidence': confidence,
            'reasons': reasons,
            'timeframe': '1-15 minutes'
        }
    
    def _calculate_orderbook_strength(self, bids: List, asks: List) -> Dict:
        """Calculate overall orderbook strength/quality"""
        if not bids or not asks:
            return {'strength': 0, 'quality': 'POOR'}
        
        total_volume = sum([q for _, q in bids]) + sum([q for _, q in asks])
        
        depth_count = len(bids) + len(asks)
        
        top_10_volume = sum([q for _, q in bids[:10]]) + sum([q for _, q in asks[:10]])
        concentration = (top_10_volume / total_volume * 100) if total_volume > 0 else 0
        
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        spread_pct = ((best_ask - best_bid) / best_bid * 100) if best_bid > 0 else 0
        
        strength_score = 0
        if total_volume > 10000:
            strength_score += 30
        elif total_volume > 5000:
            strength_score += 20
        elif total_volume > 1000:
            strength_score += 10
        
        if depth_count > 100:
            strength_score += 25
        elif depth_count > 50:
            strength_score += 15
        
        if spread_pct < 0.05:
            strength_score += 25
        elif spread_pct < 0.1:
            strength_score += 15
        elif spread_pct < 0.2:
            strength_score += 5
        
        if concentration < 30:
            strength_score += 20
        elif concentration < 50:
            strength_score += 10
        
        if strength_score >= 80:
            quality = "EXCELLENT"
        elif strength_score >= 60:
            quality = "GOOD"
        elif strength_score >= 40:
            quality = "MODERATE"
        elif strength_score >= 20:
            quality = "WEAK"
        else:
            quality = "POOR"
        
        return {
            'strength_score': strength_score,
            'quality': quality,
            'total_volume': total_volume,
            'depth': depth_count,
            'concentration': concentration,
            'spread_pct': spread_pct
        }
    
    def _store_orderbook_snapshot(self, snapshot: Dict):
        """Store orderbook snapshot for historical analysis"""
        self.orderbook_history.append(snapshot)
        
        if len(self.orderbook_history) > self.max_history:
            self.orderbook_history.pop(0)
    
    def get_orderbook_trend(self, periods: int = 10) -> Dict:
        """Analyze orderbook trend over recent snapshots"""
        if len(self.orderbook_history) < periods:
            return {'trend': 'INSUFFICIENT_DATA', 'change': 0}
        
        recent = self.orderbook_history[-periods:]
        
        imbalances = [s['imbalance'] for s in recent]
        
        avg_imbalance = np.mean(imbalances)
        imbalance_trend = np.polyfit(range(len(imbalances)), imbalances, 1)[0]
        
        if imbalance_trend > 5:
            trend = "STRENGTHENING_BIDS"
        elif imbalance_trend < -5:
            trend = "STRENGTHENING_ASKS"
        else:
            trend = "STABLE"
        
        return {
            'trend': trend,
            'avg_imbalance': avg_imbalance,
            'imbalance_change': imbalance_trend,
            'periods_analyzed': len(recent)
        }
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'timestamp': datetime.now(),
            'bid_ask_metrics': {},
            'large_orders': {'bid_walls': [], 'ask_walls': []},
            'imbalance_score': 0,
            'support_resistance': {'support_levels': [], 'resistance_levels': []},
            'prediction': {'direction': 'UNKNOWN', 'score': 0, 'confidence': 0, 'reasons': []},
            'orderbook_strength': {'strength_score': 0, 'quality': 'UNAVAILABLE'}
        }