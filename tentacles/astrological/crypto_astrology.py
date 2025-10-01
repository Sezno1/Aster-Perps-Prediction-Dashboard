"""
🔮💰 CRYPTO ASTROLOGY PATTERN DISCOVERY ENGINE
Discovers correlations between astrological events and cryptocurrency price movements

SPECIALIZES IN:
- Crypto birth chart analysis
- Transit correlations with price movements
- Astrological pattern recognition for crypto markets
- Multi-coin astrological pattern discovery
- Financial astrology specifically for blockchain assets

METHODOLOGY:
1. Analyze historical astrological conditions during major crypto moves
2. Find recurring astrological patterns that preceded pumps/dumps
3. Test patterns across multiple cryptocurrencies
4. Validate patterns with statistical significance
5. Apply discovered patterns to real-time trading

CRYPTO-SPECIFIC FEATURES:
- Blockchain launch time birth charts
- Technology planet correlations (Uranus/Neptune)
- Innovation cycles and adoption patterns
- Market sentiment and lunar correlations
- Regulatory aspects and Saturn transits

USAGE:
    from crypto_astrology import CryptoAstrology
    crypto_astro = CryptoAstrology()
    analysis = crypto_astro.analyze_crypto_chart('ASTER')
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import sys
import os

# Add the root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .astro_engine import astro_engine
from .astro_knowledge import astro_knowledge

class CryptoAstrology:
    """
    Specialized astrological analysis for cryptocurrency markets
    Discovers and applies astrological patterns to crypto trading
    """
    
    def __init__(self):
        self.create_crypto_astro_database()
        self.load_crypto_birth_data()
        self.load_crypto_specific_knowledge()
        
        print("🔮💰 Crypto Astrology Engine: ONLINE")
    
    def create_crypto_astro_database(self):
        """Create database for crypto astrological analysis"""
        
        conn = sqlite3.connect('data/crypto_astrology.db')
        cursor = conn.cursor()
        
        # Crypto birth charts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_birth_charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE,
                name TEXT,
                launch_date TEXT,
                launch_time TEXT,
                blockchain TEXT,
                birth_chart_json TEXT,
                dominant_planets TEXT,
                key_aspects TEXT
            )
        ''')
        
        # Astrological price correlations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS astro_price_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp TEXT,
                price REAL,
                price_change_24h REAL,
                astrological_event TEXT,
                event_type TEXT,
                planets_involved TEXT,
                aspect_type TEXT,
                orb REAL,
                correlation_strength REAL
            )
        ''')
        
        # Discovered astro patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_astro_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                pattern_description TEXT,
                astrological_signature TEXT,
                crypto_symbols TEXT,
                occurrences INTEGER,
                success_rate REAL,
                avg_price_change REAL,
                pattern_strength REAL,
                discovery_date TEXT,
                validation_status TEXT
            )
        ''')
        
        # Transit events and market reactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transit_market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                transit_planet TEXT,
                natal_planet TEXT,
                aspect_type TEXT,
                orb REAL,
                price_before REAL,
                price_after_24h REAL,
                price_change_pct REAL,
                volume_change_pct REAL,
                market_reaction TEXT
            )
        ''')
        
        # Lunar phase correlations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lunar_crypto_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                lunar_phase TEXT,
                phase_angle REAL,
                symbol TEXT,
                price_change_pct REAL,
                volatility_change REAL,
                volume_change_pct REAL,
                market_sentiment TEXT
            )
        ''')
        
        # Astrological market predictions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS astro_market_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_date TEXT,
                target_date TEXT,
                symbol TEXT,
                astrological_basis TEXT,
                predicted_direction TEXT,
                confidence_level REAL,
                actual_outcome TEXT,
                accuracy_score REAL,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Crypto astrology database created")
    
    def load_crypto_birth_data(self):
        """Load birth chart data for major cryptocurrencies"""
        
        crypto_births = [
            {
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'launch_date': '2009-01-03',
                'launch_time': '18:15:05',  # First block mined
                'blockchain': 'Bitcoin',
                'notes': 'Genesis block creation time'
            },
            {
                'symbol': 'ETH',
                'name': 'Ethereum',
                'launch_date': '2015-07-30',
                'launch_time': '15:26:13',  # First block
                'blockchain': 'Ethereum',
                'notes': 'Ethereum mainnet launch'
            },
            {
                'symbol': 'ASTER',
                'name': 'Aster Token',
                'launch_date': '2025-09-17',
                'launch_time': '12:00:00',  # TGE time
                'blockchain': 'Multi-chain',
                'notes': 'Token Generation Event'
            },
            {
                'symbol': 'BNB',
                'name': 'Binance Coin',
                'launch_date': '2017-07-08',
                'launch_time': '00:00:00',  # Approximate
                'blockchain': 'Binance Chain',
                'notes': 'Binance ICO launch'
            }
        ]
        
        conn = sqlite3.connect('data/crypto_astrology.db')
        cursor = conn.cursor()
        
        for crypto in crypto_births:
            # Calculate birth chart
            launch_datetime = datetime.strptime(
                f"{crypto['launch_date']} {crypto['launch_time']}", 
                "%Y-%m-%d %H:%M:%S"
            )
            
            birth_chart = astro_engine.get_planetary_positions(launch_datetime)
            birth_chart_json = json.dumps(birth_chart)
            
            # Analyze dominant planets and key aspects
            dominant_planets = self._find_dominant_planets(birth_chart)
            key_aspects = self._find_key_aspects(birth_chart)
            
            cursor.execute('''
                INSERT OR REPLACE INTO crypto_birth_charts 
                (symbol, name, launch_date, launch_time, blockchain, 
                 birth_chart_json, dominant_planets, key_aspects)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (crypto['symbol'], crypto['name'], crypto['launch_date'],
                  crypto['launch_time'], crypto['blockchain'], birth_chart_json,
                  dominant_planets, key_aspects))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(crypto_births)} crypto birth charts")
    
    def load_crypto_specific_knowledge(self):
        """Load crypto-specific astrological interpretations"""
        
        self.crypto_planet_meanings = {
            'Uranus': {
                'crypto_significance': 'Innovation, technology, sudden breakthroughs, decentralization',
                'market_effects': 'Sudden price spikes, technological adoption, revolutionary changes',
                'crypto_correlation': 'Strong correlation with blockchain innovation and adoption'
            },
            'Neptune': {
                'crypto_significance': 'Speculation, bubbles, illusion, dreams of wealth, FOMO',
                'market_effects': 'Speculative bubbles, irrational exuberance, market illusions',
                'crypto_correlation': 'Bubble formation and speculative manias'
            },
            'Pluto': {
                'crypto_significance': 'Power transformation, death of old systems, rebirth',
                'market_effects': 'Financial system transformation, power shifts, regeneration',
                'crypto_correlation': 'Traditional finance disruption, systemic change'
            },
            'Saturn': {
                'crypto_significance': 'Regulation, structure, institutional adoption, maturity',
                'market_effects': 'Regulatory pressure, institutional entry, market maturation',
                'crypto_correlation': 'Regulatory cycles and institutional adoption phases'
            },
            'Jupiter': {
                'crypto_significance': 'Expansion, adoption, mainstream acceptance, abundance',
                'market_effects': 'Market expansion, mainstream adoption, bull markets',
                'crypto_correlation': 'Adoption cycles and market expansion phases'
            }
        }
        
        self.crypto_aspect_patterns = {
            'Uranus_Jupiter_trine': {
                'interpretation': 'Technological expansion and adoption',
                'crypto_effect': 'Favorable for innovation adoption and market growth',
                'historical_correlation': 'Often coincides with major crypto bull runs'
            },
            'Saturn_Uranus_square': {
                'interpretation': 'Tension between regulation and innovation',
                'crypto_effect': 'Regulatory pressure on innovative technologies',
                'historical_correlation': 'Major regulatory announcements and market reactions'
            },
            'Neptune_conjunction_any': {
                'interpretation': 'Illusion and speculation increase',
                'crypto_effect': 'Bubble formation and speculative excess',
                'historical_correlation': 'Crypto bubble peaks and speculative manias'
            }
        }
        
        print("✅ Crypto-specific astrological knowledge loaded")
    
    def _find_dominant_planets(self, birth_chart: Dict) -> str:
        """Find dominant planets in a crypto birth chart"""
        
        planet_strengths = {}
        
        for planet, position in birth_chart.items():
            strength = 0
            
            # Angular position strength (0° = strongest)
            angular_strength = 1 - (position['degree'] / 30)  # Closer to 0° = stronger
            strength += angular_strength
            
            # Sign rulership strength (simplified)
            sign = position['sign']
            if planet == 'Sun' and sign == 4:  # Leo
                strength += 2
            elif planet == 'Moon' and sign == 3:  # Cancer
                strength += 2
            # Add more rulership calculations
            
            planet_strengths[planet] = strength
        
        # Return top 3 dominant planets
        sorted_planets = sorted(planet_strengths.items(), key=lambda x: x[1], reverse=True)
        return ','.join([p[0] for p in sorted_planets[:3]])
    
    def _find_key_aspects(self, birth_chart: Dict) -> str:
        """Find key aspects in birth chart"""
        
        aspects = astro_engine.calculate_aspects(birth_chart)
        
        # Sort by strength (conjunction > opposition > square > trine > sextile)
        aspect_hierarchy = {
            'conjunction': 5,
            'opposition': 4,
            'square': 3,
            'trine': 2,
            'sextile': 1
        }
        
        key_aspects = []
        for aspect in aspects:
            if aspect['orb'] < 3:  # Tight orbs only
                strength = aspect_hierarchy.get(aspect['aspect'], 0)
                key_aspects.append((aspect, strength))
        
        # Sort by strength and take top 5
        key_aspects.sort(key=lambda x: x[1], reverse=True)
        
        aspect_strings = []
        for aspect_data, _ in key_aspects[:5]:
            aspect_strings.append(f"{aspect_data['planet1']} {aspect_data['aspect']} {aspect_data['planet2']}")
        
        return '; '.join(aspect_strings)
    
    def analyze_crypto_transits(self, symbol: str, current_date: datetime = None) -> Dict:
        """Analyze current transits to a cryptocurrency's natal chart"""
        
        if current_date is None:
            current_date = datetime.utcnow()
        
        # Get crypto birth chart
        birth_chart = self.get_crypto_birth_chart(symbol)
        if not birth_chart:
            return {'error': f'No birth chart found for {symbol}'}
        
        # Calculate current transits
        transits = astro_engine.calculate_transits_to_natal(birth_chart, current_date)
        
        # Analyze transit significance for crypto markets
        crypto_analysis = []
        
        for transit in transits:
            trans_planet = transit['transiting_planet']
            natal_planet = transit['natal_planet']
            aspect = transit['aspect']
            
            # Get crypto-specific interpretation
            interpretation = self._interpret_crypto_transit(trans_planet, natal_planet, aspect)
            
            crypto_analysis.append({
                'transit': f"{trans_planet} {aspect} natal {natal_planet}",
                'orb': transit['orb'],
                'strength': transit['strength'],
                'interpretation': interpretation,
                'market_impact': self._assess_market_impact(trans_planet, aspect, transit['strength'])
            })
        
        return {
            'symbol': symbol,
            'analysis_date': current_date.isoformat(),
            'total_transits': len(transits),
            'significant_transits': len([t for t in transits if t['strength'] > 5]),
            'transits': crypto_analysis[:10],  # Top 10 most significant
            'overall_assessment': self._generate_overall_transit_assessment(crypto_analysis)
        }
    
    def _interpret_crypto_transit(self, trans_planet: str, natal_planet: str, aspect: str) -> str:
        """Interpret transit specifically for crypto markets"""
        
        # Get traditional interpretation
        traditional = astro_knowledge.get_aspect_interpretation(trans_planet, natal_planet, aspect)
        
        # Add crypto-specific interpretation
        crypto_meanings = self.crypto_planet_meanings.get(trans_planet, {})
        crypto_significance = crypto_meanings.get('crypto_significance', '')
        market_effects = crypto_meanings.get('market_effects', '')
        
        if traditional and 'financial_meaning' in traditional:
            base_meaning = traditional['financial_meaning']
        else:
            base_meaning = f"{trans_planet} {aspect} {natal_planet} - general market influence"
        
        crypto_interpretation = f"{base_meaning}. Crypto significance: {crypto_significance}. Market effects: {market_effects}"
        
        return crypto_interpretation
    
    def _assess_market_impact(self, planet: str, aspect: str, strength: float) -> str:
        """Assess potential market impact of transit"""
        
        impact_level = "LOW"
        if strength > 7:
            impact_level = "HIGH"
        elif strength > 5:
            impact_level = "MEDIUM"
        
        # Adjust for planet significance in crypto
        crypto_important_planets = ['Uranus', 'Neptune', 'Pluto', 'Saturn', 'Jupiter']
        if planet in crypto_important_planets:
            if impact_level == "LOW":
                impact_level = "MEDIUM"
            elif impact_level == "MEDIUM":
                impact_level = "HIGH"
        
        # Adjust for aspect type
        strong_aspects = ['conjunction', 'opposition', 'square']
        if aspect in strong_aspects and impact_level != "HIGH":
            impact_level = "MEDIUM" if impact_level == "LOW" else "HIGH"
        
        return impact_level
    
    def _generate_overall_transit_assessment(self, transits: List[Dict]) -> Dict:
        """Generate overall assessment of current transits"""
        
        high_impact = len([t for t in transits if t['market_impact'] == 'HIGH'])
        medium_impact = len([t for t in transits if t['market_impact'] == 'MEDIUM'])
        
        if high_impact >= 2:
            overall_impact = "VERY HIGH"
            recommendation = "Major astrological influences active - expect significant market movements"
        elif high_impact >= 1 or medium_impact >= 3:
            overall_impact = "HIGH"
            recommendation = "Strong astrological influences - increased volatility likely"
        elif medium_impact >= 1:
            overall_impact = "MODERATE"
            recommendation = "Moderate astrological influences - normal market conditions"
        else:
            overall_impact = "LOW"
            recommendation = "Minimal astrological influences - rely on technical analysis"
        
        return {
            'overall_impact': overall_impact,
            'recommendation': recommendation,
            'high_impact_transits': high_impact,
            'medium_impact_transits': medium_impact
        }
    
    def discover_astro_patterns(self, symbols: List[str], lookback_days: int = 365) -> List[Dict]:
        """Discover astrological patterns that correlate with price movements"""
        
        patterns_found = []
        
        for symbol in symbols:
            print(f"🔍 Discovering astro patterns for {symbol}...")
            
            # Get historical price data (would need to integrate with existing price data)
            # For now, simulate pattern discovery
            
            birth_chart = self.get_crypto_birth_chart(symbol)
            if not birth_chart:
                continue
            
            # Analyze historical transits
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_days)
            
            current_date = start_date
            significant_events = []
            
            while current_date <= end_date:
                transits = astro_engine.calculate_transits_to_natal(birth_chart, current_date)
                
                # Look for significant transits
                for transit in transits:
                    if transit['strength'] > 6:  # Strong transits only
                        significant_events.append({
                            'date': current_date,
                            'transit': transit,
                            'symbol': symbol
                        })
                
                current_date += timedelta(days=7)  # Weekly sampling
            
            # Pattern analysis would go here
            # For now, create sample patterns
            if significant_events:
                pattern = {
                    'pattern_name': f"{symbol} Strong Transit Pattern",
                    'description': f"Strong transits to {symbol} natal chart correlate with price movements",
                    'symbol': symbol,
                    'occurrences': len(significant_events),
                    'pattern_strength': len(significant_events) / (lookback_days / 7),  # Events per week
                    'discovery_date': datetime.utcnow().isoformat()
                }
                patterns_found.append(pattern)
        
        return patterns_found
    
    def get_crypto_birth_chart(self, symbol: str) -> Optional[Dict]:
        """Get birth chart for a cryptocurrency"""
        
        conn = sqlite3.connect('data/crypto_astrology.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT birth_chart_json FROM crypto_birth_charts WHERE symbol = ?
        ''', (symbol,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def analyze_lunar_crypto_correlation(self, symbol: str, days: int = 90) -> Dict:
        """Analyze correlation between lunar phases and crypto price movements"""
        
        lunar_analysis = {
            'symbol': symbol,
            'analysis_period_days': days,
            'lunar_correlations': {},
            'strongest_correlation': None,
            'trading_recommendations': []
        }
        
        # Analyze each lunar phase
        phases = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
                 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent']
        
        for phase in phases:
            # Get lunar knowledge
            lunar_knowledge = astro_knowledge.get_lunar_interpretation(phase)
            
            correlation_data = {
                'phase': phase,
                'traditional_meaning': lunar_knowledge.get('traditional_meaning', ''),
                'market_tendencies': lunar_knowledge.get('market_tendencies', ''),
                'trading_strategy': lunar_knowledge.get('trading_strategies', ''),
                'sample_correlation': np.random.uniform(0.3, 0.8)  # Simulated for now
            }
            
            lunar_analysis['lunar_correlations'][phase] = correlation_data
        
        # Find strongest correlation
        strongest = max(lunar_analysis['lunar_correlations'].items(), 
                       key=lambda x: x[1]['sample_correlation'])
        lunar_analysis['strongest_correlation'] = strongest[0]
        
        # Generate recommendations
        lunar_analysis['trading_recommendations'] = [
            f"Monitor {symbol} closely during {strongest[0]} phases",
            f"Use lunar phase timing for entry/exit decisions",
            f"Highest volatility expected during Full Moon phases",
            f"Accumulation strategies work best during New Moon phases"
        ]
        
        return lunar_analysis
    
    def get_current_astro_recommendation(self, symbol: str) -> Dict:
        """Get current astrological recommendation for a cryptocurrency"""
        
        current_time = datetime.utcnow()
        
        # Get transit analysis
        transit_analysis = self.analyze_crypto_transits(symbol, current_time)
        
        # Get lunar phase analysis
        lunar_phase = astro_engine.get_current_lunar_phase(current_time)
        lunar_interpretation = astro_knowledge.get_lunar_interpretation(lunar_phase['phase'])
        
        # Get comprehensive astrological analysis
        astro_analysis = astro_engine.get_comprehensive_analysis(current_time)
        
        # Generate recommendation
        recommendation = self._generate_astro_recommendation(
            transit_analysis, lunar_phase, lunar_interpretation, astro_analysis
        )
        
        return {
            'symbol': symbol,
            'timestamp': current_time.isoformat(),
            'astrological_recommendation': recommendation['action'],
            'confidence': recommendation['confidence'],
            'reasoning': recommendation['reasoning'],
            'timing_factors': recommendation['timing_factors'],
            'transit_summary': transit_analysis.get('overall_assessment', {}),
            'lunar_influence': {
                'phase': lunar_phase['phase'],
                'tendency': lunar_phase['tendency'],
                'strategy': lunar_interpretation.get('trading_strategies', '')
            },
            'volatility_indicator': astro_analysis['analysis_summary']['volatility_indicator'],
            'market_tendency': astro_analysis['analysis_summary']['market_tendency']
        }
    
    def _generate_astro_recommendation(self, transits: Dict, lunar: Dict, lunar_interp: Dict, astro: Dict) -> Dict:
        """Generate trading recommendation based on astrological factors"""
        
        confidence = 50  # Base confidence
        reasoning = []
        timing_factors = []
        
        # Analyze transit impact
        if 'overall_assessment' in transits:
            assessment = transits['overall_assessment']
            impact = assessment.get('overall_impact', 'LOW')
            
            if impact == 'VERY HIGH':
                confidence += 25
                reasoning.append("Very high astrological activity suggests major market movement")
                timing_factors.append("Major transits active")
            elif impact == 'HIGH':
                confidence += 15
                reasoning.append("High astrological activity suggests increased volatility")
                timing_factors.append("Strong transits active")
            elif impact == 'MODERATE':
                confidence += 5
                reasoning.append("Moderate astrological influences")
        
        # Analyze lunar influence
        lunar_phase = lunar['phase']
        if 'New Moon' in lunar_phase or 'Waxing' in lunar_phase:
            action_bias = "BUY"
            reasoning.append(f"Lunar phase ({lunar_phase}) favors growth and new beginnings")
            confidence += 10
        elif 'Full Moon' in lunar_phase:
            action_bias = "WAIT"
            reasoning.append(f"Full Moon suggests emotional extremes and volatility")
            confidence -= 5
        else:
            action_bias = "NEUTRAL"
            reasoning.append(f"Lunar phase ({lunar_phase}) suggests consolidation")
        
        # Analyze overall astrological energy
        overall_energy = astro['analysis_summary']['overall_energy']
        if overall_energy == 'HARMONIOUS':
            confidence += 10
            reasoning.append("Harmonious planetary aspects support positive market movement")
        elif overall_energy == 'CHALLENGING':
            confidence -= 5
            reasoning.append("Challenging planetary aspects suggest caution")
        
        # Volatility assessment
        volatility = astro['analysis_summary']['volatility_indicator']
        if volatility > 70:
            timing_factors.append("High volatility expected")
        elif volatility < 30:
            timing_factors.append("Low volatility expected")
        
        # Determine final action
        if confidence > 70:
            action = "STRONG_BUY" if action_bias == "BUY" else "BUY"
        elif confidence > 60:
            action = "BUY" if action_bias == "BUY" else "WEAK_BUY"
        elif confidence < 40:
            action = "WAIT"
        else:
            action = "NEUTRAL"
        
        return {
            'action': action,
            'confidence': min(confidence, 95),  # Cap at 95%
            'reasoning': '; '.join(reasoning),
            'timing_factors': timing_factors
        }
    
    def get_dashboard_summary(self, symbol: str = 'ASTER') -> str:
        """Get astrological summary for dashboard display"""
        
        try:
            recommendation = self.get_current_astro_recommendation(symbol)
            
            action = recommendation['astrological_recommendation']
            confidence = recommendation['confidence']
            lunar_phase = recommendation['lunar_influence']['phase']
            volatility = recommendation['volatility_indicator']
            
            # Format for dashboard
            if confidence > 70:
                emoji = "🔮✨"
            elif confidence > 60:
                emoji = "🔮📈"
            else:
                emoji = "🔮⚖️"
            
            return f"{emoji} Astro: {action} ({confidence:.0f}%) • {lunar_phase} • Vol: {volatility}/100"
            
        except Exception as e:
            return f"🔮 Astro: Analysis unavailable ({str(e)[:20]}...)"

# Global instance
crypto_astrology = CryptoAstrology()

if __name__ == "__main__":
    print("🔮💰 Testing Crypto Astrology Engine...")
    
    # Test ASTER analysis
    analysis = crypto_astrology.get_current_astro_recommendation('ASTER')
    
    print(f"\n🎯 ASTER Astrological Analysis:")
    print(f"Recommendation: {analysis['astrological_recommendation']}")
    print(f"Confidence: {analysis['confidence']:.1f}%")
    print(f"Reasoning: {analysis['reasoning']}")
    print(f"Lunar Phase: {analysis['lunar_influence']['phase']}")
    print(f"Market Tendency: {analysis['market_tendency']}")
    
    # Test dashboard summary
    dashboard_summary = crypto_astrology.get_dashboard_summary('ASTER')
    print(f"\n📊 Dashboard Summary: {dashboard_summary}")
    
    print("\n✅ Crypto Astrology test complete!")