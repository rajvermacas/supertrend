"""
Trade management module for backtesting engine.

This module provides classes and functions for managing individual trades
and tracking position states during backtesting.
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class TradeDirection(Enum):
    """Enumeration for trade directions."""
    LONG = "LONG"
    SHORT = "SHORT"


class TradeStatus(Enum):
    """Enumeration for trade status."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Trade:
    """
    Represents a single trade with entry and exit information.
    
    This class tracks all relevant information for a trade including
    entry/exit prices, timestamps, direction, and P&L calculation.
    """
    
    def __init__(self, direction: TradeDirection, entry_price: float, 
                 entry_datetime: datetime, entry_index: int):
        """
        Initialize a new trade.
        
        Args:
            direction: Trade direction (LONG or SHORT)
            entry_price: Price at trade entry
            entry_datetime: Timestamp of trade entry
            entry_index: DataFrame index of entry
        """
        self.direction = direction
        self.entry_price = entry_price
        self.entry_datetime = entry_datetime
        self.entry_index = entry_index
        self.exit_price: Optional[float] = None
        self.exit_datetime: Optional[datetime] = None
        self.exit_index: Optional[int] = None
        self.status = TradeStatus.OPEN
        self.pnl_pct: Optional[float] = None
        self.is_winner: Optional[bool] = None
    
    def close_trade(self, exit_price: float, exit_datetime: datetime, exit_index: int):
        """
        Close the trade and calculate P&L.
        
        Args:
            exit_price: Price at trade exit
            exit_datetime: Timestamp of trade exit
            exit_index: DataFrame index of exit
        """
        self.exit_price = exit_price
        self.exit_datetime = exit_datetime
        self.exit_index = exit_index
        self.status = TradeStatus.CLOSED
        
        # Calculate P&L percentage
        if self.direction == TradeDirection.LONG:
            self.pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            self.pnl_pct = ((self.entry_price - exit_price) / self.entry_price) * 100
        
        self.is_winner = self.pnl_pct > 0
    
    def to_dict(self) -> dict:
        """
        Convert trade to dictionary format for logging.
        
        Returns:
            Dictionary representation of the trade
        """
        return {
            'direction': self.direction.value,
            'entry_price': self.entry_price,
            'entry_datetime': self.entry_datetime,
            'entry_index': self.entry_index,
            'exit_price': self.exit_price,
            'exit_datetime': self.exit_datetime,
            'exit_index': self.exit_index,
            'status': self.status.value,
            'pnl_pct': self.pnl_pct,
            'is_winner': self.is_winner
        }
    
    def __str__(self) -> str:
        """String representation of the trade."""
        if self.status == TradeStatus.OPEN:
            return f"{self.direction.value} trade opened at {self.entry_price} on {self.entry_datetime}"
        else:
            return (f"{self.direction.value} trade: {self.entry_price} -> {self.exit_price} "
                   f"({self.pnl_pct:.2f}%) on {self.entry_datetime} -> {self.exit_datetime}")