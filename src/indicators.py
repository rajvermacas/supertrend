"""
Technical Indicators Module for Supertrend Strategy.

This module provides implementations of technical indicators used in the 
Supertrend trading strategy, including Supertrend, EMA, Volume MA, and ATR.

Classes:
    TechnicalIndicators: Main class containing all indicator calculations
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Technical Indicators class for calculating various trading indicators.
    
    This class implements technical indicators required for the Supertrend
    strategy, including ATR, Supertrend, EMA, Volume MA, and related calculations.
    """
    
    def __init__(self):
        """Initialize TechnicalIndicators class."""
        logger.info("TechnicalIndicators initialized")
    
    def calculate_atr(self, data: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            data: DataFrame with OHLC columns
            period: Number of periods for ATR calculation
            
        Returns:
            pd.Series: ATR values
            
        Raises:
            ValueError: If period is <= 0
        """
        if period <= 0:
            raise ValueError("Period must be greater than 0")
        
        if len(data) == 0:
            raise ValueError("Data cannot be empty")
        
        # Validate required columns
        required_columns = ['High', 'Low', 'Close']
        for col in required_columns:
            if col not in data.columns:
                raise KeyError(f"Required column '{col}' not found in data")
        
        high = data['High']
        low = data['Low']
        close = data['Close']
        prev_close = close.shift(1)
        
        # Calculate True Range components
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        # True Range is the maximum of the three
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR using exponential moving average
        atr = true_range.ewm(span=period, adjust=False).mean()
        
        # Set first (period-1) values to NaN to match expected behavior
        # If data length is less than period, all values should be NaN
        if len(atr) < period:
            atr[:] = np.nan
        elif len(atr) >= period:
            atr.iloc[:period-1] = np.nan
        
        logger.debug(f"Calculated ATR with period {period}")
        return atr
    
    def calculate_supertrend(self, data: pd.DataFrame, atr_period: int, 
                           multiplier: float) -> pd.DataFrame:
        """
        Calculate Supertrend indicator.
        
        Args:
            data: DataFrame with OHLC columns
            atr_period: Period for ATR calculation
            multiplier: Multiplier for ATR
            
        Returns:
            pd.DataFrame: DataFrame with 'supertrend' and 'trend' columns
            
        Raises:
            ValueError: If multiplier is <= 0
        """
        if multiplier <= 0:
            raise ValueError("Multiplier must be greater than 0")
        
        # Calculate ATR
        atr = self.calculate_atr(data, atr_period)
        
        # Calculate basic upper and lower bands
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Basic bands
        basic_upper = ((high + low) / 2) + (multiplier * atr)
        basic_lower = ((high + low) / 2) - (multiplier * atr)
        
        # Initialize final bands
        final_upper = pd.Series(index=data.index, dtype=float)
        final_lower = pd.Series(index=data.index, dtype=float)
        
        # Calculate final bands with rules
        for i in range(len(data)):
            if i == 0:
                final_upper.iloc[i] = basic_upper.iloc[i]
                final_lower.iloc[i] = basic_lower.iloc[i]
            else:
                # Final Upper Band rule
                if (basic_upper.iloc[i] < final_upper.iloc[i-1] or 
                    close.iloc[i-1] > final_upper.iloc[i-1]):
                    final_upper.iloc[i] = basic_upper.iloc[i]
                else:
                    final_upper.iloc[i] = final_upper.iloc[i-1]
                
                # Final Lower Band rule
                if (basic_lower.iloc[i] > final_lower.iloc[i-1] or 
                    close.iloc[i-1] < final_lower.iloc[i-1]):
                    final_lower.iloc[i] = basic_lower.iloc[i]
                else:
                    final_lower.iloc[i] = final_lower.iloc[i-1]
        
        # Calculate Supertrend and Trend
        supertrend = pd.Series(index=data.index, dtype=float)
        trend = pd.Series(index=data.index, dtype=int)
        
        for i in range(len(data)):
            if i == 0:
                # Initialize first value
                if close.iloc[i] <= final_lower.iloc[i]:
                    supertrend.iloc[i] = final_upper.iloc[i]
                    trend.iloc[i] = -1  # Bearish
                else:
                    supertrend.iloc[i] = final_lower.iloc[i]
                    trend.iloc[i] = 1   # Bullish
            else:
                prev_supertrend = supertrend.iloc[i-1]
                prev_trend = trend.iloc[i-1]
                
                if (prev_trend == 1 and close.iloc[i] > final_lower.iloc[i]) or \
                   (prev_trend == -1 and close.iloc[i] > final_upper.iloc[i]):
                    supertrend.iloc[i] = final_lower.iloc[i]
                    trend.iloc[i] = 1
                elif (prev_trend == -1 and close.iloc[i] < final_upper.iloc[i]) or \
                     (prev_trend == 1 and close.iloc[i] < final_lower.iloc[i]):
                    supertrend.iloc[i] = final_upper.iloc[i]
                    trend.iloc[i] = -1
                else:
                    supertrend.iloc[i] = prev_supertrend
                    trend.iloc[i] = prev_trend
        
        result = pd.DataFrame({
            'supertrend': supertrend,
            'trend': trend
        }, index=data.index)
        
        logger.debug(f"Calculated Supertrend with ATR period {atr_period}, multiplier {multiplier}")
        return result
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA).
        
        Args:
            data: Price series
            period: Number of periods for EMA calculation
            
        Returns:
            pd.Series: EMA values
        """
        if period <= 0:
            raise ValueError("Period must be greater than 0")
        
        ema = data.ewm(span=period, adjust=False).mean()
        
        logger.debug(f"Calculated EMA with period {period}")
        return ema
    
    def calculate_volume_ma(self, volume_data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Volume Moving Average.
        
        Args:
            volume_data: Volume series
            period: Number of periods for moving average
            
        Returns:
            pd.Series: Volume MA values
        """
        if period <= 0:
            raise ValueError("Period must be greater than 0")
        
        volume_ma = volume_data.rolling(window=period).mean()
        
        logger.debug(f"Calculated Volume MA with period {period}")
        return volume_ma
    
    def calculate_normalized_atr(self, data: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate normalized ATR as percentage of closing price.
        
        Args:
            data: DataFrame with OHLC columns
            period: Period for ATR calculation
            
        Returns:
            pd.Series: Normalized ATR values as percentages
        """
        atr = self.calculate_atr(data, period)
        close = data['Close']
        
        # Normalize ATR as percentage
        normalized_atr = (atr / close) * 100
        
        logger.debug(f"Calculated normalized ATR with period {period}")
        return normalized_atr
    
    def get_percentile_threshold(self, data: pd.Series, percentile: float) -> float:
        """
        Calculate percentile threshold for a data series.
        
        Args:
            data: Data series
            percentile: Percentile value (e.g., 95 for 95th percentile)
            
        Returns:
            float: Percentile threshold value
        """
        valid_data = data.dropna()
        threshold = np.percentile(valid_data, percentile)
        
        logger.debug(f"Calculated {percentile}th percentile threshold: {threshold}")
        return threshold