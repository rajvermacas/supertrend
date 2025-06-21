# Baseline Supertrend Strategy

This document defines the initial "vanilla" Supertrend strategy that will serve as our performance benchmark. The goal is to measure the win rate of this baseline strategy before attempting any optimizations.

## 1. Indicator and Parameters
- **Indicator**: Standard Supertrend.
- **ATR Period**: `10`. This is the lookback period for the Average True Range (ATR) calculation.
- **Multiplier**: `3`. This factor is multiplied by the ATR to determine the offset of the Supertrend bands.

These are common, industry-standard default values for the Supertrend indicator.

## 2. Trading Logic
The strategy will generate signals based on the crossover between the closing price and the Supertrend line.

- **Buy Signal**: A buy signal is generated when the Supertrend indicator flips from being **above** the closing price to **below** it. This indicates a potential shift to an uptrend.
- **Sell Signal**: A sell signal is generated when the Supertrend indicator flips from being **below** the closing price to **above** it. This indicates a potential shift to a downtrend.

## 3. Implementation
- **Library**: To ensure an accurate and efficient calculation of the Supertrend indicator, we will use a well-tested technical analysis library, such as `pandas-ta`. This allows us to focus on the strategy's logic rather than the indicator's mathematical implementation.
