"""
Test suite for performance metrics module.

Tests comprehensive performance analysis including win rate,
equity curve, drawdown, and other key metrics.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.performance import PerformanceMetrics
from src.trade import Trade, TradeDirection, TradeStatus


class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics class."""
    
    @pytest.fixture
    def sample_trades(self):
        """Create sample trades for testing."""
        trades = []
        base_time = datetime(2023, 1, 1, 10, 0)
        
        # Create 5 trades: 3 winners, 2 losers
        # Trade 1: LONG winner (+10%)
        trade1 = Trade(TradeDirection.LONG, 100.0, base_time, 0)
        trade1.close_trade(110.0, base_time + timedelta(hours=1), 1)
        trades.append(trade1)
        
        # Trade 2: SHORT winner (+5%)
        trade2 = Trade(TradeDirection.SHORT, 100.0, base_time + timedelta(hours=2), 2)
        trade2.close_trade(95.0, base_time + timedelta(hours=3), 3)
        trades.append(trade2)
        
        # Trade 3: LONG loser (-3%)
        trade3 = Trade(TradeDirection.LONG, 100.0, base_time + timedelta(hours=4), 4)
        trade3.close_trade(97.0, base_time + timedelta(hours=5), 5)
        trades.append(trade3)
        
        # Trade 4: SHORT loser (-7%)
        trade4 = Trade(TradeDirection.SHORT, 100.0, base_time + timedelta(hours=6), 6)
        trade4.close_trade(107.0, base_time + timedelta(hours=7), 7)
        trades.append(trade4)
        
        # Trade 5: LONG winner (+2%)
        trade5 = Trade(TradeDirection.LONG, 100.0, base_time + timedelta(hours=8), 8)
        trade5.close_trade(102.0, base_time + timedelta(hours=9), 9)
        trades.append(trade5)
        
        return trades
    
    @pytest.fixture
    def empty_trades(self):
        """Create empty trades list for edge case testing."""
        return []
    
    @pytest.fixture
    def open_trades(self):
        """Create list with open trades for testing."""
        base_time = datetime(2023, 1, 1, 10, 0)
        trades = []
        
        # Open trade (should be ignored in calculations)
        trade = Trade(TradeDirection.LONG, 100.0, base_time, 0)
        trades.append(trade)
        
        return trades
    
    def test_initialization(self, sample_trades):
        """Test PerformanceMetrics initialization."""
        metrics = PerformanceMetrics(sample_trades, initial_capital=50000.0)
        
        assert metrics.trades == sample_trades
        assert metrics.initial_capital == 50000.0
        assert len(metrics.closed_trades) == 5
        assert all(trade.status == TradeStatus.CLOSED for trade in metrics.closed_trades)
    
    def test_default_initial_capital(self, sample_trades):
        """Test default initial capital."""
        metrics = PerformanceMetrics(sample_trades)
        assert metrics.initial_capital == 100000.0
    
    def test_calculate_win_rate(self, sample_trades):
        """Test win rate calculation."""
        metrics = PerformanceMetrics(sample_trades)
        win_rate = metrics.calculate_win_rate()
        
        # 3 winners out of 5 trades = 60%
        assert win_rate == 60.0
    
    def test_calculate_win_rate_empty(self, empty_trades):
        """Test win rate calculation with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        win_rate = metrics.calculate_win_rate()
        assert win_rate == 0.0
    
    def test_calculate_win_rate_with_open_trades(self, open_trades):
        """Test win rate calculation ignores open trades."""
        metrics = PerformanceMetrics(open_trades)
        win_rate = metrics.calculate_win_rate()
        assert win_rate == 0.0
    
    def test_calculate_total_return(self, sample_trades):
        """Test total return calculation."""
        metrics = PerformanceMetrics(sample_trades)
        total_return = metrics.calculate_total_return()
        
        # 10% + 5% + (-3%) + (-7%) + 2% = 7%
        assert abs(total_return - 7.0) < 1e-10
    
    def test_calculate_total_return_empty(self, empty_trades):
        """Test total return with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        total_return = metrics.calculate_total_return()
        assert total_return == 0.0
    
    def test_calculate_average_return_per_trade(self, sample_trades):
        """Test average return per trade calculation."""
        metrics = PerformanceMetrics(sample_trades)
        avg_return = metrics.calculate_average_return_per_trade()
        
        # 7% / 5 trades = 1.4%
        assert avg_return == 1.4
    
    def test_calculate_average_return_empty(self, empty_trades):
        """Test average return with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        avg_return = metrics.calculate_average_return_per_trade()
        assert avg_return == 0.0
    
    def test_calculate_best_trade(self, sample_trades):
        """Test best trade calculation."""
        metrics = PerformanceMetrics(sample_trades)
        best_trade = metrics.calculate_best_trade()
        
        # Best trade should be 10%
        assert best_trade == 10.0
    
    def test_calculate_best_trade_empty(self, empty_trades):
        """Test best trade with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        best_trade = metrics.calculate_best_trade()
        assert best_trade == 0.0
    
    def test_calculate_worst_trade(self, sample_trades):
        """Test worst trade calculation."""
        metrics = PerformanceMetrics(sample_trades)
        worst_trade = metrics.calculate_worst_trade()
        
        # Worst trade should be -7%
        assert abs(worst_trade - (-7.0)) < 1e-10
    
    def test_calculate_worst_trade_empty(self, empty_trades):
        """Test worst trade with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        worst_trade = metrics.calculate_worst_trade()
        assert worst_trade == 0.0
    
    def test_generate_equity_curve(self, sample_trades):
        """Test equity curve generation."""
        initial_capital = 100000.0
        metrics = PerformanceMetrics(sample_trades, initial_capital)
        equity_curve = metrics.generate_equity_curve()
        
        assert isinstance(equity_curve, pd.DataFrame)
        assert 'equity' in equity_curve.columns
        assert len(equity_curve) == 6  # Initial + 5 trades
        
        # Check initial equity
        assert equity_curve.iloc[0]['equity'] == initial_capital
        
        # Check final equity (should reflect cumulative returns)
        # Note: Equity curve compounds returns, so final value may differ from simple addition
        final_equity = equity_curve.iloc[-1]['equity']
        assert final_equity > initial_capital  # Should be profitable overall
    
    def test_generate_equity_curve_empty(self, empty_trades):
        """Test equity curve with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        equity_curve = metrics.generate_equity_curve()
        
        assert isinstance(equity_curve, pd.DataFrame)
        assert equity_curve.empty
    
    def test_calculate_profit_factor(self, sample_trades):
        """Test profit factor calculation."""
        metrics = PerformanceMetrics(sample_trades)
        profit_factor = metrics.calculate_profit_factor()
        
        # Gross profit: 10% + 5% + 2% = 17%
        # Gross loss: 3% + 7% = 10%
        # Profit factor: 17/10 = 1.7
        assert abs(profit_factor - 1.7) < 0.001
    
    def test_calculate_profit_factor_no_losses(self):
        """Test profit factor with no losing trades."""
        base_time = datetime(2023, 1, 1, 10, 0)
        trades = []
        
        # Only winning trades
        trade1 = Trade(TradeDirection.LONG, 100.0, base_time, 0)
        trade1.close_trade(110.0, base_time + timedelta(hours=1), 1)
        trades.append(trade1)
        
        metrics = PerformanceMetrics(trades)
        profit_factor = metrics.calculate_profit_factor()
        
        assert profit_factor == float('inf')
    
    def test_calculate_profit_factor_no_profits(self):
        """Test profit factor with no winning trades."""
        base_time = datetime(2023, 1, 1, 10, 0)
        trades = []
        
        # Only losing trades
        trade1 = Trade(TradeDirection.LONG, 100.0, base_time, 0)
        trade1.close_trade(90.0, base_time + timedelta(hours=1), 1)
        trades.append(trade1)
        
        metrics = PerformanceMetrics(trades)
        profit_factor = metrics.calculate_profit_factor()
        
        assert profit_factor == 0.0
    
    def test_calculate_profit_factor_empty(self, empty_trades):
        """Test profit factor with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        profit_factor = metrics.calculate_profit_factor()
        assert profit_factor == 0.0
    
    def test_calculate_maximum_drawdown(self, sample_trades):
        """Test maximum drawdown calculation."""
        metrics = PerformanceMetrics(sample_trades, 100000.0)
        drawdown_info = metrics.calculate_maximum_drawdown()
        
        assert 'max_drawdown_pct' in drawdown_info
        assert 'max_drawdown_duration' in drawdown_info
        assert isinstance(drawdown_info['max_drawdown_pct'], float)
        assert isinstance(drawdown_info['max_drawdown_duration'], int)
        assert drawdown_info['max_drawdown_pct'] >= 0
        assert drawdown_info['max_drawdown_duration'] >= 0
    
    def test_calculate_maximum_drawdown_empty(self, empty_trades):
        """Test maximum drawdown with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        drawdown_info = metrics.calculate_maximum_drawdown()
        
        assert drawdown_info['max_drawdown_pct'] == 0.0
        assert drawdown_info['max_drawdown_duration'] == 0
    
    def test_get_summary_stats(self, sample_trades):
        """Test comprehensive summary statistics."""
        metrics = PerformanceMetrics(sample_trades)
        summary = metrics.get_summary_stats()
        
        expected_keys = [
            'total_trades', 'win_rate_pct', 'total_return_pct',
            'avg_return_per_trade_pct', 'best_trade_pct', 'worst_trade_pct',
            'profit_factor', 'max_drawdown_pct', 'max_drawdown_duration'
        ]
        
        for key in expected_keys:
            assert key in summary
        
        assert summary['total_trades'] == 5
        assert summary['win_rate_pct'] == 60.0
        assert abs(summary['total_return_pct'] - 7.0) < 1e-10
        assert summary['avg_return_per_trade_pct'] == 1.4
        assert summary['best_trade_pct'] == 10.0
        assert abs(summary['worst_trade_pct'] - (-7.0)) < 1e-10
        assert abs(summary['profit_factor'] - 1.7) < 0.001
    
    def test_get_summary_stats_empty(self, empty_trades):
        """Test summary statistics with no trades."""
        metrics = PerformanceMetrics(empty_trades)
        summary = metrics.get_summary_stats()
        
        assert summary['total_trades'] == 0
        assert summary['win_rate_pct'] == 0.0
        assert summary['total_return_pct'] == 0.0
        assert summary['avg_return_per_trade_pct'] == 0.0
        assert summary['best_trade_pct'] == 0.0
        assert summary['worst_trade_pct'] == 0.0
        assert summary['profit_factor'] == 0.0
        assert summary['max_drawdown_pct'] == 0.0
        assert summary['max_drawdown_duration'] == 0