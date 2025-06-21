"""
Performance metrics calculation module for backtesting.

This module provides comprehensive performance analysis including
win rate, equity curve, maximum drawdown, and other key metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from src.trade import Trade, TradeStatus


class PerformanceMetrics:
    """
    Calculates comprehensive performance metrics from trade history.
    
    This class analyzes completed trades to provide key performance
    indicators for strategy evaluation.
    """
    
    def __init__(self, trades: List[Trade], initial_capital: float = 100000.0):
        """
        Initialize performance metrics calculator.
        
        Args:
            trades: List of completed trades
            initial_capital: Starting capital for equity curve calculation
        """
        self.trades = trades
        self.initial_capital = initial_capital
        self.closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED]
        
    def calculate_win_rate(self) -> float:
        """
        Calculate win rate as percentage of profitable trades.
        
        Returns:
            Win rate as percentage (0-100)
        """
        if not self.closed_trades:
            return 0.0
        
        winning_trades = sum(1 for trade in self.closed_trades if trade.is_winner)
        return (winning_trades / len(self.closed_trades)) * 100
    
    def calculate_total_return(self) -> float:
        """
        Calculate total return percentage from all trades.
        
        Returns:
            Total return as percentage
        """
        if not self.closed_trades:
            return 0.0
        
        total_pnl_pct = sum(trade.pnl_pct for trade in self.closed_trades)
        return total_pnl_pct
    
    def calculate_average_return_per_trade(self) -> float:
        """
        Calculate average return per trade.
        
        Returns:
            Average return per trade as percentage
        """
        if not self.closed_trades:
            return 0.0
        
        return self.calculate_total_return() / len(self.closed_trades)
    
    def calculate_best_trade(self) -> float:
        """
        Find the best (most profitable) single trade.
        
        Returns:
            Best trade P&L percentage
        """
        if not self.closed_trades:
            return 0.0
        
        return max(trade.pnl_pct for trade in self.closed_trades)
    
    def calculate_worst_trade(self) -> float:
        """
        Find the worst (most losing) single trade.
        
        Returns:
            Worst trade P&L percentage
        """
        if not self.closed_trades:
            return 0.0
        
        return min(trade.pnl_pct for trade in self.closed_trades)
    
    def generate_equity_curve(self) -> pd.DataFrame:
        """
        Generate equity curve from trade history.
        
        Returns:
            DataFrame with datetime index and equity values
        """
        if not self.closed_trades:
            return pd.DataFrame(columns=['datetime', 'equity'])
        
        # Sort trades by exit datetime
        sorted_trades = sorted(self.closed_trades, key=lambda t: t.exit_datetime)
        
        equity_data = []
        current_equity = self.initial_capital
        
        # Add initial equity point
        equity_data.append({
            'datetime': sorted_trades[0].entry_datetime,
            'equity': current_equity
        })
        
        # Calculate equity after each trade
        for trade in sorted_trades:
            # Convert percentage P&L to dollar amount
            dollar_pnl = (trade.pnl_pct / 100) * current_equity
            current_equity += dollar_pnl
            
            equity_data.append({
                'datetime': trade.exit_datetime,
                'equity': current_equity
            })
        
        return pd.DataFrame(equity_data).set_index('datetime')
    
    def calculate_maximum_drawdown(self) -> Dict[str, float]:
        """
        Calculate maximum drawdown from equity curve.
        
        Returns:
            Dictionary with max_drawdown_pct and max_drawdown_duration
        """
        equity_curve = self.generate_equity_curve()
        
        if equity_curve.empty:
            return {'max_drawdown_pct': 0.0, 'max_drawdown_duration': 0}
        
        # Calculate running maximum (peak)
        equity_curve['peak'] = equity_curve['equity'].expanding().max()
        
        # Calculate drawdown percentage
        equity_curve['drawdown_pct'] = ((equity_curve['equity'] - equity_curve['peak']) / 
                                       equity_curve['peak']) * 100
        
        # Find maximum drawdown
        max_drawdown_pct = equity_curve['drawdown_pct'].min()
        
        # Calculate drawdown duration (simplified - number of trades in drawdown)
        max_drawdown_duration = 0
        current_duration = 0
        
        for drawdown in equity_curve['drawdown_pct']:
            if drawdown < 0:
                current_duration += 1
                max_drawdown_duration = max(max_drawdown_duration, current_duration)
            else:
                current_duration = 0
        
        return {
            'max_drawdown_pct': abs(max_drawdown_pct),
            'max_drawdown_duration': max_drawdown_duration
        }
    
    def calculate_profit_factor(self) -> float:
        """
        Calculate profit factor (gross profit / gross loss).
        
        Returns:
            Profit factor ratio
        """
        if not self.closed_trades:
            return 0.0
        
        gross_profit = sum(trade.pnl_pct for trade in self.closed_trades if trade.is_winner)
        gross_loss = abs(sum(trade.pnl_pct for trade in self.closed_trades if not trade.is_winner))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics.
        
        Returns:
            Dictionary containing all key performance metrics
        """
        drawdown_info = self.calculate_maximum_drawdown()
        
        return {
            'total_trades': len(self.closed_trades),
            'win_rate_pct': self.calculate_win_rate(),
            'total_return_pct': self.calculate_total_return(),
            'avg_return_per_trade_pct': self.calculate_average_return_per_trade(),
            'best_trade_pct': self.calculate_best_trade(),
            'worst_trade_pct': self.calculate_worst_trade(),
            'profit_factor': self.calculate_profit_factor(),
            'max_drawdown_pct': drawdown_info['max_drawdown_pct'],
            'max_drawdown_duration': drawdown_info['max_drawdown_duration']
        }