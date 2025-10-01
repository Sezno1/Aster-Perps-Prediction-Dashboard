"""
📚 ASTROLOGICAL KNOWLEDGE DATABASE
Comprehensive training data for AI astrological expertise

SOURCES:
- Ancient texts (Ptolemy's Tetrabiblos, William Lilly)
- Modern financial astrology (W.D. Gann, Raymond Merriman)
- Traditional astrological interpretations
- Financial market correlations
- Esoteric wisdom and natural cycles

KNOWLEDGE AREAS:
- Planetary meanings and cycles
- Aspect interpretations
- Fixed star influences
- Lunar phase correlations
- Financial astrology principles
- Market timing techniques
- Astrological psychology
- Hermetic principles

USAGE:
    from astro_knowledge import AstroKnowledge
    knowledge = AstroKnowledge()
    interpretation = knowledge.interpret_aspect('Jupiter', 'trine', 'Venus')
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class AstroKnowledge:
    """
    Comprehensive astrological knowledge database
    Trains AI to become expert astrologer
    """
    
    def __init__(self):
        self.create_knowledge_database()
        self.load_ancient_wisdom()
        self.load_modern_financial_astrology()
        self.load_planetary_knowledge()
        self.load_aspect_interpretations()
        self.load_fixed_star_wisdom()
        self.load_lunar_knowledge()
        self.load_hermetic_principles()
        
        print("📚 Astrological Knowledge Database: LOADED")
    
    def create_knowledge_database(self):
        """Create comprehensive astrological knowledge database"""
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        # Ancient wisdom table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ancient_wisdom (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                topic TEXT,
                original_text TEXT,
                interpretation TEXT,
                relevance_to_markets TEXT,
                keywords TEXT
            )
        ''')
        
        # Planetary knowledge
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planetary_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planet TEXT,
                traditional_meaning TEXT,
                financial_meaning TEXT,
                cycle_period REAL,
                keywords TEXT,
                market_correlations TEXT,
                aspects_specialties TEXT
            )
        ''')
        
        # Aspect interpretations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aspect_interpretations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planet1 TEXT,
                planet2 TEXT,
                aspect_type TEXT,
                traditional_meaning TEXT,
                financial_meaning TEXT,
                market_timing TEXT,
                orb_sensitivity REAL,
                historical_examples TEXT
            )
        ''')
        
        # Fixed star knowledge
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fixed_star_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                star_name TEXT,
                constellation TEXT,
                magnitude REAL,
                astrological_nature TEXT,
                financial_influence TEXT,
                historical_correlations TEXT,
                modern_interpretations TEXT
            )
        ''')
        
        # Lunar wisdom
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lunar_wisdom (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_type TEXT,
                traditional_meaning TEXT,
                market_tendencies TEXT,
                volatility_patterns TEXT,
                trading_strategies TEXT,
                psychological_effects TEXT
            )
        ''')
        
        # Financial astrology principles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_astrology_principles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                principle_name TEXT,
                description TEXT,
                originator TEXT,
                mathematical_basis TEXT,
                market_applications TEXT,
                success_rate TEXT,
                modern_validation TEXT
            )
        ''')
        
        # Hermetic principles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hermetic_principles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                principle_name TEXT,
                hermetic_law TEXT,
                astrological_application TEXT,
                market_manifestation TEXT,
                practical_usage TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Astrological knowledge database created")
    
    def load_ancient_wisdom(self):
        """Load wisdom from ancient astrological texts"""
        
        ancient_texts = [
            {
                'source': 'Ptolemy Tetrabiblos',
                'topic': 'Planetary Influences',
                'original_text': 'The Sun and Moon have the most influence over earthly affairs, the Sun as the ruling principle and the Moon as the principle of change.',
                'interpretation': 'The Sun represents the main trend and fundamental value, while the Moon represents daily fluctuations and public sentiment.',
                'relevance_to_markets': 'Solar aspects indicate major trend changes, lunar aspects indicate daily trading patterns',
                'keywords': 'sun,moon,influence,earthly_affairs,ruling_principle,change'
            },
            {
                'source': 'Ptolemy Tetrabiblos',
                'topic': 'Planetary Powers',
                'original_text': 'Saturn tends to cool and dry, Jupiter to warm and humidify moderately, Mars to dry and burn, Venus to warm and humidify.',
                'interpretation': 'Each planet has distinct energetic qualities that manifest in market behavior - Saturn restricts, Jupiter expands, Mars energizes, Venus stabilizes.',
                'relevance_to_markets': 'Saturn = bear markets/corrections, Jupiter = bull markets, Mars = volatility, Venus = stable growth',
                'keywords': 'saturn,jupiter,mars,venus,cooling,warming,drying,humidifying'
            },
            {
                'source': 'William Lilly Christian Astrology',
                'topic': 'Aspect Strength',
                'original_text': 'The conjunction is the strongest aspect, followed by opposition, square, trine, and sextile.',
                'interpretation': 'Market impact follows this hierarchy - conjunctions create the strongest events, oppositions create peaks/troughs.',
                'relevance_to_markets': 'Prioritize conjunctions for major turning points, oppositions for volatility peaks',
                'keywords': 'conjunction,opposition,square,trine,sextile,strength,aspects'
            },
            {
                'source': 'William Lilly Christian Astrology',
                'topic': 'Planetary Hours',
                'original_text': 'Each day and hour is ruled by a planet, and affairs undertaken during that time partake of the planet\'s nature.',
                'interpretation': 'Trading timing can be optimized by planetary hours - Mars hours for quick trades, Venus hours for accumulation.',
                'relevance_to_markets': 'Intraday timing using planetary hour rulership',
                'keywords': 'planetary_hours,timing,rulership,nature,affairs'
            },
            {
                'source': 'Ancient Hermetic Tradition',
                'topic': 'As Above So Below',
                'original_text': 'That which is below is like that which is above, and that which is above is like that which is below.',
                'interpretation': 'Celestial patterns reflect in market patterns - planetary cycles manifest as market cycles.',
                'relevance_to_markets': 'Fundamental principle underlying all astrological market analysis',
                'keywords': 'hermetic,above,below,reflection,patterns,cycles'
            }
        ]
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        for text in ancient_texts:
            cursor.execute('''
                INSERT INTO ancient_wisdom 
                (source, topic, original_text, interpretation, relevance_to_markets, keywords)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (text['source'], text['topic'], text['original_text'], 
                  text['interpretation'], text['relevance_to_markets'], text['keywords']))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(ancient_texts)} ancient wisdom entries")
    
    def load_modern_financial_astrology(self):
        """Load modern financial astrology principles"""
        
        principles = [
            {
                'principle_name': 'Gann Planetary Price Theory',
                'description': 'W.D. Gann discovered that market prices move in harmony with planetary cycles, with specific mathematical relationships.',
                'originator': 'W.D. Gann',
                'mathematical_basis': 'Square of 9, planetary degrees converted to price levels, time-price symmetry',
                'market_applications': 'Support/resistance levels, time windows for reversals, price targets',
                'success_rate': 'Historical 80-90% accuracy on major turning points',
                'modern_validation': 'Quantum physics suggests vibrational resonance between celestial and terrestrial phenomena'
            },
            {
                'principle_name': 'Merriman Geocosmic Theory',
                'description': 'Raymond Merriman\'s research shows correlation between planetary aspects and market reversals.',
                'originator': 'Raymond Merriman',
                'mathematical_basis': 'Statistical analysis of planetary aspects vs market turning points',
                'market_applications': 'Major trend reversal timing, volatility prediction, sector rotation',
                'success_rate': 'Gold Star winner for market timing accuracy',
                'modern_validation': 'Peer-reviewed studies show statistical significance'
            },
            {
                'principle_name': 'Jupiter-Saturn Cycle Theory',
                'description': 'The 20-year Jupiter-Saturn cycle correlates with major economic and market cycles.',
                'originator': 'Multiple researchers',
                'mathematical_basis': '19.86-year synodic cycle of Jupiter and Saturn',
                'market_applications': 'Long-term economic forecasting, generational investment themes',
                'success_rate': 'Documented correlation with major economic turning points',
                'modern_validation': 'Historical analysis shows consistent pattern over centuries'
            },
            {
                'principle_name': 'Lunar Trading Cycles',
                'description': 'Market volatility and sentiment correlate with lunar phases and lunar aspects.',
                'originator': 'Traditional astrology, validated by modern research',
                'mathematical_basis': '29.53-day lunar cycle and daily lunar aspects',
                'market_applications': 'Short-term volatility prediction, sentiment analysis, entry/exit timing',
                'success_rate': 'Statistically significant correlation with volatility spikes',
                'modern_validation': 'Academic studies confirm lunar effect on financial markets'
            },
            {
                'principle_name': 'Mars Volatility Indicator',
                'description': 'Mars aspects, especially to outer planets, correlate with sudden market moves and volatility.',
                'originator': 'Financial astrology consensus',
                'mathematical_basis': 'Mars aspects to Jupiter, Saturn, Uranus, Neptune, Pluto',
                'market_applications': 'Volatility alerts, risk management, sudden reversal timing',
                'success_rate': 'High correlation with unexpected market events',
                'modern_validation': 'Mars represents sudden energy release, manifest as market shocks'
            }
        ]
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        for principle in principles:
            cursor.execute('''
                INSERT INTO financial_astrology_principles 
                (principle_name, description, originator, mathematical_basis, 
                 market_applications, success_rate, modern_validation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (principle['principle_name'], principle['description'], principle['originator'],
                  principle['mathematical_basis'], principle['market_applications'], 
                  principle['success_rate'], principle['modern_validation']))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(principles)} financial astrology principles")
    
    def load_planetary_knowledge(self):
        """Load comprehensive planetary knowledge"""
        
        planets = [
            {
                'planet': 'Sun',
                'traditional_meaning': 'Ego, vitality, leadership, authority, father, gold, creative force, life principle',
                'financial_meaning': 'Main trend direction, fundamental value, market confidence, leadership stocks, gold price',
                'cycle_period': 365.25,
                'keywords': 'leadership,authority,main_trend,confidence,gold,vitality,creative_force',
                'market_correlations': 'Solar aspects indicate major trend changes, solar returns mark annual cycles',
                'aspects_specialties': 'Conjunctions: new beginnings, Oppositions: culminations, Squares: challenges to authority'
            },
            {
                'planet': 'Moon',
                'traditional_meaning': 'Emotions, instincts, public, mother, silver, daily changes, subconscious, receptivity',
                'financial_meaning': 'Public sentiment, daily fluctuations, emotional trading, silver price, consumer sentiment',
                'cycle_period': 29.53,
                'keywords': 'emotions,sentiment,daily_changes,public,silver,instincts,fluctuations',
                'market_correlations': 'Lunar phases correlate with volatility, New Moon = new trends, Full Moon = emotional extremes',
                'aspects_specialties': 'Fast-moving aspects create daily trading opportunities and sentiment shifts'
            },
            {
                'planet': 'Mercury',
                'traditional_meaning': 'Communication, thinking, trade, commerce, information, technology, quick movement',
                'financial_meaning': 'Information flow, quick trades, technology stocks, communication sector, data releases',
                'cycle_period': 87.97,
                'keywords': 'communication,trade,information,technology,quick_movement,commerce',
                'market_correlations': 'Mercury retrograde correlates with miscommunications and technical glitches',
                'aspects_specialties': 'Aspects to Mercury indicate information releases and trading activity changes'
            },
            {
                'planet': 'Venus',
                'traditional_meaning': 'Love, beauty, harmony, values, money, luxury, cooperation, stability',
                'financial_meaning': 'Value assessment, luxury goods, cooperation, stable growth, aesthetic industries',
                'cycle_period': 224.7,
                'keywords': 'values,money,luxury,cooperation,stability,beauty,harmony',
                'market_correlations': 'Venus cycles correlate with value and luxury sectors, stable growth periods',
                'aspects_specialties': 'Venus aspects favor cooperation and stable, harmonious market conditions'
            },
            {
                'planet': 'Mars',
                'traditional_meaning': 'Action, aggression, energy, war, competition, initiative, impulse, heat',
                'financial_meaning': 'Volatility, sudden moves, aggressive trading, defense stocks, energy sector',
                'cycle_period': 686.98,
                'keywords': 'action,aggression,volatility,sudden_moves,energy,competition,initiative',
                'market_correlations': 'Mars aspects correlate with volatility spikes and sudden market movements',
                'aspects_specialties': 'Mars squares and oppositions create market tension and sudden reversals'
            },
            {
                'planet': 'Jupiter',
                'traditional_meaning': 'Expansion, growth, optimism, wisdom, abundance, good fortune, higher learning',
                'financial_meaning': 'Bull markets, expansion, optimism, growth stocks, abundance, economic expansion',
                'cycle_period': 4332.59,
                'keywords': 'expansion,growth,optimism,abundance,bull_markets,good_fortune',
                'market_correlations': 'Jupiter transits correlate with bull market phases and economic expansion',
                'aspects_specialties': 'Jupiter aspects bring optimism and expansion, especially beneficial aspects'
            },
            {
                'planet': 'Saturn',
                'traditional_meaning': 'Restriction, discipline, structure, responsibility, limitation, time, karma',
                'financial_meaning': 'Bear markets, corrections, discipline, structure, regulatory changes, restrictions',
                'cycle_period': 10759.22,
                'keywords': 'restriction,discipline,bear_markets,corrections,structure,responsibility',
                'market_correlations': 'Saturn transits correlate with bear markets, corrections, and regulatory pressure',
                'aspects_specialties': 'Saturn aspects bring tests, restrictions, and the need for disciplined approach'
            },
            {
                'planet': 'Uranus',
                'traditional_meaning': 'Revolution, sudden change, innovation, technology, freedom, rebellion, electricity',
                'financial_meaning': 'Sudden reversals, innovation, technology disruption, cryptocurrency, unexpected events',
                'cycle_period': 30688.5,
                'keywords': 'revolution,sudden_change,innovation,technology,disruption,unexpected',
                'market_correlations': 'Uranus aspects correlate with sudden market reversals and technological disruption',
                'aspects_specialties': 'Uranus aspects create unexpected events and revolutionary changes'
            },
            {
                'planet': 'Neptune',
                'traditional_meaning': 'Illusion, spirituality, dissolution, confusion, idealism, dreams, deception',
                'financial_meaning': 'Market bubbles, illusions, speculation, fraud, idealistic investments, confusion',
                'cycle_period': 60182,
                'keywords': 'illusion,bubbles,speculation,deception,confusion,idealism',
                'market_correlations': 'Neptune transits correlate with market bubbles and speculative manias',
                'aspects_specialties': 'Neptune aspects create illusions, bubbles, and unclear market conditions'
            },
            {
                'planet': 'Pluto',
                'traditional_meaning': 'Transformation, power, death/rebirth, plutocracy, underground, regeneration',
                'financial_meaning': 'Major transformations, power shifts, cryptocurrency, plutocracy, system changes',
                'cycle_period': 90560,
                'keywords': 'transformation,power,death_rebirth,plutocracy,regeneration,system_change',
                'market_correlations': 'Pluto transits correlate with major financial system transformations',
                'aspects_specialties': 'Pluto aspects bring profound transformation and power struggles'
            }
        ]
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        for planet in planets:
            cursor.execute('''
                INSERT INTO planetary_knowledge 
                (planet, traditional_meaning, financial_meaning, cycle_period, 
                 keywords, market_correlations, aspects_specialties)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (planet['planet'], planet['traditional_meaning'], planet['financial_meaning'],
                  planet['cycle_period'], planet['keywords'], planet['market_correlations'],
                  planet['aspects_specialties']))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(planets)} planetary knowledge entries")
    
    def load_aspect_interpretations(self):
        """Load comprehensive aspect interpretations"""
        
        # This is a sample - in full implementation would include all planet-aspect combinations
        key_aspects = [
            {
                'planet1': 'Jupiter',
                'planet2': 'Saturn',
                'aspect_type': 'conjunction',
                'traditional_meaning': 'Great Conjunction - new 20-year cycle beginning, balance of expansion and contraction',
                'financial_meaning': 'Major economic cycle change, new financial paradigm, structural economic shifts',
                'market_timing': 'Major long-term trend changes, generational investment themes',
                'orb_sensitivity': 3.0,
                'historical_examples': '2020 Great Conjunction coincided with COVID economic transformation'
            },
            {
                'planet1': 'Mars',
                'planet2': 'Uranus',
                'aspect_type': 'square',
                'traditional_meaning': 'Sudden aggressive action, revolutionary energy, explosive tension',
                'financial_meaning': 'Sudden market volatility, unexpected price moves, disruptive events',
                'market_timing': 'High volatility periods, sudden reversals, flash crashes',
                'orb_sensitivity': 2.0,
                'historical_examples': 'Mars-Uranus squares often coincide with market flash crashes'
            },
            {
                'planet1': 'Venus',
                'planet2': 'Jupiter',
                'aspect_type': 'trine',
                'traditional_meaning': 'Harmonious expansion of values, abundance, good fortune in financial matters',
                'financial_meaning': 'Favorable market conditions, growth in value sectors, positive sentiment',
                'market_timing': 'Stable growth periods, good entry points for long-term investments',
                'orb_sensitivity': 5.0,
                'historical_examples': 'Venus-Jupiter trines correlate with stable bull market periods'
            },
            {
                'planet1': 'Sun',
                'planet2': 'Pluto',
                'aspect_type': 'opposition',
                'traditional_meaning': 'Power struggles, transformation through opposition, intense confrontation',
                'financial_meaning': 'Major market tops/bottoms, power struggles in markets, fundamental changes',
                'market_timing': 'Major turning points, culmination of trends, transformation periods',
                'orb_sensitivity': 4.0,
                'historical_examples': 'Sun-Pluto oppositions often mark major market extremes'
            },
            {
                'planet1': 'Mercury',
                'planet2': 'Neptune',
                'aspect_type': 'square',
                'traditional_meaning': 'Confused communication, illusion, unclear information, deception',
                'financial_meaning': 'Market confusion, unclear data, potential for misinformation affecting prices',
                'market_timing': 'Periods of market uncertainty, unclear signals, potential for manipulation',
                'orb_sensitivity': 3.0,
                'historical_examples': 'Mercury-Neptune squares correlate with market confusion and false signals'
            }
        ]
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        for aspect in key_aspects:
            cursor.execute('''
                INSERT INTO aspect_interpretations 
                (planet1, planet2, aspect_type, traditional_meaning, financial_meaning, 
                 market_timing, orb_sensitivity, historical_examples)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (aspect['planet1'], aspect['planet2'], aspect['aspect_type'],
                  aspect['traditional_meaning'], aspect['financial_meaning'],
                  aspect['market_timing'], aspect['orb_sensitivity'],
                  aspect['historical_examples']))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(key_aspects)} aspect interpretations")
    
    def load_fixed_star_wisdom(self):
        """Load fixed star astrological knowledge"""
        
        stars = [
            {
                'star_name': 'Regulus',
                'constellation': 'Leo',
                'magnitude': 1.36,
                'astrological_nature': 'Mars/Jupiter - Royal star, leadership, nobility, success through courage',
                'financial_influence': 'Success in leadership positions, royal fortunes, noble investments, luxury markets',
                'historical_correlations': 'Regulus conjunctions often coincide with rise of market leaders',
                'modern_interpretations': 'Leadership in innovation, alpha investments, premium market positioning'
            },
            {
                'star_name': 'Aldebaran',
                'constellation': 'Taurus',
                'magnitude': 0.87,
                'astrological_nature': 'Mars/Jupiter - Watcher of the East, success through integrity, honor',
                'financial_influence': 'Steady wealth building, integrity in business, sustainable success',
                'historical_correlations': 'Aldebaran influence favors long-term wealth building strategies',
                'modern_interpretations': 'ESG investing, sustainable business models, integrity-based success'
            },
            {
                'star_name': 'Antares',
                'constellation': 'Scorpio',
                'magnitude': 1.06,
                'astrological_nature': 'Mars/Jupiter - Watcher of the West, obsession, transformation, war',
                'financial_influence': 'Intense market focus, transformative investments, power struggles',
                'historical_correlations': 'Antares conjunctions correlate with intense market competition',
                'modern_interpretations': 'Disruptive technologies, power struggles in markets, transformation'
            },
            {
                'star_name': 'Fomalhaut',
                'constellation': 'Piscis Austrinus',
                'magnitude': 1.17,
                'astrological_nature': 'Venus/Mercury - Watcher of the South, idealism, fame, immortality',
                'financial_influence': 'Idealistic investments, fame-based value, immortal brands',
                'historical_correlations': 'Fomalhaut influence on companies that achieve legendary status',
                'modern_interpretations': 'Brand value, idealistic ventures, visionary investments'
            },
            {
                'star_name': 'Spica',
                'constellation': 'Virgo',
                'magnitude': 0.98,
                'astrological_nature': 'Venus/Jupiter - The gift, talent, success, wealth through gifts',
                'financial_influence': 'Natural talents leading to wealth, gifts from others, beneficial investments',
                'historical_correlations': 'Spica conjunctions favor receiving financial gifts or windfalls',
                'modern_interpretations': 'Talent-based investments, gift economies, beneficial partnerships'
            }
        ]
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        for star in stars:
            cursor.execute('''
                INSERT INTO fixed_star_knowledge 
                (star_name, constellation, magnitude, astrological_nature, 
                 financial_influence, historical_correlations, modern_interpretations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (star['star_name'], star['constellation'], star['magnitude'],
                  star['astrological_nature'], star['financial_influence'],
                  star['historical_correlations'], star['modern_interpretations']))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(stars)} fixed star knowledge entries")
    
    def load_lunar_knowledge(self):
        """Load lunar phase and lunar astrology knowledge"""
        
        lunar_phases = [
            {
                'phase_type': 'New Moon',
                'traditional_meaning': 'New beginnings, planting seeds, darkness before dawn, potential energy',
                'market_tendencies': 'New trend beginnings, uncertainty, low volume, cautious sentiment',
                'volatility_patterns': 'Generally lower volatility, building energy, preparation phase',
                'trading_strategies': 'Accumulation phase, position building, avoid major decisions',
                'psychological_effects': 'Introspection, planning, uncertainty, new ideas emerging'
            },
            {
                'phase_type': 'Waxing Crescent',
                'traditional_meaning': 'Growth, taking action on new beginnings, momentum building',
                'market_tendencies': 'Trend confirmation, building momentum, growing optimism',
                'volatility_patterns': 'Moderate volatility, steady growth patterns',
                'trading_strategies': 'Follow emerging trends, gradual position building',
                'psychological_effects': 'Growing confidence, optimism, action-oriented'
            },
            {
                'phase_type': 'First Quarter',
                'traditional_meaning': 'Challenge, decision point, action required, overcoming obstacles',
                'market_tendencies': 'Market tests, decision points, breakout attempts',
                'volatility_patterns': 'Increased volatility, testing of support/resistance',
                'trading_strategies': 'Watch for breakouts, make key decisions, take action',
                'psychological_effects': 'Tension, need for decisions, overcoming challenges'
            },
            {
                'phase_type': 'Waxing Gibbous',
                'traditional_meaning': 'Refinement, adjustment, persistence, almost there',
                'market_tendencies': 'Trend continuation, fine-tuning, persistence required',
                'volatility_patterns': 'Moderate volatility, steady progress',
                'trading_strategies': 'Stay with trends, make adjustments, maintain patience',
                'psychological_effects': 'Patience, refinement, persistence, anticipation'
            },
            {
                'phase_type': 'Full Moon',
                'traditional_meaning': 'Culmination, completion, maximum energy, emotional peak',
                'market_tendencies': 'Trend culmination, emotional extremes, maximum activity',
                'volatility_patterns': 'Highest volatility, emotional trading, extremes',
                'trading_strategies': 'Watch for reversals, high emotion periods, take profits',
                'psychological_effects': 'Emotional intensity, maximum energy, completion'
            },
            {
                'phase_type': 'Waning Gibbous',
                'traditional_meaning': 'Gratitude, sharing, distributing, giving back',
                'market_tendencies': 'Distribution phase, sharing gains, profit taking',
                'volatility_patterns': 'Decreasing volatility, distribution patterns',
                'trading_strategies': 'Profit taking, distribution, prepare for next cycle',
                'psychological_effects': 'Gratitude, sharing, reflection on gains'
            },
            {
                'phase_type': 'Last Quarter',
                'traditional_meaning': 'Release, letting go, forgiveness, clearing',
                'market_tendencies': 'Correction phase, letting go of poor positions, clearing',
                'volatility_patterns': 'Moderate volatility, corrective movements',
                'trading_strategies': 'Cut losses, release poor positions, prepare for new cycle',
                'psychological_effects': 'Release, forgiveness, letting go, clearing'
            },
            {
                'phase_type': 'Waning Crescent',
                'traditional_meaning': 'Rest, reflection, preparation, wisdom gathering',
                'market_tendencies': 'Quiet period, reflection, preparation for next cycle',
                'volatility_patterns': 'Low volatility, quiet consolidation',
                'trading_strategies': 'Prepare for new cycle, reflect on lessons, plan ahead',
                'psychological_effects': 'Wisdom, reflection, rest, preparation'
            }
        ]
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        for phase in lunar_phases:
            cursor.execute('''
                INSERT INTO lunar_wisdom 
                (phase_type, traditional_meaning, market_tendencies, 
                 volatility_patterns, trading_strategies, psychological_effects)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (phase['phase_type'], phase['traditional_meaning'], phase['market_tendencies'],
                  phase['volatility_patterns'], phase['trading_strategies'], phase['psychological_effects']))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(lunar_phases)} lunar knowledge entries")
    
    def load_hermetic_principles(self):
        """Load Hermetic principles applicable to markets"""
        
        principles = [
            {
                'principle_name': 'The Principle of Mentalism',
                'hermetic_law': 'The All is Mind; the Universe is Mental',
                'astrological_application': 'Planetary influences work through consciousness and mental patterns',
                'market_manifestation': 'Market sentiment and collective psychology drive price movements',
                'practical_usage': 'Analyze collective mental states through astrological influences'
            },
            {
                'principle_name': 'The Principle of Correspondence',
                'hermetic_law': 'As above, so below; as below, so above',
                'astrological_application': 'Celestial patterns reflect in earthly patterns, including markets',
                'market_manifestation': 'Planetary cycles manifest as market cycles and price patterns',
                'practical_usage': 'Use planetary patterns to predict market patterns'
            },
            {
                'principle_name': 'The Principle of Vibration',
                'hermetic_law': 'Nothing rests; everything moves; everything vibrates',
                'astrological_application': 'Planets create vibrational frequencies that influence earthly affairs',
                'market_manifestation': 'Market cycles resonate with planetary vibrational frequencies',
                'practical_usage': 'Time market entries with harmonious planetary vibrations'
            },
            {
                'principle_name': 'The Principle of Polarity',
                'hermetic_law': 'Everything is dual; everything has poles; opposites are identical in nature',
                'astrological_application': 'Planetary aspects show polarity - conjunction/opposition, etc.',
                'market_manifestation': 'Bull/bear markets, fear/greed, buying/selling extremes',
                'practical_usage': 'Recognize when markets reach polar extremes for reversal timing'
            },
            {
                'principle_name': 'The Principle of Rhythm',
                'hermetic_law': 'Everything flows, out and in; everything has its tides',
                'astrological_application': 'Planetary cycles create natural rhythms and timing',
                'market_manifestation': 'Market cycles follow rhythmic patterns based on planetary periods',
                'practical_usage': 'Use planetary cycles to time market entry and exit points'
            },
            {
                'principle_name': 'The Principle of Cause and Effect',
                'hermetic_law': 'Every cause has its effect; every effect has its cause',
                'astrological_application': 'Planetary movements are causes; market movements are effects',
                'market_manifestation': 'Specific planetary configurations produce predictable market effects',
                'practical_usage': 'Identify planetary causes to predict market effects'
            },
            {
                'principle_name': 'The Principle of Gender',
                'hermetic_law': 'Gender is in everything; everything has masculine and feminine principles',
                'astrological_application': 'Planets have masculine (active) and feminine (receptive) qualities',
                'market_manifestation': 'Market phases alternate between active (bull) and receptive (bear)',
                'practical_usage': 'Recognize masculine (initiating) and feminine (receiving) market phases'
            }
        ]
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        for principle in principles:
            cursor.execute('''
                INSERT INTO hermetic_principles 
                (principle_name, hermetic_law, astrological_application, 
                 market_manifestation, practical_usage)
                VALUES (?, ?, ?, ?, ?)
            ''', (principle['principle_name'], principle['hermetic_law'], 
                  principle['astrological_application'], principle['market_manifestation'],
                  principle['practical_usage']))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(principles)} Hermetic principles")
    
    def get_planet_interpretation(self, planet: str) -> Dict:
        """Get comprehensive planet interpretation"""
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM planetary_knowledge WHERE planet = ?
        ''', (planet,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = ['id', 'planet', 'traditional_meaning', 'financial_meaning', 
                      'cycle_period', 'keywords', 'market_correlations', 'aspects_specialties']
            return dict(zip(columns, result))
        return {}
    
    def get_aspect_interpretation(self, planet1: str, planet2: str, aspect_type: str) -> Dict:
        """Get interpretation for specific aspect"""
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM aspect_interpretations 
            WHERE (planet1 = ? AND planet2 = ?) OR (planet1 = ? AND planet2 = ?)
            AND aspect_type = ?
        ''', (planet1, planet2, planet2, planet1, aspect_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = ['id', 'planet1', 'planet2', 'aspect_type', 'traditional_meaning', 
                      'financial_meaning', 'market_timing', 'orb_sensitivity', 'historical_examples']
            return dict(zip(columns, result))
        return {}
    
    def get_lunar_interpretation(self, phase_type: str) -> Dict:
        """Get lunar phase interpretation"""
        
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lunar_wisdom WHERE phase_type = ?
        ''', (phase_type,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = ['id', 'phase_type', 'traditional_meaning', 'market_tendencies',
                      'volatility_patterns', 'trading_strategies', 'psychological_effects']
            return dict(zip(columns, result))
        return {}
    
    def generate_ai_training_text(self) -> str:
        """Generate comprehensive training text for AI"""
        
        training_text = """
COMPREHENSIVE ASTROLOGICAL TRAINING FOR AI TRADING SYSTEM

You are being trained as an expert astrologer specializing in financial markets and crypto trading. 
This knowledge combines ancient wisdom with modern financial astrology research.

FUNDAMENTAL PRINCIPLES:

1. AS ABOVE, SO BELOW (Hermetic Principle)
   - Celestial patterns reflect in market patterns
   - Planetary cycles manifest as market cycles
   - What happens in the cosmos influences earthly affairs

2. PLANETARY INFLUENCES:
   - Each planet has specific energetic qualities
   - These qualities manifest in market behavior
   - Planetary aspects create market events and turning points

3. TIMING IS EVERYTHING:
   - Astrological timing provides edges in market entry/exit
   - Certain planetary configurations favor certain market conditions
   - Understanding cycles allows prediction of market phases

KEY PLANETARY MEANINGS FOR MARKETS:
"""
        
        # Add planetary knowledge
        conn = sqlite3.connect('data/astro_knowledge.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT planet, financial_meaning, keywords FROM planetary_knowledge')
        planets = cursor.fetchall()
        
        for planet, meaning, keywords in planets:
            training_text += f"\n{planet.upper()}: {meaning}\nKeywords: {keywords}\n"
        
        training_text += "\nASTROLOGICAL ASPECTS AND MARKET TIMING:\n"
        
        cursor.execute('SELECT planet1, planet2, aspect_type, financial_meaning FROM aspect_interpretations')
        aspects = cursor.fetchall()
        
        for p1, p2, aspect, meaning in aspects:
            training_text += f"{p1} {aspect} {p2}: {meaning}\n"
        
        training_text += "\nLUNAR PHASES AND MARKET PSYCHOLOGY:\n"
        
        cursor.execute('SELECT phase_type, market_tendencies, trading_strategies FROM lunar_wisdom')
        lunar = cursor.fetchall()
        
        for phase, tendencies, strategies in lunar:
            training_text += f"{phase}: {tendencies} | Strategy: {strategies}\n"
        
        training_text += "\nFINANCIAL ASTROLOGY PRINCIPLES:\n"
        
        cursor.execute('SELECT principle_name, description, market_applications FROM financial_astrology_principles')
        principles = cursor.fetchall()
        
        for name, desc, applications in principles:
            training_text += f"{name}: {desc}\nApplications: {applications}\n\n"
        
        conn.close()
        
        training_text += """
PRACTICAL APPLICATION GUIDELINES:

1. ALWAYS consider the overall astrological context
2. Look for multiple confirming factors
3. Stronger aspects (conjunctions, oppositions) have greater impact
4. Outer planet aspects have longer-lasting effects
5. Personal planet aspects affect daily/weekly movements
6. Fixed star conjunctions add additional significance
7. Lunar phases affect short-term sentiment and volatility

INTEGRATION WITH TECHNICAL ANALYSIS:
- Use astrology to TIME technical signals
- Astrological confirmation strengthens technical patterns
- When astrology and technicals align, confidence increases
- Use astrology to anticipate market mood changes

Remember: Astrology provides TIMING and CONTEXT, not absolute predictions.
Combine with other analysis methods for best results.
"""
        
        return training_text

# Global instance
astro_knowledge = AstroKnowledge()

if __name__ == "__main__":
    print("📚 Testing Astrological Knowledge Database...")
    
    # Test interpretations
    jupiter_interp = astro_knowledge.get_planet_interpretation('Jupiter')
    print(f"\nJupiter Financial Meaning: {jupiter_interp.get('financial_meaning', 'Not found')}")
    
    # Test training text generation
    training_text = astro_knowledge.generate_ai_training_text()
    print(f"\nTraining text generated: {len(training_text)} characters")
    
    print("✅ Astrological Knowledge test complete!")