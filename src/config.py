"""
Configuration module for Supertrend Strategy
Contains all configuration parameters and settings
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for Supertrend Strategy"""
    
    # Data Configuration
    TICKER = '^NSEI'  # Nifty 50 Index
    PERIOD = '730d'   # 730 days (maximum for hourly data)
    INTERVAL = '1h'   # Hourly interval
    
    # Cache Configuration
    CACHE_DIR = 'data'
    CACHE_FILE = os.path.join(CACHE_DIR, 'nifty_hourly.csv')
    
    # Strategy Parameters - Baseline
    BASELINE_ATR_PERIOD = 10
    BASELINE_MULTIPLIER = 3.0
    
    # Strategy Parameters - Improved
    EMA_PERIOD = 100          # Trend filter
    VOLUME_MA_PERIOD = 20     # Volume filter
    ATR_VOLATILITY_PERIOD = 14  # Volatility filter
    VOLATILITY_PERCENTILE = 95  # ATR percentile threshold
    
    # Optimization Parameters
    ATR_PERIOD_RANGE = (5, 20)    # Range for ATR period optimization
    MULTIPLIER_RANGE = (2.0, 5.0)  # Range for multiplier optimization
    
    # Data Splitting
    IN_SAMPLE_RATIO = 0.7  # 70% for in-sample data
    OUT_SAMPLE_RATIO = 0.3  # 30% for out-of-sample data
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_optimization_params(cls) -> Dict[str, Any]:
        """Get optimization parameters as dictionary"""
        return {
            'atr_period_range': cls.ATR_PERIOD_RANGE,
            'multiplier_range': cls.MULTIPLIER_RANGE,
            'in_sample_ratio': cls.IN_SAMPLE_RATIO
        }
    
    @classmethod
    def get_strategy_params(cls) -> Dict[str, Any]:
        """Get strategy parameters as dictionary"""
        return {
            'baseline': {
                'atr_period': cls.BASELINE_ATR_PERIOD,
                'multiplier': cls.BASELINE_MULTIPLIER
            },
            'improved': {
                'ema_period': cls.EMA_PERIOD,
                'volume_ma_period': cls.VOLUME_MA_PERIOD,
                'atr_volatility_period': cls.ATR_VOLATILITY_PERIOD,
                'volatility_percentile': cls.VOLATILITY_PERCENTILE
            }
        }


# Configuration dictionaries for easy import
BASELINE_CONFIG = {
    'atr_period': Config.BASELINE_ATR_PERIOD,
    'multiplier': Config.BASELINE_MULTIPLIER
}

IMPROVED_CONFIG = {
    'atr_period': Config.BASELINE_ATR_PERIOD,
    'multiplier': Config.BASELINE_MULTIPLIER,
    'ema_period': Config.EMA_PERIOD,
    'volume_ma_period': Config.VOLUME_MA_PERIOD,
    'atr_volatility_period': Config.ATR_VOLATILITY_PERIOD,
    'volatility_percentile': Config.VOLATILITY_PERCENTILE
}