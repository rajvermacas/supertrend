"""
Test suite for technical indicators module.
Following TDD approach - RED phase: Write failing tests first.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Import will fail initially - that's expected in RED phase
try:
    from src.indicators import TechnicalIndicators
except ImportError:
    # Expected to fail in RED phase
    pass


class TestTechnicalIndicators:
    """Test suite for TechnicalIndicators class."""
    
    def setup_method(self):
        """Setup test data for each test method."""
        # Create sample OHLCV data for testing
        dates = pd.date_range('2023-01-01', periods=100, freq='H')
        np.random.seed(42)  # For reproducible tests
        
        # Generate realistic price data
        base_price = 18000
        price_changes = np.random.normal(0, 50, 100)
        close_prices = base_price + np.cumsum(price_changes)
        
        # Ensure High >= Close and Low <= Close
        high_prices = close_prices + np.random.uniform(0, 50, 100)
        low_prices = close_prices - np.random.uniform(0, 50, 100)
        open_prices = close_prices + np.random.uniform(-25, 25, 100)
        
        # Generate volume data
        volumes = np.random.randint(1000000, 10000000, 100)
        
        self.test_data = pd.DataFrame({
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volumes
        }, index=dates)
        
        self.indicators = TechnicalIndicators()
    
    def test_indicators_initialization(self):
        """Test TechnicalIndicators class initialization."""
        assert self.indicators is not None
    
    def test_calculate_atr_basic(self):
        """Test ATR calculation with basic functionality."""
        period = 14
        atr_values = self.indicators.calculate_atr(self.test_data, period)
        
        # ATR should be a pandas Series
        assert isinstance(atr_values, pd.Series)
        
        # Length should match input data
        assert len(atr_values) == len(self.test_data)
        
        # First (period-1) values should be NaN
        assert pd.isna(atr_values.iloc[:period-1]).all()
        
        # Subsequent values should be positive
        assert (atr_values.iloc[period-1:] > 0).all()
    
    def test_calculate_atr_edge_cases(self):
        """Test ATR calculation edge cases."""
        # Test with insufficient data
        small_data = self.test_data.head(5)
        atr_values = self.indicators.calculate_atr(small_data, 14)
        assert pd.isna(atr_values).all()
        
        # Test with period = 1
        atr_values = self.indicators.calculate_atr(self.test_data, 1)
        assert not pd.isna(atr_values.iloc[0])
    
    def test_calculate_supertrend_basic(self):
        """Test Supertrend calculation with default parameters."""
        atr_period = 10
        multiplier = 3.0
        
        supertrend_values = self.indicators.calculate_supertrend(
            self.test_data, atr_period, multiplier
        )
        
        # Should return a DataFrame with supertrend and trend columns
        assert isinstance(supertrend_values, pd.DataFrame)
        assert 'supertrend' in supertrend_values.columns
        assert 'trend' in supertrend_values.columns
        
        # Length should match input data
        assert len(supertrend_values) == len(self.test_data)
        
        # Trend should be 1 (bullish) or -1 (bearish)
        trend_values = supertrend_values['trend'].dropna()
        assert trend_values.isin([1, -1]).all()
    
    def test_calculate_supertrend_parameters(self):
        """Test Supertrend with different parameters."""
        # Test with different ATR periods
        for period in [5, 10, 15, 20]:
            result = self.indicators.calculate_supertrend(self.test_data, period, 3.0)
            assert isinstance(result, pd.DataFrame)
        
        # Test with different multipliers
        for multiplier in [2.0, 2.5, 3.0, 4.0, 5.0]:
            result = self.indicators.calculate_supertrend(self.test_data, 10, multiplier)
            assert isinstance(result, pd.DataFrame)
    
    def test_calculate_ema_basic(self):
        """Test EMA calculation with basic functionality."""
        period = 100
        
        ema_values = self.indicators.calculate_ema(self.test_data['Close'], period)
        
        # EMA should be a pandas Series
        assert isinstance(ema_values, pd.Series)
        
        # Length should match input data
        assert len(ema_values) == len(self.test_data)
        
        # First value should not be NaN (EMA starts immediately)
        assert not pd.isna(ema_values.iloc[0])
        
        # Values should be reasonable (within range of price data)
        price_range = (self.test_data['Close'].min(), self.test_data['Close'].max())
        ema_range = (ema_values.min(), ema_values.max())
        assert ema_range[0] >= price_range[0] * 0.8  # Allow some flexibility
        assert ema_range[1] <= price_range[1] * 1.2
    
    def test_calculate_volume_ma_basic(self):
        """Test Volume MA calculation with basic functionality."""
        period = 20
        
        volume_ma = self.indicators.calculate_volume_ma(self.test_data['Volume'], period)
        
        # Volume MA should be a pandas Series
        assert isinstance(volume_ma, pd.Series)
        
        # Length should match input data
        assert len(volume_ma) == len(self.test_data)
        
        # First (period-1) values should be NaN
        assert pd.isna(volume_ma.iloc[:period-1]).all()
        
        # Subsequent values should be positive
        assert (volume_ma.iloc[period-1:] > 0).all()
    
    def test_calculate_normalized_atr(self):
        """Test normalized ATR calculation."""
        period = 14
        
        normalized_atr = self.indicators.calculate_normalized_atr(self.test_data, period)
        
        # Should be a pandas Series
        assert isinstance(normalized_atr, pd.Series)
        
        # Length should match input data
        assert len(normalized_atr) == len(self.test_data)
        
        # Values should be percentages (0-100)
        valid_values = normalized_atr.dropna()
        assert (valid_values >= 0).all()
        assert (valid_values <= 100).all()  # Reasonable upper bound
    
    def test_get_percentile_threshold(self):
        """Test percentile threshold calculation."""
        period = 14
        percentile = 95
        
        # Calculate normalized ATR first
        normalized_atr = self.indicators.calculate_normalized_atr(self.test_data, period)
        
        threshold = self.indicators.get_percentile_threshold(normalized_atr, percentile)
        
        # Threshold should be a single float value
        assert isinstance(threshold, float)
        
        # Threshold should be reasonable
        assert threshold > 0
        assert threshold < 100  # Should be less than 100%
    
    def test_integration_all_indicators(self):
        """Test integration of all indicators together."""
        # This test ensures all indicators can work together
        # (similar to how they'll be used in the strategy)
        
        # Calculate all indicators
        atr = self.indicators.calculate_atr(self.test_data, 14)
        supertrend = self.indicators.calculate_supertrend(self.test_data, 10, 3.0)
        ema = self.indicators.calculate_ema(self.test_data['Close'], 100)
        volume_ma = self.indicators.calculate_volume_ma(self.test_data['Volume'], 20)
        normalized_atr = self.indicators.calculate_normalized_atr(self.test_data, 14)
        
        # All should have same length
        assert len(atr) == len(supertrend) == len(ema) == len(volume_ma) == len(normalized_atr)
        
        # All should be pandas objects
        assert isinstance(atr, pd.Series)
        assert isinstance(supertrend, pd.DataFrame)
        assert isinstance(ema, pd.Series)
        assert isinstance(volume_ma, pd.Series)
        assert isinstance(normalized_atr, pd.Series)
    
    def test_error_handling_invalid_data(self):
        """Test error handling with invalid data."""
        # Test with empty DataFrame
        empty_data = pd.DataFrame()
        
        with pytest.raises((ValueError, KeyError)):
            self.indicators.calculate_supertrend(empty_data, 10, 3.0)
    
    def test_error_handling_invalid_parameters(self):
        """Test error handling with invalid parameters."""
        # Test with negative period
        with pytest.raises(ValueError):
            self.indicators.calculate_atr(self.test_data, -1)
        
        # Test with zero period
        with pytest.raises(ValueError):
            self.indicators.calculate_atr(self.test_data, 0)
        
        # Test with negative multiplier
        with pytest.raises(ValueError):
            self.indicators.calculate_supertrend(self.test_data, 10, -1.0)