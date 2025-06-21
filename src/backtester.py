"""
Core backtesting engine for strategy simulation.

This module provides the main backtesting functionality including
trade execution, position management, and performance tracking.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.trade import Trade, TradeDirection, TradeStatus
from src.performance import PerformanceMetrics
from src.strategy import StrategyEngine
from src.indicators import TechnicalIndicators


class BacktestEngine:
    """
    Core backtesting engine for strategy simulation.
    
    This class simulates trading strategies on historical data,
    managing positions, executing trades, and tracking performance.
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize the backtesting engine.
        
        Args:
            initial_capital: Starting capital for the backtest
        """
        self.initial_capital = initial_capital
        self.trades: List[Trade] = []
        self.current_position: Optional[TradeDirection] = None
        self.current_trade: Optional[Trade] = None
        self.logger = logging.getLogger(__name__)
        
    def reset(self):
        """Reset the backtesting engine for a new run."""
        self.trades = []
        self.current_position = None
        self.current_trade = None
        
    def execute_strategy(self, data: pd.DataFrame, strategy_config: Dict[str, Any],
                        use_improved_strategy: bool = False) -> Dict[str, Any]:
        """
        Execute a trading strategy on historical data.
        
        Args:
            data: Historical price data with OHLCV columns
            strategy_config: Strategy configuration parameters
            use_improved_strategy: Whether to use improved multi-filter strategy
            
        Returns:
            Dictionary containing backtest results and performance metrics
        """
        self.reset()
        
        # Initialize strategy engine
        strategy_engine = StrategyEngine()
        
        # Generate signals based on strategy type
        if use_improved_strategy:
            signals = strategy_engine.generate_improved_signals(data, strategy_config)
        else:
            signals = strategy_engine.generate_baseline_signals(data, strategy_config)
        
        # Add signals to data
        data_with_signals = data.copy()
        # Extract signal column if signals is a DataFrame, otherwise use as-is
        if hasattr(signals, 'signal'):
            data_with_signals['signal'] = signals['signal']
        else:
            data_with_signals['signal'] = signals
        
        # Execute trades based on signals
        self._execute_trades(data_with_signals)
        
        # Calculate performance metrics
        performance = PerformanceMetrics(self.trades, self.initial_capital)
        
        return {
            'trades': self.trades,
            'performance_metrics': performance.get_summary_stats(),
            'equity_curve': performance.generate_equity_curve(),
            'total_signals': self._count_signals(data_with_signals['signal']),
            'strategy_type': 'improved' if use_improved_strategy else 'baseline'
        }
    
    def _count_signals(self, signals):
        """
        Count non-hold signals, handling both string and numeric formats.
        
        Args:
            signals: Series or list of signals
            
        Returns:
            int: Number of non-hold signals
        """
        if hasattr(signals, 'values'):
            # Handle pandas Series
            signal_values = signals.values
        else:
            # Handle list or array
            signal_values = signals
        
        count = 0
        for signal in signal_values:
            # Handle both string format ('BUY', 'SELL' vs 'HOLD') and numeric format (1, -1 vs 0)
            if isinstance(signal, str):
                if signal != 'HOLD':
                    count += 1
            else:
                if signal != 0:
                    count += 1
        
        return count
    
    def _execute_trades(self, data: pd.DataFrame):
        """
        Execute trades based on signal column in data.
        
        Args:
            data: DataFrame with signal column containing BUY/SELL/HOLD signals
        """
        for idx, row in data.iterrows():
            signal = row['signal']
            current_price = row['Close']
            current_datetime = row.name if hasattr(row.name, 'to_pydatetime') else row.name
            
            # Convert pandas timestamp to datetime if needed
            if hasattr(current_datetime, 'to_pydatetime'):
                current_datetime = current_datetime.to_pydatetime()
            
            # Skip if no signal or holding
            if signal == 'HOLD':
                continue
                
            # Process signal
            self._process_signal(signal, current_price, current_datetime, idx)
    
    def _process_signal(self, signal: str, price: float, datetime_obj: datetime, index: int):
        """
        Process a trading signal and execute appropriate trades.
        
        Args:
            signal: Trading signal ('BUY' or 'SELL')
            price: Current price
            datetime_obj: Current datetime
            index: Current data index
        """
        if signal == 'BUY':
            # If we have a short position, close it first
            if self.current_position == TradeDirection.SHORT:
                self._close_current_trade(price, datetime_obj, index)
            
            # Open new long position
            if self.current_position != TradeDirection.LONG:
                self._open_trade(TradeDirection.LONG, price, datetime_obj, index)
                
        elif signal == 'SELL':
            # If we have a long position, close it first
            if self.current_position == TradeDirection.LONG:
                self._close_current_trade(price, datetime_obj, index)
            
            # Open new short position
            if self.current_position != TradeDirection.SHORT:
                self._open_trade(TradeDirection.SHORT, price, datetime_obj, index)
    
    def _open_trade(self, direction: TradeDirection, price: float, 
                   datetime_obj: datetime, index: int):
        """
        Open a new trade.
        
        Args:
            direction: Trade direction (LONG or SHORT)
            price: Entry price
            datetime_obj: Entry datetime
            index: Entry data index
        """
        self.current_trade = Trade(direction, price, datetime_obj, index)
        self.current_position = direction
        
        self.logger.debug(f"Opened {direction.value} trade at {price} on {datetime_obj}")
    
    def _close_current_trade(self, price: float, datetime_obj: datetime, index: int):
        """
        Close the current open trade.
        
        Args:
            price: Exit price
            datetime_obj: Exit datetime
            index: Exit data index
        """
        if self.current_trade is None:
            return
            
        self.current_trade.close_trade(price, datetime_obj, index)
        self.trades.append(self.current_trade)
        
        self.logger.debug(f"Closed {self.current_trade.direction.value} trade: "
                         f"{self.current_trade.entry_price} -> {price} "
                         f"({self.current_trade.pnl_pct:.2f}%)")
        
        self.current_trade = None
        self.current_position = None
    
    def close_final_trade(self, data: pd.DataFrame):
        """
        Close any remaining open trade at the end of the backtest.
        
        Args:
            data: Historical data to get final close price
        """
        if self.current_trade is not None and len(data) > 0:
            final_row = data.iloc[-1]
            final_price = final_row['Close']
            final_datetime = final_row.name
            final_index = len(data) - 1
            
            # Convert pandas timestamp to datetime if needed
            if hasattr(final_datetime, 'to_pydatetime'):
                final_datetime = final_datetime.to_pydatetime()
            
            self._close_current_trade(final_price, final_datetime, final_index)
    
    def get_trade_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all executed trades.
        
        Returns:
            Dictionary with trade summary information
        """
        closed_trades = [trade for trade in self.trades if trade.status == TradeStatus.CLOSED]
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'long_trades': 0,
                'short_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0
            }
        
        long_trades = sum(1 for trade in closed_trades if trade.direction == TradeDirection.LONG)
        short_trades = sum(1 for trade in closed_trades if trade.direction == TradeDirection.SHORT)
        winning_trades = sum(1 for trade in closed_trades if trade.is_winner)
        losing_trades = len(closed_trades) - winning_trades
        
        return {
            'total_trades': len(closed_trades),
            'long_trades': long_trades,
            'short_trades': short_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades
        }
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data for backtesting.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Check if all required columns exist
        if not all(col in data.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in data.columns]
            self.logger.error(f"Missing required columns: {missing_cols}")
            return False
        
        # Check for empty data
        if len(data) == 0:
            self.logger.error("Data is empty")
            return False
        
        # Check for NaN values in critical columns
        critical_columns = ['Close']
        for col in critical_columns:
            if data[col].isna().any():
                self.logger.error(f"NaN values found in {col} column")
                return False
        
        return True