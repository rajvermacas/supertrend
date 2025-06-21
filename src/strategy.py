"""
Strategy Module for Supertrend Trading System.

This module implements the baseline and improved Supertrend trading strategies
with multiple filter components including trend, volume, and volatility filters.

Classes:
    StrategyEngine: Main class for strategy signal generation and filtering
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Union

from .indicators import TechnicalIndicators

# Configure logging
logger = logging.getLogger(__name__)


class StrategyEngine:
    """
    Strategy Engine for Supertrend-based trading signals.
    
    This class implements both baseline and improved Supertrend strategies
    with comprehensive filtering systems for enhanced signal quality.
    """
    
    def __init__(self):
        """Initialize StrategyEngine with technical indicators."""
        self.indicators = TechnicalIndicators()
        logger.info("StrategyEngine initialized")
    
    def generate_baseline_signals(self, data: pd.DataFrame, atr_period: int, 
                                multiplier: float) -> pd.DataFrame:
        """
        Generate baseline Supertrend signals without filters.
        
        Args:
            data: OHLCV DataFrame
            atr_period: Period for ATR calculation
            multiplier: Multiplier for Supertrend calculation
            
        Returns:
            pd.DataFrame: DataFrame with signals, supertrend, and trend columns
            
        Raises:
            ValueError: If parameters are invalid
        """
        if atr_period <= 0:
            raise ValueError("ATR period must be greater than 0")
        if multiplier <= 0:
            raise ValueError("Multiplier must be greater than 0")
        
        if len(data) == 0:
            raise ValueError("Data cannot be empty")
        
        # Calculate Supertrend
        supertrend_data = self.indicators.calculate_supertrend(
            data, atr_period, multiplier
        )
        
        # Initialize signals DataFrame
        signals = pd.DataFrame(index=data.index)
        signals['supertrend'] = supertrend_data['supertrend']
        signals['trend'] = supertrend_data['trend']
        signals['signal'] = 0  # Initialize all signals to 0 (HOLD)
        
        # Generate signals based on trend changes
        prev_trend = None
        for i in range(len(signals)):
            current_trend = signals['trend'].iloc[i]
            
            if pd.notna(current_trend) and prev_trend is not None:
                # BUY signal: trend changes from bearish (-1) to bullish (1)
                if prev_trend == -1 and current_trend == 1:
                    signals['signal'].iloc[i] = 1
                # SELL signal: trend changes from bullish (1) to bearish (-1)
                elif prev_trend == 1 and current_trend == -1:
                    signals['signal'].iloc[i] = -1
            
            if pd.notna(current_trend):
                prev_trend = current_trend
        
        logger.debug(f"Generated baseline signals with ATR period {atr_period}, multiplier {multiplier}")
        return signals
    
    def apply_trend_filter(self, data: pd.DataFrame, signals: pd.DataFrame, 
                          ema_period: int) -> pd.DataFrame:
        """
        Apply trend filter using EMA.
        
        Args:
            data: OHLCV DataFrame
            signals: Signals DataFrame from previous step
            ema_period: Period for EMA calculation
            
        Returns:
            pd.DataFrame: Filtered signals with EMA column
        """
        if ema_period <= 0:
            raise ValueError("EMA period must be greater than 0")
        
        # Calculate EMA
        ema = self.indicators.calculate_ema(data['Close'], ema_period)
        
        # Copy signals and add EMA
        filtered_signals = signals.copy()
        filtered_signals[f'ema_{ema_period}'] = ema
        
        # Apply trend filter
        for i in range(len(filtered_signals)):
            current_signal = filtered_signals['signal'].iloc[i]
            
            if current_signal != 0 and pd.notna(ema.iloc[i]):
                close_price = data['Close'].iloc[i]
                ema_value = ema.iloc[i]
                
                # BUY signal: only valid if Close > EMA (uptrend)
                if current_signal == 1 and close_price <= ema_value:
                    filtered_signals['signal'].iloc[i] = 0
                
                # SELL signal: only valid if Close < EMA (downtrend)
                elif current_signal == -1 and close_price >= ema_value:
                    filtered_signals['signal'].iloc[i] = 0
        
        logger.debug(f"Applied trend filter with EMA period {ema_period}")
        return filtered_signals
    
    def apply_volume_filter(self, data: pd.DataFrame, signals: pd.DataFrame, 
                           volume_period: int) -> pd.DataFrame:
        """
        Apply volume filter using Volume MA.
        
        Args:
            data: OHLCV DataFrame
            signals: Signals DataFrame from previous step
            volume_period: Period for Volume MA calculation
            
        Returns:
            pd.DataFrame: Volume filtered signals with Volume MA column
        """
        if volume_period <= 0:
            raise ValueError("Volume period must be greater than 0")
        
        # Calculate Volume MA
        volume_ma = self.indicators.calculate_volume_ma(data['Volume'], volume_period)
        
        # Copy signals and add Volume MA
        filtered_signals = signals.copy()
        filtered_signals[f'volume_ma_{volume_period}'] = volume_ma
        
        # Apply volume filter
        for i in range(len(filtered_signals)):
            current_signal = filtered_signals['signal'].iloc[i]
            
            if current_signal != 0 and pd.notna(volume_ma.iloc[i]):
                current_volume = data['Volume'].iloc[i]
                volume_ma_value = volume_ma.iloc[i]
                
                # Signal only valid if current volume > volume MA
                if current_volume <= volume_ma_value:
                    filtered_signals['signal'].iloc[i] = 0
        
        logger.debug(f"Applied volume filter with Volume MA period {volume_period}")
        return filtered_signals
    
    def apply_volatility_filter(self, data: pd.DataFrame, signals: pd.DataFrame, 
                               atr_period: int, percentile: float) -> pd.DataFrame:
        """
        Apply volatility filter using normalized ATR.
        
        Args:
            data: OHLCV DataFrame
            signals: Signals DataFrame from previous step
            atr_period: Period for ATR calculation
            percentile: Percentile threshold for volatility filter
            
        Returns:
            pd.DataFrame: Volatility filtered signals with ATR columns
        """
        if atr_period <= 0:
            raise ValueError("ATR period must be greater than 0")
        if not (0 < percentile < 100):
            raise ValueError("Percentile must be between 0 and 100")
        
        # Calculate normalized ATR
        normalized_atr = self.indicators.calculate_normalized_atr(data, atr_period)
        
        # Calculate threshold
        threshold = self.indicators.get_percentile_threshold(normalized_atr, percentile)
        
        # Copy signals and add ATR columns
        filtered_signals = signals.copy()
        filtered_signals['normalized_atr'] = normalized_atr
        filtered_signals['atr_threshold'] = threshold
        
        # Apply volatility filter
        for i in range(len(filtered_signals)):
            current_signal = filtered_signals['signal'].iloc[i]
            
            if current_signal != 0 and pd.notna(normalized_atr.iloc[i]):
                current_atr = normalized_atr.iloc[i]
                
                # Signal ignored if ATR exceeds threshold (too volatile)
                if current_atr > threshold:
                    filtered_signals['signal'].iloc[i] = 0
        
        logger.debug(f"Applied volatility filter with ATR period {atr_period}, "
                    f"{percentile}th percentile threshold: {threshold:.2f}")
        return filtered_signals
    
    def generate_improved_signals(self, data: pd.DataFrame, atr_period: int,
                                multiplier: float, ema_period: int, volume_period: int,
                                volatility_period: int, volatility_percentile: float) -> pd.DataFrame:
        """
        Generate improved Supertrend signals with all filters applied.
        
        Args:
            data: OHLCV DataFrame
            atr_period: Period for Supertrend ATR calculation
            multiplier: Multiplier for Supertrend calculation
            ema_period: Period for EMA trend filter
            volume_period: Period for Volume MA filter
            volatility_period: Period for volatility ATR calculation
            volatility_percentile: Percentile threshold for volatility filter
            
        Returns:
            pd.DataFrame: DataFrame with improved signals and all indicators
        """
        # Step 1: Generate baseline signals
        baseline_signals = self.generate_baseline_signals(data, atr_period, multiplier)
        
        # Step 2: Apply trend filter
        trend_filtered = self.apply_trend_filter(data, baseline_signals, ema_period)
        
        # Step 3: Apply volume filter
        volume_filtered = self.apply_volume_filter(data, trend_filtered, volume_period)
        
        # Step 4: Apply volatility filter
        final_signals = self.apply_volatility_filter(
            data, volume_filtered, volatility_period, volatility_percentile
        )
        
        logger.info("Generated improved signals with all filters applied")
        return final_signals