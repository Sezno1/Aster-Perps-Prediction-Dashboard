"""
AI Prediction Tracker - Auto-learns from its own decisions
Tracks every prediction, monitors outcome, and learns continuously
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
import json

class AIPredictionTracker:
    def __init__(self, db_path: str = "ai_predictions.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize prediction tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                prediction_type TEXT NOT NULL,
                current_price FLOAT NOT NULL,
                entry_price FLOAT,
                exit_price FLOAT,
                stop_loss FLOAT,
                leverage INTEGER,
                confidence FLOAT,
                signal_strength FLOAT,
                orderflow_direction TEXT,
                orderflow_confidence FLOAT,
                whale_sentiment TEXT,
                whale_score FLOAT,
                funding_rate FLOAT,
                btc_price FLOAT,
                fear_greed_index INTEGER,
                recommendation TEXT,
                reasoning TEXT,
                key_factors TEXT,
                price_1h_later FLOAT,
                price_4h_later FLOAT,
                price_24h_later FLOAT,
                outcome TEXT,
                actual_move_1h FLOAT,
                actual_move_4h FLOAT,
                actual_move_24h FLOAT,
                was_correct BOOLEAN,
                profit_if_followed FLOAT,
                actual_profit_usd FLOAT,
                wallet_size_usd FLOAT,
                actual_entry_price FLOAT,
                actual_exit_price FLOAT,
                exit_reason TEXT,
                hold_time_hours FLOAT,
                last_checked DATETIME
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON predictions(timestamp)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                insight_type TEXT NOT NULL,
                insight_data TEXT NOT NULL,
                accuracy_score FLOAT,
                sample_size INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_prediction(self, prediction_data: Dict, market_data: Dict, 
                      signal_results: Dict, orderflow_analysis: Dict, 
                      whale_sentiment: Dict, ai_analysis: Dict, 
                      wallet_size: float = 10.0) -> int:
        """Log AI prediction for future evaluation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_price = market_data['prices']['aster']
        
        cursor.execute("""
            INSERT INTO predictions (
                timestamp, prediction_type, current_price,
                entry_price, exit_price, stop_loss, leverage,
                confidence, signal_strength,
                orderflow_direction, orderflow_confidence,
                whale_sentiment, whale_score,
                funding_rate, btc_price, fear_greed_index,
                recommendation, reasoning, key_factors,
                wallet_size_usd,
                last_checked
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            'SIGNAL',
            current_price,
            ai_analysis.get('entry_price'),
            ai_analysis.get('exit_price'),
            ai_analysis.get('stop_loss'),
            ai_analysis.get('leverage', 10),
            ai_analysis.get('confidence', 50),
            signal_results['composite_score'],
            orderflow_analysis['prediction']['direction'],
            orderflow_analysis['prediction']['confidence'],
            whale_sentiment.get('sentiment', 'NEUTRAL'),
            whale_sentiment.get('score', 50),
            market_data['perp_metrics'].get('aster_funding', 0),
            market_data['prices']['btc'],
            market_data['sentiment'].get('value') if market_data['sentiment'] else None,
            ai_analysis['recommendation'],
            ai_analysis['reasoning'],
            json.dumps(ai_analysis['key_factors']),
            wallet_size,
            datetime.now()
        ))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def update_prediction_outcomes(self, current_price: float):
        """Check and update outcomes for past predictions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute("""
            SELECT id, timestamp, current_price, entry_price, exit_price, 
                   recommendation, leverage, last_checked
            FROM predictions
            WHERE outcome IS NULL
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        
        predictions = cursor.fetchall()
        
        for pred in predictions:
            pred_id, pred_time, pred_price, entry_price, exit_price, recommendation, leverage, last_checked = pred
            
            time_elapsed = (now - datetime.fromisoformat(pred_time)).total_seconds() / 3600
            
            if time_elapsed >= 1:
                move_1h = ((current_price - pred_price) / pred_price) * 100
                cursor.execute("""
                    UPDATE predictions 
                    SET price_1h_later = ?, actual_move_1h = ?, last_checked = ?
                    WHERE id = ?
                """, (current_price, move_1h, now, pred_id))
            
            if time_elapsed >= 4:
                move_4h = ((current_price - pred_price) / pred_price) * 100
                cursor.execute("""
                    UPDATE predictions 
                    SET price_4h_later = ?, actual_move_4h = ?, last_checked = ?
                    WHERE id = ?
                """, (current_price, move_4h, now, pred_id))
            
            if time_elapsed >= 24:
                move_24h = ((current_price - pred_price) / pred_price) * 100
                
                was_correct = False
                profit_if_followed = 0
                outcome = "PENDING"
                
                if recommendation in ["BUY_NOW", "STRONG_BUY"] and entry_price:
                    if current_price > entry_price:
                        price_change_pct = ((current_price - entry_price) / entry_price)
                        profit_if_followed = price_change_pct * 100 * leverage
                        was_correct = profit_if_followed > 0
                        outcome = "WIN" if was_correct else "LOSS"
                    else:
                        outcome = "NO_MOVE"
                elif recommendation == "WAIT":
                    if abs(move_24h) < 2:
                        was_correct = True
                        outcome = "CORRECT_WAIT"
                    else:
                        was_correct = False
                        outcome = "MISSED_OPPORTUNITY" if move_24h > 5 else "CORRECT_WAIT"
                
                cursor.execute("""
                    UPDATE predictions 
                    SET price_24h_later = ?, actual_move_24h = ?,
                        outcome = ?, was_correct = ?, profit_if_followed = ?,
                        last_checked = ?
                    WHERE id = ?
                """, (current_price, move_24h, outcome, was_correct, profit_if_followed, now, pred_id))
        
        conn.commit()
        conn.close()
    
    def get_learning_insights(self) -> Dict:
        """Analyze past predictions to generate learning insights"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                COUNT(*) as total_predictions,
                SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct_predictions,
                AVG(CASE WHEN was_correct = 1 THEN confidence ELSE NULL END) as avg_confidence_correct,
                AVG(CASE WHEN was_correct = 0 THEN confidence ELSE NULL END) as avg_confidence_wrong,
                AVG(profit_if_followed) as avg_profit_if_followed,
                AVG(signal_strength) as avg_signal_strength,
                orderflow_direction,
                whale_sentiment,
                COUNT(*) as count
            FROM predictions
            WHERE outcome IS NOT NULL AND outcome != 'PENDING'
            GROUP BY orderflow_direction, whale_sentiment
        """
        
        df = pd.read_sql_query(query, conn)
        
        overall_query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct,
                AVG(profit_if_followed) as avg_profit
            FROM predictions
            WHERE outcome IS NOT NULL AND outcome != 'PENDING'
        """
        
        overall_df = pd.read_sql_query(overall_query, conn)
        
        best_conditions_query = """
            SELECT 
                signal_strength,
                orderflow_direction,
                whale_sentiment,
                AVG(profit_if_followed) as avg_profit,
                COUNT(*) as sample_size,
                SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as wins
            FROM predictions
            WHERE outcome IS NOT NULL AND recommendation = 'BUY_NOW'
            GROUP BY 
                ROUND(signal_strength / 10) * 10,
                orderflow_direction,
                whale_sentiment
            HAVING sample_size >= 3
            ORDER BY avg_profit DESC
            LIMIT 5
        """
        
        best_df = pd.read_sql_query(best_conditions_query, conn)
        
        conn.close()
        
        if overall_df.empty or overall_df.iloc[0]['total'] == 0:
            return {
                'has_data': False,
                'message': 'Not enough prediction history yet'
            }
        
        total = int(overall_df.iloc[0]['total'])
        correct = int(overall_df.iloc[0]['correct']) if overall_df.iloc[0]['correct'] else 0
        accuracy = (correct / total * 100) if total > 0 else 0
        avg_profit = float(overall_df.iloc[0]['avg_profit']) if overall_df.iloc[0]['avg_profit'] else 0
        
        insights = {
            'has_data': True,
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy': accuracy,
            'avg_profit_if_followed': avg_profit,
            'best_conditions': best_df.to_dict('records') if not best_df.empty else [],
            'by_orderflow': df.to_dict('records') if not df.empty else []
        }
        
        return insights
    
    def generate_ai_learning_context(self) -> str:
        """Generate learning context for AI prompt"""
        insights = self.get_learning_insights()
        
        if not insights['has_data']:
            return ""
        
        accuracy = insights['accuracy']
        total = insights['total_predictions']
        avg_profit = insights['avg_profit_if_followed']
        
        context = f"""
SELF-LEARNING FROM PAST PREDICTIONS:
I have made {total} predictions in the past. Here's my performance:
- Accuracy: {accuracy:.1f}%
- Average Profit if Followed: {avg_profit:.2f}%

"""
        
        if insights['best_conditions']:
            context += "PATTERNS I'VE DISCOVERED THAT WORK:\n"
            for condition in insights['best_conditions'][:3]:
                context += f"- Signal {condition['signal_strength']:.0f}, {condition['orderflow_direction']}, {condition['whale_sentiment']}: "
                context += f"{condition['avg_profit']:.1f}% profit ({condition['wins']}/{condition['sample_size']} wins)\n"
        
        if accuracy < 60:
            context += f"""
⚠️ SELF-CORRECTION: Accuracy is {accuracy:.1f}% (below target). BEING MORE CONSERVATIVE:
- ONLY recommend BUY when signal strength > 70
- ONLY use strategies with >70% confidence
- REDUCE leverage by 20-30%
- REQUIRE stronger orderflow confirmation (imbalance > 20)
- AVOID trading during low-volume periods
- TIGHTER stop losses to minimize losses
"""
        elif accuracy < 70:
            context += f"""
📊 PERFORMANCE: {accuracy:.1f}% accuracy. ADJUSTMENTS:
- Maintain current signal thresholds
- Continue monitoring for patterns
- Fine-tune stop losses based on volatility
"""
        elif accuracy >= 70:
            context += f"""
✅ EXCELLENT PERFORMANCE: {accuracy:.1f}% accuracy! Current approach is working:
- Continue using proven patterns
- Can slightly increase position confidence
- Keep stop losses protective
"""
        
        return context
    
    def log_actual_trade_result(self, prediction_id: int, entry_price: float, 
                                exit_price: float, exit_reason: str, 
                                hold_time_hours: float, wallet_size: float, 
                                leverage: int):
        """Log the actual result of a trade that was executed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate actual profit
        price_change_pct = ((exit_price - entry_price) / entry_price)
        position_size = wallet_size * leverage
        actual_profit_usd = position_size * price_change_pct
        
        outcome = "WIN" if actual_profit_usd > 0 else "LOSS"
        was_correct = actual_profit_usd > 0
        
        cursor.execute("""
            UPDATE predictions 
            SET actual_entry_price = ?,
                actual_exit_price = ?,
                exit_reason = ?,
                hold_time_hours = ?,
                actual_profit_usd = ?,
                outcome = ?,
                was_correct = ?,
                last_checked = ?
            WHERE id = ?
        """, (entry_price, exit_price, exit_reason, hold_time_hours, 
              actual_profit_usd, outcome, was_correct, datetime.now(), prediction_id))
        
        conn.commit()
        conn.close()
        return actual_profit_usd
    
    def get_recent_predictions(self, limit: int = 10) -> pd.DataFrame:
        """Get recent predictions with outcomes"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT timestamp, recommendation, current_price, 
                   confidence, signal_strength,
                   actual_move_24h, outcome, was_correct,
                   profit_if_followed, actual_profit_usd,
                   actual_entry_price, actual_exit_price, exit_reason
            FROM predictions
            ORDER BY timestamp DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df