"""
Test suite for trade management module.

Tests the Trade class functionality including trade creation,
closing, P&L calculation, and data conversion.
"""

import pytest
from datetime import datetime
from src.trade import Trade, TradeDirection, TradeStatus


class TestTrade:
    """Test cases for Trade class."""
    
    def test_trade_creation_long(self):
        """Test creating a LONG trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        trade = Trade(
            direction=TradeDirection.LONG,
            entry_price=100.0,
            entry_datetime=entry_datetime,
            entry_index=0
        )
        
        assert trade.direction == TradeDirection.LONG
        assert trade.entry_price == 100.0
        assert trade.entry_datetime == entry_datetime
        assert trade.entry_index == 0
        assert trade.status == TradeStatus.OPEN
        assert trade.exit_price is None
        assert trade.exit_datetime is None
        assert trade.exit_index is None
        assert trade.pnl_pct is None
        assert trade.is_winner is None
    
    def test_trade_creation_short(self):
        """Test creating a SHORT trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        trade = Trade(
            direction=TradeDirection.SHORT,
            entry_price=100.0,
            entry_datetime=entry_datetime,
            entry_index=0
        )
        
        assert trade.direction == TradeDirection.SHORT
        assert trade.entry_price == 100.0
        assert trade.status == TradeStatus.OPEN
    
    def test_close_long_trade_profitable(self):
        """Test closing a profitable LONG trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        trade.close_trade(110.0, exit_datetime, 1)
        
        assert trade.status == TradeStatus.CLOSED
        assert trade.exit_price == 110.0
        assert trade.exit_datetime == exit_datetime
        assert trade.exit_index == 1
        assert trade.pnl_pct == 10.0  # (110-100)/100 * 100
        assert trade.is_winner is True
    
    def test_close_long_trade_losing(self):
        """Test closing a losing LONG trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        trade.close_trade(90.0, exit_datetime, 1)
        
        assert trade.status == TradeStatus.CLOSED
        assert trade.exit_price == 90.0
        assert trade.pnl_pct == -10.0  # (90-100)/100 * 100
        assert trade.is_winner is False
    
    def test_close_short_trade_profitable(self):
        """Test closing a profitable SHORT trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        trade = Trade(TradeDirection.SHORT, 100.0, entry_datetime, 0)
        trade.close_trade(90.0, exit_datetime, 1)
        
        assert trade.status == TradeStatus.CLOSED
        assert trade.exit_price == 90.0
        assert trade.pnl_pct == 10.0  # (100-90)/100 * 100
        assert trade.is_winner is True
    
    def test_close_short_trade_losing(self):
        """Test closing a losing SHORT trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        trade = Trade(TradeDirection.SHORT, 100.0, entry_datetime, 0)
        trade.close_trade(110.0, exit_datetime, 1)
        
        assert trade.status == TradeStatus.CLOSED
        assert trade.exit_price == 110.0
        assert trade.pnl_pct == -10.0  # (100-110)/100 * 100
        assert trade.is_winner is False
    
    def test_to_dict_open_trade(self):
        """Test converting open trade to dictionary."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        
        trade_dict = trade.to_dict()
        
        expected = {
            'direction': 'LONG',
            'entry_price': 100.0,
            'entry_datetime': entry_datetime,
            'entry_index': 0,
            'exit_price': None,
            'exit_datetime': None,
            'exit_index': None,
            'status': 'OPEN',
            'pnl_pct': None,
            'is_winner': None
        }
        
        assert trade_dict == expected
    
    def test_to_dict_closed_trade(self):
        """Test converting closed trade to dictionary."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        trade.close_trade(110.0, exit_datetime, 1)
        
        trade_dict = trade.to_dict()
        
        expected = {
            'direction': 'LONG',
            'entry_price': 100.0,
            'entry_datetime': entry_datetime,
            'entry_index': 0,
            'exit_price': 110.0,
            'exit_datetime': exit_datetime,
            'exit_index': 1,
            'status': 'CLOSED',
            'pnl_pct': 10.0,
            'is_winner': True
        }
        
        assert trade_dict == expected
    
    def test_str_representation_open(self):
        """Test string representation of open trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        
        expected = "LONG trade opened at 100.0 on 2023-01-01 10:00:00"
        assert str(trade) == expected
    
    def test_str_representation_closed(self):
        """Test string representation of closed trade."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        trade.close_trade(110.0, exit_datetime, 1)
        
        expected = ("LONG trade: 100.0 -> 110.0 (10.00%) on "
                   "2023-01-01 10:00:00 -> 2023-01-01 11:00:00")
        assert str(trade) == expected
    
    def test_pnl_calculation_edge_cases(self):
        """Test P&L calculation edge cases."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        # Test zero P&L
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        trade.close_trade(100.0, exit_datetime, 1)
        assert trade.pnl_pct == 0.0
        assert trade.is_winner is False
        
        # Test very small price movements
        trade = Trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        trade.close_trade(100.01, exit_datetime, 1)
        assert abs(trade.pnl_pct - 0.01) < 1e-10
        assert trade.is_winner is True