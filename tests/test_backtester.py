"""
Test suite for backtesting engine module.

Tests the core backtesting functionality including trade execution,
position management, and performance tracking.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.backtester import BacktestEngine
from src.trade import Trade, TradeDirection, TradeStatus
from src.config import BASELINE_CONFIG, IMPROVED_CONFIG


class TestBacktestEngine:
    """Test cases for BacktestEngine class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data for testing."""
        dates = pd.date_range(start='2023-01-01', periods=10, freq='H')
        data = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'High': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'Low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            'Close': [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5, 108.5, 109.5],
            'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        }, index=dates)
        return data
    
    @pytest.fixture
    def simple_signals_data(self):
        """Create simple data with manual signals for testing."""
        dates = pd.date_range(start='2023-01-01', periods=5, freq='H')
        data = pd.DataFrame({
            'Open': [100, 102, 104, 106, 108],
            'High': [101, 103, 105, 107, 109],
            'Low': [99, 101, 103, 105, 107],
            'Close': [100, 102, 104, 106, 108],
            'Volume': [1000, 1100, 1200, 1300, 1400],
            'signal': ['BUY', 'HOLD', 'SELL', 'HOLD', 'BUY']
        }, index=dates)
        return data
    
    @pytest.fixture
    def backtest_engine(self):
        """Create a BacktestEngine instance for testing."""
        return BacktestEngine(initial_capital=50000.0)
    
    def test_initialization(self, backtest_engine):
        """Test BacktestEngine initialization."""
        assert backtest_engine.initial_capital == 50000.0
        assert backtest_engine.trades == []
        assert backtest_engine.current_position is None
        assert backtest_engine.current_trade is None
    
    def test_default_initial_capital(self):
        """Test default initial capital."""
        engine = BacktestEngine()
        assert engine.initial_capital == 100000.0
    
    def test_reset(self, backtest_engine):
        """Test engine reset functionality."""
        # Simulate some state
        backtest_engine.trades = [Mock()]
        backtest_engine.current_position = TradeDirection.LONG
        backtest_engine.current_trade = Mock()
        
        # Reset
        backtest_engine.reset()
        
        assert backtest_engine.trades == []
        assert backtest_engine.current_position is None
        assert backtest_engine.current_trade is None
    
    def test_validate_data_valid(self, backtest_engine, sample_data):
        """Test data validation with valid data."""
        assert backtest_engine.validate_data(sample_data) is True
    
    def test_validate_data_missing_columns(self, backtest_engine):
        """Test data validation with missing columns."""
        invalid_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [101, 102],
            # Missing Low, Close, Volume
        })
        
        assert backtest_engine.validate_data(invalid_data) is False
    
    def test_validate_data_empty(self, backtest_engine):
        """Test data validation with empty data."""
        empty_data = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        assert backtest_engine.validate_data(empty_data) is False
    
    def test_validate_data_nan_values(self, backtest_engine):
        """Test data validation with NaN values in Close."""
        invalid_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [101, 102],
            'Low': [99, 100],
            'Close': [100, np.nan],  # NaN in Close
            'Volume': [1000, 1100]
        })
        
        assert backtest_engine.validate_data(invalid_data) is False
    
    def test_open_trade_long(self, backtest_engine):
        """Test opening a LONG trade."""
        test_datetime = datetime(2023, 1, 1, 10, 0)
        
        backtest_engine._open_trade(TradeDirection.LONG, 100.0, test_datetime, 0)
        
        assert backtest_engine.current_position == TradeDirection.LONG
        assert backtest_engine.current_trade is not None
        assert backtest_engine.current_trade.direction == TradeDirection.LONG
        assert backtest_engine.current_trade.entry_price == 100.0
        assert backtest_engine.current_trade.entry_datetime == test_datetime
        assert backtest_engine.current_trade.entry_index == 0
        assert backtest_engine.current_trade.status == TradeStatus.OPEN
    
    def test_open_trade_short(self, backtest_engine):
        """Test opening a SHORT trade."""
        test_datetime = datetime(2023, 1, 1, 10, 0)
        
        backtest_engine._open_trade(TradeDirection.SHORT, 100.0, test_datetime, 0)
        
        assert backtest_engine.current_position == TradeDirection.SHORT
        assert backtest_engine.current_trade is not None
        assert backtest_engine.current_trade.direction == TradeDirection.SHORT
    
    def test_close_current_trade(self, backtest_engine):
        """Test closing current trade."""
        # First open a trade
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        backtest_engine._open_trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        
        # Close the trade
        backtest_engine._close_current_trade(110.0, exit_datetime, 1)
        
        # Check that trade was closed and added to trades list
        assert backtest_engine.current_trade is None
        assert backtest_engine.current_position is None
        assert len(backtest_engine.trades) == 1
        
        closed_trade = backtest_engine.trades[0]
        assert closed_trade.status == TradeStatus.CLOSED
        assert closed_trade.exit_price == 110.0
        assert closed_trade.exit_datetime == exit_datetime
        assert closed_trade.pnl_pct == 10.0
    
    def test_close_current_trade_no_open_trade(self, backtest_engine):
        """Test closing trade when no trade is open."""
        exit_datetime = datetime(2023, 1, 1, 11, 0)
        
        # Should not raise an error
        backtest_engine._close_current_trade(110.0, exit_datetime, 1)
        
        assert len(backtest_engine.trades) == 0
    
    def test_process_signal_buy_no_position(self, backtest_engine):
        """Test processing BUY signal with no current position."""
        test_datetime = datetime(2023, 1, 1, 10, 0)
        
        backtest_engine._process_signal('BUY', 100.0, test_datetime, 0)
        
        assert backtest_engine.current_position == TradeDirection.LONG
        assert backtest_engine.current_trade is not None
    
    def test_process_signal_sell_no_position(self, backtest_engine):
        """Test processing SELL signal with no current position."""
        test_datetime = datetime(2023, 1, 1, 10, 0)
        
        backtest_engine._process_signal('SELL', 100.0, test_datetime, 0)
        
        assert backtest_engine.current_position == TradeDirection.SHORT
        assert backtest_engine.current_trade is not None
    
    def test_process_signal_buy_with_short_position(self, backtest_engine):
        """Test processing BUY signal when holding SHORT position (reversal)."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        signal_datetime = datetime(2023, 1, 1, 11, 0)
        
        # First open a short position
        backtest_engine._open_trade(TradeDirection.SHORT, 100.0, entry_datetime, 0)
        
        # Process BUY signal (should close short and open long)
        backtest_engine._process_signal('BUY', 95.0, signal_datetime, 1)
        
        # Should have closed the short trade
        assert len(backtest_engine.trades) == 1
        closed_trade = backtest_engine.trades[0]
        assert closed_trade.direction == TradeDirection.SHORT
        assert closed_trade.status == TradeStatus.CLOSED
        
        # Should have opened new long position
        assert backtest_engine.current_position == TradeDirection.LONG
        assert backtest_engine.current_trade.direction == TradeDirection.LONG
    
    def test_process_signal_sell_with_long_position(self, backtest_engine):
        """Test processing SELL signal when holding LONG position (reversal)."""
        entry_datetime = datetime(2023, 1, 1, 10, 0)
        signal_datetime = datetime(2023, 1, 1, 11, 0)
        
        # First open a long position
        backtest_engine._open_trade(TradeDirection.LONG, 100.0, entry_datetime, 0)
        
        # Process SELL signal (should close long and open short)
        backtest_engine._process_signal('SELL', 105.0, signal_datetime, 1)
        
        # Should have closed the long trade
        assert len(backtest_engine.trades) == 1
        closed_trade = backtest_engine.trades[0]
        assert closed_trade.direction == TradeDirection.LONG
        assert closed_trade.status == TradeStatus.CLOSED
        
        # Should have opened new short position
        assert backtest_engine.current_position == TradeDirection.SHORT
        assert backtest_engine.current_trade.direction == TradeDirection.SHORT
    
    def test_execute_trades_simple(self, backtest_engine, simple_signals_data):
        """Test trade execution with simple signal data."""
        # simple_signals_data has: ['BUY', 'HOLD', 'SELL', 'HOLD', 'BUY']
        # This should execute: BUY(100) -> SELL(104) -> BUY(108)
        # Resulting in 2 completed trades and 1 open trade
        backtest_engine._execute_trades(simple_signals_data)
        
        # Should have executed: BUY->SELL (1 trade), SELL->BUY (1 trade), final BUY open
        assert len(backtest_engine.trades) == 2
        
        # Check the first completed trade (LONG)
        trade1 = backtest_engine.trades[0]
        assert trade1.direction == TradeDirection.LONG
        assert trade1.entry_price == 100.0
        assert trade1.exit_price == 104.0
        assert trade1.status == TradeStatus.CLOSED
        
        # Check the second completed trade (SHORT)
        trade2 = backtest_engine.trades[1]
        assert trade2.direction == TradeDirection.SHORT
        assert trade2.entry_price == 104.0
        assert trade2.exit_price == 108.0
        assert trade2.status == TradeStatus.CLOSED
        
        # Should have a current open position (final BUY)
        assert backtest_engine.current_position == TradeDirection.LONG
        assert backtest_engine.current_trade is not None
    
    def test_close_final_trade(self, backtest_engine, simple_signals_data):
        """Test closing final trade at end of backtest."""
        # Execute trades
        backtest_engine._execute_trades(simple_signals_data)
        
        # Should have an open trade
        assert backtest_engine.current_trade is not None
        
        # Close final trade
        backtest_engine.close_final_trade(simple_signals_data)
        
        # Should have closed the final trade
        assert backtest_engine.current_trade is None
        assert backtest_engine.current_position is None
        assert len(backtest_engine.trades) == 3  # All trades now closed
    
    def test_close_final_trade_no_open_trade(self, backtest_engine, simple_signals_data):
        """Test closing final trade when no trade is open."""
        # Should not raise an error
        backtest_engine.close_final_trade(simple_signals_data)
        
        assert len(backtest_engine.trades) == 0
    
    def test_get_trade_summary_empty(self, backtest_engine):
        """Test trade summary with no trades."""
        summary = backtest_engine.get_trade_summary()
        
        expected = {
            'total_trades': 0,
            'long_trades': 0,
            'short_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
        
        assert summary == expected
    
    def test_get_trade_summary_with_trades(self, backtest_engine):
        """Test trade summary with completed trades."""
        # Create sample trades
        base_time = datetime(2023, 1, 1, 10, 0)
        
        # Long winning trade
        trade1 = Trade(TradeDirection.LONG, 100.0, base_time, 0)
        trade1.close_trade(110.0, base_time + timedelta(hours=1), 1)
        
        # Short losing trade
        trade2 = Trade(TradeDirection.SHORT, 100.0, base_time + timedelta(hours=2), 2)
        trade2.close_trade(105.0, base_time + timedelta(hours=3), 3)
        
        # Long losing trade
        trade3 = Trade(TradeDirection.LONG, 100.0, base_time + timedelta(hours=4), 4)
        trade3.close_trade(95.0, base_time + timedelta(hours=5), 5)
        
        backtest_engine.trades = [trade1, trade2, trade3]
        
        summary = backtest_engine.get_trade_summary()
        
        expected = {
            'total_trades': 3,
            'long_trades': 2,
            'short_trades': 1,
            'winning_trades': 1,
            'losing_trades': 2
        }
        
        assert summary == expected
    
    @patch('src.backtester.StrategyEngine')
    def test_execute_strategy_baseline(self, mock_strategy_engine, backtest_engine, sample_data):
        """Test executing baseline strategy."""
        # Mock strategy engine
        mock_instance = mock_strategy_engine.return_value
        mock_signals = ['HOLD', 'BUY', 'HOLD', 'SELL', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'SELL', 'HOLD']
        mock_instance.generate_baseline_signals.return_value = mock_signals
        
        result = backtest_engine.execute_strategy(
            sample_data,
            BASELINE_CONFIG,
            use_improved_strategy=False
        )
        
        # Check that the strategy engine was called correctly
        mock_instance.generate_baseline_signals.assert_called_once_with(sample_data, BASELINE_CONFIG)
        
        # Check result structure
        assert 'trades' in result
        assert 'performance_metrics' in result
        assert 'equity_curve' in result
        assert 'total_signals' in result
        assert 'strategy_type' in result
        
        assert result['strategy_type'] == 'baseline'
        assert result['total_signals'] == 4  # BUY, SELL, BUY, SELL
    
    @patch('src.backtester.StrategyEngine')
    def test_execute_strategy_improved(self, mock_strategy_engine, backtest_engine, sample_data):
        """Test executing improved strategy."""
        # Mock strategy engine
        mock_instance = mock_strategy_engine.return_value
        mock_signals = ['HOLD', 'BUY', 'HOLD', 'HOLD', 'SELL', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD']
        mock_instance.generate_improved_signals.return_value = mock_signals
        
        result = backtest_engine.execute_strategy(
            sample_data,
            IMPROVED_CONFIG,
            use_improved_strategy=True
        )
        
        # Check that the strategy engine was called correctly (with unpacked parameters)
        mock_instance.generate_improved_signals.assert_called_once_with(
            data=sample_data,
            atr_period=IMPROVED_CONFIG['atr_period'],
            multiplier=IMPROVED_CONFIG['multiplier'],
            ema_period=IMPROVED_CONFIG['ema_period'],
            volume_period=IMPROVED_CONFIG['volume_ma_period'],
            volatility_period=IMPROVED_CONFIG['atr_volatility_period'],
            volatility_percentile=IMPROVED_CONFIG['volatility_percentile']
        )
        
        # Check result structure
        assert result['strategy_type'] == 'improved'
        assert result['total_signals'] == 2  # BUY, SELL
    
    def test_pandas_timestamp_conversion(self, backtest_engine):
        """Test conversion of pandas timestamps to datetime objects."""
        # Create data with pandas DatetimeIndex
        dates = pd.date_range(start='2023-01-01', periods=3, freq='H')
        data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100, 101, 102],
            'Volume': [1000, 1100, 1200],
            'signal': ['BUY', 'SELL', 'HOLD']
        }, index=dates)
        
        # Should handle pandas timestamps without error
        backtest_engine._execute_trades(data)
        
        # Should have one completed trade
        assert len(backtest_engine.trades) == 1
        
        # Check that datetime conversion worked
        trade = backtest_engine.trades[0]
        assert isinstance(trade.entry_datetime, datetime)
        assert isinstance(trade.exit_datetime, datetime)