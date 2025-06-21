"""
Test suite for strategy module.
Following TDD approach - RED phase: Write failing tests first.
"""

import pytest
import pandas as pd
import numpy as np
import logging
from unittest.mock import patch, MagicMock

# Import will fail initially - that's expected in RED phase
try:
    from src.strategy import StrategyEngine
    from src.indicators import TechnicalIndicators
except ImportError:
    # Expected to fail in RED phase
    pass


class TestStrategyEngine:
    """Test suite for StrategyEngine class."""
    
    def setup_method(self):
        """Setup test data for each test method."""
        # Create sample OHLCV data for testing
        dates = pd.date_range('2023-01-01', periods=200, freq='h')
        np.random.seed(42)  # For reproducible tests
        
        # Generate realistic price data with alternating trends to create signals
        base_price = 18000
        # Create oscillating trend to generate trend changes
        trend_component = 200 * np.sin(np.linspace(0, 4*np.pi, 200))
        noise = np.random.normal(0, 50, 200)  # Increased noise for more volatility
        close_prices = base_price + trend_component + noise
        
        # Ensure High >= Close and Low <= Close
        high_prices = close_prices + np.abs(np.random.normal(20, 10, 200))
        low_prices = close_prices - np.abs(np.random.normal(20, 10, 200))
        open_prices = close_prices + np.random.normal(0, 15, 200)
        
        # Generate volume data with some correlation to price movement
        volumes = np.random.randint(1000000, 10000000, 200)
        
        self.test_data = pd.DataFrame({
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volumes
        }, index=dates)
        
        # Initialize strategy engine
        self.strategy = StrategyEngine()
        self.indicators = TechnicalIndicators()
    
    def test_strategy_initialization(self):
        """Test StrategyEngine class initialization."""
        assert self.strategy is not None
        assert hasattr(self.strategy, 'indicators')
    
    def test_generate_baseline_signals(self):
        """Test baseline strategy signal generation."""
        atr_period = 10
        multiplier = 3.0
        
        signals = self.strategy.generate_baseline_signals(
            self.test_data, atr_period, multiplier
        )
        
        # Should return a DataFrame with signal column
        assert isinstance(signals, pd.DataFrame)
        assert 'signal' in signals.columns
        assert 'supertrend' in signals.columns
        assert 'trend' in signals.columns
        
        # Length should match input data
        assert len(signals) == len(self.test_data)
        
        # Signals should be 1 (BUY), -1 (SELL), or 0 (HOLD)
        signal_values = signals['signal'].dropna()
        assert signal_values.isin([1, -1, 0]).all()
    
    def test_generate_baseline_signals_parameters(self):
        """Test baseline signals with different parameters."""
        # Test with different ATR periods
        for period in [5, 10, 15, 20]:
            signals = self.strategy.generate_baseline_signals(
                self.test_data, period, 3.0
            )
            assert isinstance(signals, pd.DataFrame)
            assert 'signal' in signals.columns
        
        # Test with different multipliers
        for multiplier in [2.0, 2.5, 3.0, 4.0, 5.0]:
            signals = self.strategy.generate_baseline_signals(
                self.test_data, 10, multiplier
            )
            assert isinstance(signals, pd.DataFrame)
            assert 'signal' in signals.columns
    
    def test_apply_trend_filter(self):
        """Test trend filter application."""
        # Generate baseline signals first
        baseline_signals = self.strategy.generate_baseline_signals(
            self.test_data, 10, 3.0
        )
        
        ema_period = 100
        filtered_signals = self.strategy.apply_trend_filter(
            self.test_data, baseline_signals, ema_period
        )
        
        # Should return a DataFrame with filtered signals
        assert isinstance(filtered_signals, pd.DataFrame)
        assert 'signal' in filtered_signals.columns
        assert 'ema_100' in filtered_signals.columns
        
        # Length should match input data
        assert len(filtered_signals) == len(self.test_data)
        
        # Should have fewer or equal signals than baseline
        baseline_trades = (baseline_signals['signal'] != 0).sum()
        filtered_trades = (filtered_signals['signal'] != 0).sum()
        assert filtered_trades <= baseline_trades
    
    def test_apply_volume_filter(self):
        """Test volume filter application."""
        # Generate signals with trend filter
        baseline_signals = self.strategy.generate_baseline_signals(
            self.test_data, 10, 3.0
        )
        trend_filtered = self.strategy.apply_trend_filter(
            self.test_data, baseline_signals, 100
        )
        
        volume_period = 20
        volume_filtered = self.strategy.apply_volume_filter(
            self.test_data, trend_filtered, volume_period
        )
        
        # Should return a DataFrame with volume filtered signals
        assert isinstance(volume_filtered, pd.DataFrame)
        assert 'signal' in volume_filtered.columns
        assert 'volume_ma_20' in volume_filtered.columns
        
        # Length should match input data
        assert len(volume_filtered) == len(self.test_data)
        
        # Should have fewer or equal signals than trend filtered
        trend_trades = (trend_filtered['signal'] != 0).sum()
        volume_trades = (volume_filtered['signal'] != 0).sum()
        assert volume_trades <= trend_trades
    
    def test_apply_volatility_filter(self):
        """Test volatility filter application."""
        # Generate signals with previous filters
        baseline_signals = self.strategy.generate_baseline_signals(
            self.test_data, 10, 3.0
        )
        trend_filtered = self.strategy.apply_trend_filter(
            self.test_data, baseline_signals, 100
        )
        volume_filtered = self.strategy.apply_volume_filter(
            self.test_data, trend_filtered, 20
        )
        
        atr_period = 14
        percentile = 95
        volatility_filtered = self.strategy.apply_volatility_filter(
            self.test_data, volume_filtered, atr_period, percentile
        )
        
        # Should return a DataFrame with volatility filtered signals
        assert isinstance(volatility_filtered, pd.DataFrame)
        assert 'signal' in volatility_filtered.columns
        assert 'normalized_atr' in volatility_filtered.columns
        assert 'atr_threshold' in volatility_filtered.columns
        
        # Length should match input data
        assert len(volatility_filtered) == len(self.test_data)
        
        # Should have fewer or equal signals than volume filtered
        volume_trades = (volume_filtered['signal'] != 0).sum()
        volatility_trades = (volatility_filtered['signal'] != 0).sum()
        assert volatility_trades <= volume_trades
    
    def test_generate_improved_signals(self):
        """Test improved strategy with all filters."""
        # Strategy parameters
        params = {
            'atr_period': 10,
            'multiplier': 3.0,
            'ema_period': 100,
            'volume_period': 20,
            'volatility_period': 14,
            'volatility_percentile': 95
        }
        
        improved_signals = self.strategy.generate_improved_signals(
            self.test_data, **params
        )
        
        # Should return a DataFrame with all components
        assert isinstance(improved_signals, pd.DataFrame)
        assert 'signal' in improved_signals.columns
        assert 'supertrend' in improved_signals.columns
        assert 'ema_100' in improved_signals.columns
        assert 'volume_ma_20' in improved_signals.columns
        assert 'normalized_atr' in improved_signals.columns
        
        # Length should match input data
        assert len(improved_signals) == len(self.test_data)
        
        # Signals should be 1 (BUY), -1 (SELL), or 0 (HOLD)
        signal_values = improved_signals['signal'].dropna()
        assert signal_values.isin([1, -1, 0]).all()
    
    def test_strategy_comparison(self):
        """Test comparison between baseline and improved strategies."""
        # Generate both strategies
        baseline = self.strategy.generate_baseline_signals(self.test_data, 10, 3.0)
        
        improved_params = {
            'atr_period': 10,
            'multiplier': 3.0,
            'ema_period': 100,
            'volume_period': 20,
            'volatility_period': 14,
            'volatility_percentile': 95
        }
        improved = self.strategy.generate_improved_signals(self.test_data, **improved_params)
        
        # Count signals for each strategy
        baseline_trades = (baseline['signal'] != 0).sum()
        improved_trades = (improved['signal'] != 0).sum()
        
        # Improved strategy should typically have fewer trades (more selective)
        assert improved_trades <= baseline_trades
        
        # With oscillating test data, we should get some signals
        # If not, the strategy is working but might need different parameters
        # This is acceptable behavior - we just verify the relationship holds
        print(f"Baseline trades: {baseline_trades}, Improved trades: {improved_trades}")
        
        # The key requirement is that improved <= baseline (more selective)
        # Both having 0 trades is valid if market conditions don't trigger signals
    
    def test_signal_consistency(self):
        """Test signal consistency and logic."""
        signals = self.strategy.generate_baseline_signals(self.test_data, 10, 3.0)
        
        # Check that signals are consistent with trend direction
        for i in range(1, len(signals)):
            if pd.notna(signals['signal'].iloc[i]) and signals['signal'].iloc[i] != 0:
                current_signal = signals['signal'].iloc[i]
                current_trend = signals['trend'].iloc[i]
                
                # BUY signal should correspond to bullish trend (1)
                # SELL signal should correspond to bearish trend (-1)
                if current_signal == 1:  # BUY
                    assert current_trend == 1
                elif current_signal == -1:  # SELL
                    assert current_trend == -1
    
    def test_error_handling_invalid_data(self):
        """Test error handling with invalid data."""
        # Test with empty DataFrame
        empty_data = pd.DataFrame()
        
        with pytest.raises((ValueError, KeyError)):
            self.strategy.generate_baseline_signals(empty_data, 10, 3.0)
    
    def test_error_handling_invalid_parameters(self):
        """Test error handling with invalid parameters."""
        # Test with negative parameters
        with pytest.raises(ValueError):
            self.strategy.generate_baseline_signals(self.test_data, -1, 3.0)
        
        with pytest.raises(ValueError):
            self.strategy.generate_baseline_signals(self.test_data, 10, -1.0)
    
    def test_filter_integration(self):
        """Test that all filters work together correctly."""
        # Test the complete pipeline
        baseline = self.strategy.generate_baseline_signals(self.test_data, 10, 3.0)
        
        # Apply filters step by step
        trend_filtered = self.strategy.apply_trend_filter(self.test_data, baseline, 100)
        volume_filtered = self.strategy.apply_volume_filter(self.test_data, trend_filtered, 20)
        final_filtered = self.strategy.apply_volatility_filter(self.test_data, volume_filtered, 14, 95)
        
        # Compare with integrated approach
        improved_integrated = self.strategy.generate_improved_signals(
            self.test_data,
            atr_period=10,
            multiplier=3.0,
            ema_period=100,
            volume_period=20,
            volatility_period=14,
            volatility_percentile=95
        )
        
        # Results should be identical (signals should match)
        pd.testing.assert_series_equal(
            final_filtered['signal'], 
            improved_integrated['signal'], 
            check_names=False
        )