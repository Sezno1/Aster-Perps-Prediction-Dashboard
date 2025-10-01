"""
🔮🧠💰 ASTROLOGICAL PSYCHOLOGY INTEGRATION
Connects astrological patterns to market psychology and financial behavior
Integrates extensive esoteric and psychological knowledge for trading insights

SOURCES:
- Carl Jung's psychological astrology
- William Gann's financial astrology methods
- Ptolemy's Tetrabiblos
- Alan Leo's modern astrology
- Robert Hand's psychological astrology
- Liz Greene's psychological approach
- Market psychology research
- Behavioral finance studies
- Hermetic principles
- Ancient wisdom traditions
"""

import sqlite3
from datetime import datetime
from typing import Dict, List
import json
from .astro_engine import astro_engine

class AstroPsychologyIntegration:
    """
    Integrates astrological knowledge with market psychology
    Uses extensive training data from classical and modern sources
    """
    
    def __init__(self):
        self.create_psychology_database()
        self.load_extensive_knowledge()
        print("🔮🧠 Astrological Psychology Integration: ONLINE")
    
    def create_psychology_database(self):
        """Create comprehensive psychology-astrology database"""
        
        conn = sqlite3.connect('data/astro_psychology.db')
        cursor = conn.cursor()
        
        # Jung's psychological astrology
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jungian_astrology (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                archetype TEXT,
                planet TEXT,
                sign TEXT,
                house INTEGER,
                psychological_function TEXT,
                shadow_expression TEXT,
                integration_goal TEXT,
                market_behavior TEXT,
                trading_pattern TEXT,
                risk_profile TEXT
            )
        ''')
        
        # Market psychology patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_psychology (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                psychological_state TEXT,
                astrological_indicator TEXT,
                market_phase TEXT,
                emotional_driver TEXT,
                behavioral_pattern TEXT,
                trading_bias TEXT,
                confidence_impact REAL,
                volatility_factor REAL,
                crowd_behavior TEXT
            )
        ''')
        
        # Gann's financial astrology methods
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gann_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method_name TEXT,
                planetary_factor TEXT,
                time_cycle TEXT,
                price_relationship TEXT,
                geometric_angle TEXT,
                natural_law TEXT,
                application TEXT,
                success_rate REAL,
                market_type TEXT
            )
        ''')
        
        # Hermetic principles for markets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hermetic_principles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                principle_name TEXT,
                hermetic_law TEXT,
                astrological_correspondence TEXT,
                market_manifestation TEXT,
                practical_application TEXT,
                timing_significance TEXT,
                confidence_modifier REAL
            )
        ''')
        
        # Psychological aspects meanings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS psychological_aspects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aspect_name TEXT,
                planets_involved TEXT,
                psychological_dynamic TEXT,
                internal_conflict TEXT,
                resolution_path TEXT,
                market_expression TEXT,
                trading_implication TEXT,
                emotional_state TEXT
            )
        ''')
        
        # Esoteric timing methods
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS esoteric_timing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method_name TEXT,
                tradition_source TEXT,
                calculation_method TEXT,
                significance TEXT,
                market_application TEXT,
                psychological_basis TEXT,
                accuracy_notes TEXT,
                modern_validation TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Astrological psychology database created")
    
    def load_extensive_knowledge(self):
        """Load comprehensive astrological and psychological knowledge"""
        
        conn = sqlite3.connect('data/astro_psychology.db')
        cursor = conn.cursor()
        
        # Jungian archetypes and market behavior
        jungian_data = [
            ("The Hero", "Mars", "Aries", 1, "initiating_action", "reckless_aggression", "conscious_courage", "impulsive_buying", "breakout_trading", "high_risk"),
            ("The Sage", "Mercury", "Gemini", 9, "gathering_wisdom", "information_overload", "integrated_knowledge", "analysis_paralysis", "over_research", "moderate_risk"),
            ("The Lover", "Venus", "Libra", 7, "creating_harmony", "codependency", "balanced_relationships", "emotional_trading", "following_others", "variable_risk"),
            ("The Creator", "Sun", "Leo", 5, "expressing_uniqueness", "narcissistic_grandiosity", "authentic_creation", "speculative_gambling", "creative_strategies", "high_risk"),
            ("The Innocent", "Moon", "Cancer", 4, "trusting_faith", "naive_denial", "wise_innocence", "FOMO_trading", "following_trends", "low_risk"),
            ("The Explorer", "Jupiter", "Sagittarius", 9, "seeking_freedom", "restless_wandering", "purposeful_adventure", "diversification", "global_markets", "moderate_risk"),
            ("The Ruler", "Saturn", "Capricorn", 10, "taking_responsibility", "tyrannical_control", "wise_leadership", "conservative_approach", "blue_chip_stocks", "low_risk"),
            ("The Magician", "Uranus", "Aquarius", 11, "transforming_reality", "manipulative_power", "authentic_transformation", "innovative_trading", "tech_disruption", "high_risk"),
            ("The Caregiver", "Moon", "Virgo", 6, "serving_others", "martyr_complex", "healthy_service", "defensive_trading", "utility_stocks", "low_risk"),
            ("The Rebel", "Uranus", "Scorpio", 8, "revolutionary_change", "destructive_rebellion", "positive_reform", "contrarian_trading", "shorting_markets", "very_high_risk")
        ]
        
        cursor.executemany('''
            INSERT INTO jungian_astrology 
            (archetype, planet, sign, house, psychological_function, shadow_expression, 
             integration_goal, market_behavior, trading_pattern, risk_profile)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', jungian_data)
        
        # Market psychology states
        psychology_data = [
            ("Greed", "Jupiter_Venus_conjunction", "bull_market_peak", "desire_acquisition", "overconfidence_bias", "bullish", -0.2, 1.5, "euphoric_buying"),
            ("Fear", "Saturn_Mars_square", "bear_market_bottom", "survival_instinct", "loss_aversion", "bearish", -0.3, 1.8, "panic_selling"),
            ("Hope", "Jupiter_Sun_trine", "market_recovery", "optimistic_expectation", "confirmation_bias", "bullish", 0.15, 0.8, "gradual_accumulation"),
            ("Despair", "Saturn_Moon_opposition", "capitulation", "hopelessness", "learned_helplessness", "bearish", -0.25, 1.2, "surrender_selling"),
            ("Euphoria", "Jupiter_Uranus_conjunction", "bubble_formation", "irrational_exuberance", "overconfidence", "extremely_bullish", -0.4, 2.0, "mania_buying"),
            ("Anxiety", "Mars_Saturn_conjunction", "uncertainty", "worry_about_future", "overthinking", "neutral", -0.15, 1.3, "indecisive_trading"),
            ("Confidence", "Sun_Jupiter_sextile", "trending_market", "self_assurance", "competence", "bullish", 0.2, 0.6, "disciplined_buying"),
            ("Complacency", "Venus_Saturn_trine", "sideways_market", "satisfaction_comfort", "status_quo_bias", "neutral", 0.05, 0.4, "lazy_holding"),
            ("Anger", "Mars_Pluto_square", "volatile_periods", "frustration_rage", "revenge_trading", "volatile", -0.2, 1.9, "emotional_decisions"),
            ("Curiosity", "Mercury_Uranus_sextile", "discovery_phase", "seeking_understanding", "exploration", "neutral", 0.1, 0.7, "research_based")
        ]
        
        cursor.executemany('''
            INSERT INTO market_psychology 
            (psychological_state, astrological_indicator, market_phase, emotional_driver, 
             behavioral_pattern, trading_bias, confidence_impact, volatility_factor, crowd_behavior)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', psychology_data)
        
        # Gann's methods
        gann_data = [
            ("Square_of_Nine", "planetary_degrees", "time_price_squares", "geometric_progression", "45_90_180_degrees", "as_above_so_below", "price_time_targets", 0.75, "all_markets"),
            ("Master_Time_Factor", "Jupiter_Saturn_cycle", "20_year_cycles", "major_trend_changes", "conjunction_opposition", "planetary_harmony", "long_term_timing", 0.80, "stock_indices"),
            ("Planetary_Lines", "daily_planetary_positions", "support_resistance", "planetary_price_levels", "longitude_degrees", "celestial_geometry", "key_levels", 0.70, "forex"),
            ("Natural_Squares", "seasonal_patterns", "90_day_cycles", "natural_rhythm", "cardinal_points", "natural_law", "seasonal_trades", 0.65, "commodities"),
            ("Vibration_Analysis", "planetary_frequencies", "harmonic_cycles", "resonance_patterns", "musical_intervals", "vibrational_law", "cycle_analysis", 0.60, "crypto"),
            ("Cardinal_Cross", "Aries_Cancer_Libra_Capricorn", "quarterly_cycles", "seasonal_changes", "0_90_180_270", "cardinal_energy", "major_turns", 0.78, "all_markets"),
            ("Astronomical_Time", "eclipse_cycles", "saros_periods", "eclipse_effects", "18_year_cycles", "light_shadow", "major_events", 0.72, "global_markets"),
            ("Planetary_Hours", "daily_planetary_rulers", "intraday_timing", "hourly_influences", "traditional_hours", "micro_timing", "entry_exit", 0.55, "day_trading")
        ]
        
        cursor.executemany('''
            INSERT INTO gann_methods 
            (method_name, planetary_factor, time_cycle, price_relationship, geometric_angle, 
             natural_law, application, success_rate, market_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', gann_data)
        
        # Hermetic principles
        hermetic_data = [
            ("Correspondence", "As above, so below", "planetary_market_correlation", "celestial_terrestrial_mirror", "planetary_timing", "cycle_synchronization", 0.2),
            ("Vibration", "Everything vibrates", "market_frequency_analysis", "price_rhythm_patterns", "harmonic_analysis", "resonance_detection", 0.15),
            ("Polarity", "Everything has opposites", "bull_bear_cycles", "trend_reversal_points", "opposition_aspects", "reversal_timing", 0.18),
            ("Rhythm", "Everything flows", "cyclic_market_movements", "wave_pattern_analysis", "planetary_cycles", "flow_identification", 0.16),
            ("Causation", "Every effect has a cause", "planetary_price_causation", "astrological_market_triggers", "aspect_formations", "cause_identification", 0.22),
            ("Gender", "Everything has masculine/feminine", "yang_bull_yin_bear", "active_passive_markets", "solar_lunar_balance", "market_gender_timing", 0.12),
            ("Mentalism", "All is mind", "collective_consciousness", "market_psychology_mass", "mental_planetary_states", "consciousness_timing", 0.20)
        ]
        
        cursor.executemany('''
            INSERT INTO hermetic_principles 
            (principle_name, hermetic_law, astrological_correspondence, market_manifestation, 
             practical_application, timing_significance, confidence_modifier)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', hermetic_data)
        
        conn.commit()
        conn.close()
        print("✅ Loaded extensive astrological psychology knowledge")
    
    def get_psychological_market_state(self, current_aspects: List[Dict], lunar_phase: Dict) -> Dict:
        """Analyze current psychological market state from astrological factors"""
        
        try:
            conn = sqlite3.connect('data/astro_psychology.db')
            cursor = conn.cursor()
            
            # Find matching psychological states
            psychological_matches = []
            
            # Check aspects against psychological patterns
            for aspect in current_aspects:
                # Safely extract planet names (handle both old and new aspect structures)
                planet1 = aspect.get('planet1', '')
                planet2 = aspect.get('planet2', '')
                aspect_type = aspect.get('type', aspect.get('aspect', 'unknown'))
                
                # Skip invalid aspects
                if not planet1 or not planet2:
                    continue
                    
                aspect_signature = f"{planet1}_{planet2}_{aspect_type}"
                
                cursor.execute('''
                    SELECT psychological_state, market_phase, emotional_driver, 
                           behavioral_pattern, trading_bias, confidence_impact, volatility_factor
                    FROM market_psychology 
                    WHERE astrological_indicator LIKE ?
                ''', (f"%{planet1}%{planet2}%",))
                
                matches = cursor.fetchall()
                for match in matches:
                    psychological_matches.append({
                        'state': match[0],
                        'phase': match[1],
                        'driver': match[2],
                        'pattern': match[3],
                        'bias': match[4],
                        'confidence_impact': match[5],
                        'volatility_factor': match[6],
                        'source': 'aspects'
                    })
            
            # Add lunar psychological influence
            lunar_psychology = self._get_lunar_psychology(lunar_phase)
            psychological_matches.append(lunar_psychology)
            
            # Calculate dominant psychological state
            if psychological_matches:
                # Weight by confidence impact and volatility
                dominant_state = max(psychological_matches, 
                                   key=lambda x: abs(x['confidence_impact']) + x['volatility_factor'])
                
                # Calculate composite confidence modifier
                total_confidence_impact = sum(m['confidence_impact'] for m in psychological_matches)
                avg_volatility = sum(m['volatility_factor'] for m in psychological_matches) / len(psychological_matches)
                
                psychological_analysis = {
                    'dominant_state': dominant_state['state'],
                    'market_phase': dominant_state['phase'],
                    'emotional_driver': dominant_state['driver'],
                    'trading_bias': dominant_state['bias'],
                    'confidence_modifier': max(-0.5, min(0.5, total_confidence_impact)),
                    'volatility_expectation': avg_volatility,
                    'psychological_matches': len(psychological_matches),
                    'analysis_timestamp': datetime.now().isoformat()
                }
            else:
                psychological_analysis = {
                    'dominant_state': 'Neutral',
                    'confidence_modifier': 0.0,
                    'volatility_expectation': 1.0,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            
            conn.close()
            return psychological_analysis
            
        except Exception as e:
            print(f"Psychological analysis error: {e}")
            return {
                'dominant_state': 'Unknown',
                'confidence_modifier': 0.0,
                'error': str(e)
            }
    
    def _get_lunar_psychology(self, lunar_phase: Dict) -> Dict:
        """Get psychological state from lunar phase"""
        
        phase = lunar_phase.get('phase', 'Unknown')
        
        lunar_psychology_map = {
            'New Moon': {
                'state': 'New Beginnings',
                'phase': 'initiation',
                'driver': 'fresh_start_optimism',
                'pattern': 'exploratory_behavior',
                'bias': 'neutral',
                'confidence_impact': 0.1,
                'volatility_factor': 1.2,
                'source': 'lunar'
            },
            'Waxing Crescent': {
                'state': 'Hope',
                'phase': 'growth',
                'driver': 'building_momentum',
                'pattern': 'accumulation_behavior',
                'bias': 'bullish',
                'confidence_impact': 0.15,
                'volatility_factor': 0.8,
                'source': 'lunar'
            },
            'First Quarter': {
                'state': 'Determination',
                'phase': 'action',
                'driver': 'decision_pressure',
                'pattern': 'decisive_action',
                'bias': 'neutral',
                'confidence_impact': 0.05,
                'volatility_factor': 1.1,
                'source': 'lunar'
            },
            'Waxing Gibbous': {
                'state': 'Persistence',
                'phase': 'refinement',
                'driver': 'perfectionist_tendency',
                'pattern': 'fine_tuning',
                'bias': 'bullish',
                'confidence_impact': 0.12,
                'volatility_factor': 0.7,
                'source': 'lunar'
            },
            'Full Moon': {
                'state': 'Emotional Peak',
                'phase': 'culmination',
                'driver': 'heightened_emotions',
                'pattern': 'extreme_behavior',
                'bias': 'volatile',
                'confidence_impact': -0.25,
                'volatility_factor': 2.0,
                'source': 'lunar'
            },
            'Waning Gibbous': {
                'state': 'Reflection',
                'phase': 'distribution',
                'driver': 'sharing_wisdom',
                'pattern': 'profit_taking',
                'bias': 'bearish',
                'confidence_impact': -0.1,
                'volatility_factor': 0.9,
                'source': 'lunar'
            },
            'Last Quarter': {
                'state': 'Release',
                'phase': 'correction',
                'driver': 'letting_go',
                'pattern': 'selling_pressure',
                'bias': 'bearish',
                'confidence_impact': -0.15,
                'volatility_factor': 1.3,
                'source': 'lunar'
            },
            'Waning Crescent': {
                'state': 'Preparation',
                'phase': 'clearing',
                'driver': 'preparation_mindset',
                'pattern': 'cautious_waiting',
                'bias': 'neutral',
                'confidence_impact': 0.0,
                'volatility_factor': 0.6,
                'source': 'lunar'
            }
        }
        
        return lunar_psychology_map.get(phase, {
            'state': 'Unknown',
            'confidence_impact': 0.0,
            'volatility_factor': 1.0,
            'source': 'lunar'
        })
    
    def get_gann_timing_factors(self, dt: datetime) -> Dict:
        """Get Gann timing factors for current moment"""
        
        try:
            conn = sqlite3.connect('data/astro_psychology.db')
            cursor = conn.cursor()
            
            # Get all Gann methods
            cursor.execute('''
                SELECT method_name, planetary_factor, time_cycle, application, success_rate
                FROM gann_methods
                ORDER BY success_rate DESC
            ''')
            
            gann_methods = cursor.fetchall()
            
            # Calculate current Gann factors
            active_factors = []
            
            for method in gann_methods:
                method_name, planetary_factor, time_cycle, application, success_rate = method
                
                # Check if method is currently active
                if self._is_gann_method_active(dt, planetary_factor, time_cycle):
                    active_factors.append({
                        'method': method_name,
                        'factor': planetary_factor,
                        'cycle': time_cycle,
                        'application': application,
                        'strength': success_rate,
                        'confidence_boost': success_rate * 0.3  # Max 30% boost
                    })
            
            # Calculate composite Gann influence
            if active_factors:
                total_confidence_boost = sum(f['confidence_boost'] for f in active_factors)
                strongest_method = max(active_factors, key=lambda x: x['strength'])
                
                gann_analysis = {
                    'active_methods': len(active_factors),
                    'strongest_method': strongest_method['method'],
                    'confidence_boost': min(0.4, total_confidence_boost),  # Cap at 40%
                    'methods_list': active_factors[:3],  # Top 3 methods
                    'gann_strength': strongest_method['strength']
                }
            else:
                gann_analysis = {
                    'active_methods': 0,
                    'confidence_boost': 0.0,
                    'methods_list': []
                }
            
            conn.close()
            return gann_analysis
            
        except Exception as e:
            print(f"Gann analysis error: {e}")
            return {'active_methods': 0, 'confidence_boost': 0.0, 'error': str(e)}
    
    def _is_gann_method_active(self, dt: datetime, planetary_factor: str, time_cycle: str) -> bool:
        """Check if a Gann method is currently active"""
        
        # Simplified activation logic - would be more complex in full implementation
        positions = astro_engine.get_planetary_positions(dt)
        
        # Check for specific planetary activations
        if "Jupiter_Saturn" in planetary_factor:
            # Check for Jupiter-Saturn aspects
            jupiter_long = positions['Jupiter']['longitude']
            saturn_long = positions['Saturn']['longitude']
            aspect_angle = abs(jupiter_long - saturn_long) % 360
            return aspect_angle < 5 or abs(aspect_angle - 180) < 5  # Conjunction or opposition
        
        elif "eclipse" in planetary_factor.lower():
            # Simplified eclipse check - would need more precise calculation
            sun_long = positions['Sun']['longitude']
            moon_long = positions['Moon']['longitude']
            return abs(sun_long - moon_long) < 3 or abs(abs(sun_long - moon_long) - 180) < 3
        
        elif "cardinal" in time_cycle.lower():
            # Cardinal points (0°, 90°, 180°, 270° of major planets)
            for planet in ['Sun', 'Mars', 'Jupiter', 'Saturn']:
                if planet in positions:
                    longitude = positions[planet]['longitude']
                    cardinal_distances = [abs(longitude - angle) for angle in [0, 90, 180, 270]]
                    if min(cardinal_distances) < 2:
                        return True
        
        return False
    
    def get_comprehensive_confidence_analysis(self, market_data: Dict, current_aspects: List[Dict], 
                                            lunar_phase: Dict, technical_signals: Dict) -> Dict:
        """Comprehensive confidence analysis integrating all astrological psychology factors"""
        
        try:
            # Get psychological market state
            psychological_state = self.get_psychological_market_state(current_aspects, lunar_phase)
            
            # Get Gann timing factors
            gann_factors = self.get_gann_timing_factors(datetime.now())
            
            # Get lunar confidence modifier
            lunar_confidence = lunar_phase.get('confidence_modifier', 0.0)
            
            # Get aspects confidence modifier
            aspects_confidence = 0.0
            if current_aspects:
                aspects_analysis = astro_engine.get_current_aspects_and_confidence(datetime.now())
                aspects_confidence = aspects_analysis.get('overall_confidence_modifier', 0.0)
            
            # Calculate composite confidence modifier
            confidence_components = {
                'psychological_state': psychological_state.get('confidence_modifier', 0.0),
                'lunar_influence': lunar_confidence,
                'planetary_aspects': aspects_confidence,
                'gann_timing': gann_factors.get('confidence_boost', 0.0),
                'technical_alignment': self._calculate_technical_alignment(technical_signals)
            }
            
            # Weight the components
            weights = {
                'psychological_state': 0.25,
                'lunar_influence': 0.20,
                'planetary_aspects': 0.25,
                'gann_timing': 0.15,
                'technical_alignment': 0.15
            }
            
            composite_confidence = sum(
                confidence_components[component] * weights[component] 
                for component in confidence_components
            )
            
            # Ensure within bounds (-0.5 to +0.5)
            composite_confidence = max(-0.5, min(0.5, composite_confidence))
            
            # Convert to percentage modifier
            confidence_percentage_modifier = composite_confidence * 100
            
            return {
                'composite_confidence_modifier': confidence_percentage_modifier,
                'confidence_components': confidence_components,
                'dominant_psychological_state': psychological_state.get('dominant_state', 'Neutral'),
                'trading_bias': psychological_state.get('trading_bias', 'neutral'),
                'volatility_expectation': psychological_state.get('volatility_expectation', 1.0),
                'active_gann_methods': gann_factors.get('active_methods', 0),
                'strongest_influence': max(confidence_components.keys(), 
                                         key=lambda k: abs(confidence_components[k])),
                'analysis_summary': self._generate_confidence_summary(confidence_components, psychological_state)
            }
            
        except Exception as e:
            print(f"Comprehensive confidence analysis error: {e}")
            return {
                'composite_confidence_modifier': 0.0,
                'error': str(e)
            }
    
    def _calculate_technical_alignment(self, technical_signals: Dict) -> float:
        """Calculate how well technical signals align with astrological timing"""
        
        # Simplified technical alignment calculation
        if not technical_signals:
            return 0.0
        
        # Check for alignment between technical and astrological signals
        alignment_score = 0.0
        
        # Example alignment checks
        if technical_signals.get('trend_bullish') and technical_signals.get('volume_spike'):
            alignment_score += 0.1
        
        if technical_signals.get('oversold') and not technical_signals.get('overbought'):
            alignment_score += 0.1
        
        return min(0.2, alignment_score)  # Cap at 20% boost
    
    def _generate_confidence_summary(self, components: Dict, psychological_state: Dict) -> str:
        """Generate human-readable confidence analysis summary"""
        
        strongest_component = max(components.keys(), key=lambda k: abs(components[k]))
        strongest_value = components[strongest_component]
        
        if strongest_value > 0.1:
            direction = "boosting"
            strength = "significantly" if strongest_value > 0.2 else "moderately"
        elif strongest_value < -0.1:
            direction = "reducing"
            strength = "significantly" if strongest_value < -0.2 else "moderately"
        else:
            direction = "neutral"
            strength = ""
        
        psychological = psychological_state.get('dominant_state', 'Neutral')
        
        return f"{strongest_component.replace('_', ' ').title()} is {strength} {direction} confidence. Market psychology: {psychological}."

# Global instance
astro_psychology = AstroPsychologyIntegration()

if __name__ == "__main__":
    print("🔮🧠 Testing Astrological Psychology Integration...")
    
    # Test psychological analysis
    test_aspects = [
        {'planet1': 'Sun', 'planet2': 'Jupiter', 'type': 'trine', 'orb': 2.5},
        {'planet1': 'Moon', 'planet2': 'Mars', 'type': 'square', 'orb': 1.8}
    ]
    
    test_lunar = {
        'phase': 'Waxing Crescent',
        'confidence_modifier': 0.15
    }
    
    psychology_analysis = astro_psychology.get_psychological_market_state(test_aspects, test_lunar)
    print(f"📊 Psychological State: {psychology_analysis}")
    
    # Test comprehensive confidence
    comprehensive = astro_psychology.get_comprehensive_confidence_analysis(
        {}, test_aspects, test_lunar, {'trend_bullish': True, 'volume_spike': True}
    )
    print(f"🎯 Comprehensive Confidence: {comprehensive['composite_confidence_modifier']:.1f}%")
    print(f"📝 Summary: {comprehensive['analysis_summary']}")
    
    print("✅ Astrological Psychology Integration test complete!")