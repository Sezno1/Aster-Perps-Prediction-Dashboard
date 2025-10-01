"""
Backtesting Engine
Tests patterns and strategies against historical data
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

class BacktestEngine:
    
    def __init__(self, initial_capital=1000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades = []
        self.equity_curve = []
    
    def load_data(self, symbol, timeframe, days=90):
        """Load historical data for backtesting"""
        try:
            conn = sqlite3.connect('data/market_data.db')
            
            query = '''
                SELECT timestamp, open, high, low, close, volume 
                FROM ohlcv 
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, timeframe))
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def backtest_pattern(self, df, entry_condition, exit_condition, stop_loss_pct=2, leverage=10):
        """
        Backtest a pattern with entry/exit conditions
        entry_condition: function that returns True when pattern detected
        exit_condition: function that returns True when exit signal
        """
        
        if df.empty:
            return None
        
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = []
        
        position = None
        
        for i in range(50, len(df)):
            current_bar = df.iloc[:i+1]
            current_price = current_bar['close'].iloc[-1]
            
            self.equity_curve.append({
                'timestamp': current_bar.index[-1],
                'equity': self.capital
            })
            
            if position is None:
                if entry_condition(current_bar):
                    entry_price = current_price
                    position_size = self.capital * leverage
                    
                    position = {
                        'entry_time': current_bar.index[-1],
                        'entry_price': entry_price,
                        'position_size': position_size,
                        'stop_loss': entry_price * (1 - stop_loss_pct / 100),
                        'leverage': leverage
                    }
            
            else:
                stop_hit = current_price <= position['stop_loss']
                exit_signal = exit_condition(current_bar)
                
                if stop_hit or exit_signal:
                    exit_price = current_price
                    
                    price_change_pct = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                    profit_pct = price_change_pct * position['leverage']
                    profit_amount = self.capital * (profit_pct / 100)
                    
                    self.capital += profit_amount
                    
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': current_bar.index[-1],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'profit_pct': profit_pct,
                        'profit_amount': profit_amount,
                        'outcome': 'WIN' if profit_amount > 0 else 'LOSS',
                        'exit_reason': 'STOP_LOSS' if stop_hit else 'EXIT_SIGNAL'
                    }
                    
                    self.trades.append(trade)
                    position = None
        
        return self.calculate_stats()
    
    def calculate_stats(self):
        """Calculate backtest statistics"""
        
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_return': 0,
                'sharpe_ratio': 0
            }
        
        wins = [t for t in self.trades if t['outcome'] == 'WIN']
        losses = [t for t in self.trades if t['outcome'] == 'LOSS']
        
        win_rate = len(wins) / len(self.trades) * 100
        
        total_profit = sum(t['profit_amount'] for t in wins)
        total_loss = abs(sum(t['profit_amount'] for t in losses))
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 999
        
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        returns = [t['profit_pct'] for t in self.trades]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if len(returns) > 1 else 0
        
        avg_win = np.mean([t['profit_pct'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['profit_pct'] for t in losses]) if losses else 0
        
        max_drawdown = self.calculate_max_drawdown()
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_capital': self.capital,
            'trades': self.trades
        }
    
    def calculate_max_drawdown(self):
        """Calculate maximum drawdown"""
        if not self.equity_curve:
            return 0
        
        equity_values = [e['equity'] for e in self.equity_curve]
        peak = equity_values[0]
        max_dd = 0
        
        for value in equity_values:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def print_backtest_results(self, stats):
        """Print formatted backtest results"""
        
        print("\n" + "="*70)
        print("📊 BACKTEST RESULTS")
        print("="*70)
        
        print(f"\nTotal Trades: {stats['total_trades']}")
        print(f"Wins: {stats['winning_trades']} | Losses: {stats['losing_trades']}")
        print(f"Win Rate: {stats['win_rate']:.1f}%")
        print(f"Profit Factor: {stats['profit_factor']:.2f}")
        print(f"\nTotal Return: {stats['total_return']:.2f}%")
        print(f"Final Capital: ${stats['final_capital']:.2f}")
        print(f"\nAvg Win: {stats['avg_win']:.2f}%")
        print(f"Avg Loss: {stats['avg_loss']:.2f}%")
        print(f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {stats['max_drawdown']:.2f}%")
        
        print("\n" + "="*70)

if __name__ == '__main__':
    print("✅ Backtest Engine Ready")