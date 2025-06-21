"""
Tests for config module
"""

import pytest
from src.config import Config


class TestConfig:
    """Test cases for Config class"""
    
    def test_config_constants(self):
        """Test that all configuration constants are defined"""
        assert Config.TICKER == '^NSEI'
        assert Config.PERIOD == '730d'
        assert Config.INTERVAL == '1h'
        assert Config.CACHE_DIR == 'data'
        assert Config.CACHE_FILE == 'data/nifty_hourly.csv'
        
    def test_baseline_strategy_params(self):
        """Test baseline strategy parameters"""
        assert Config.BASELINE_ATR_PERIOD == 10
        assert Config.BASELINE_MULTIPLIER == 3.0
        
    def test_improved_strategy_params(self):
        """Test improved strategy parameters"""
        assert Config.EMA_PERIOD == 100
        assert Config.VOLUME_MA_PERIOD == 20
        assert Config.ATR_VOLATILITY_PERIOD == 14
        assert Config.VOLATILITY_PERCENTILE == 95
        
    def test_optimization_parameters(self):
        """Test optimization parameters"""
        assert Config.ATR_PERIOD_RANGE == (5, 20)
        assert Config.MULTIPLIER_RANGE == (2.0, 5.0)
        assert Config.IN_SAMPLE_RATIO == 0.7
        assert Config.OUT_SAMPLE_RATIO == 0.3
        
    def test_get_optimization_params(self):
        """Test get_optimization_params method"""
        params = Config.get_optimization_params()
        
        assert isinstance(params, dict)
        assert 'atr_period_range' in params
        assert 'multiplier_range' in params
        assert 'in_sample_ratio' in params
        assert params['atr_period_range'] == (5, 20)
        assert params['multiplier_range'] == (2.0, 5.0)
        assert params['in_sample_ratio'] == 0.7
        
    def test_get_strategy_params(self):
        """Test get_strategy_params method"""
        params = Config.get_strategy_params()
        
        assert isinstance(params, dict)
        assert 'baseline' in params
        assert 'improved' in params
        
        # Test baseline params
        baseline = params['baseline']
        assert baseline['atr_period'] == 10
        assert baseline['multiplier'] == 3.0
        
        # Test improved params
        improved = params['improved']
        assert improved['ema_period'] == 100
        assert improved['volume_ma_period'] == 20
        assert improved['atr_volatility_period'] == 14
        assert improved['volatility_percentile'] == 95