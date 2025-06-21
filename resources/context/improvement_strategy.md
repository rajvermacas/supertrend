# Strategy Improvement and Optimization Plan

This document outlines the multi-stage plan to improve the win rate of the baseline Supertrend strategy. The approach is to layer several complementary filters, each analyzing the market from a different perspective (Trend, Volume, Volatility). This plan includes a strict process to prevent lookahead bias.

## 1. The Core Principle: Preventing Lookahead Bias

To ensure results are robust and trustworthy, we will use an **In-Sample / Out-of-Sample** data split.

- **In-Sample Data (First ~70%)**: This partition is used for training and optimizing all strategy parameters.
- **Out-of-Sample Data (Last ~30%)**: This "unseen" data is used for the final test to generate our true performance report.

## 2. Stage 1: Parameter Optimization (On In-Sample Data)

The first step is to find the optimal parameters for the core Supertrend indicator and its filters.

- **Action**: Systematically test parameters on the **in-sample data only** to find the combination with the highest win rate.
  - **Supertrend ATR Period**: `5` to `20`.
  - **Supertrend Multiplier**: `2.0` to `5.0`.

## 3. Stage 2: The Multi-Filter System

We will apply a series of filters in sequence. A signal must pass all filters to be considered valid.

### Filter 1: Trend Confirmation
- **Indicator**: **100-period Exponential Moving Average (EMA)**.
- **Purpose**: To ensure we only trade in the direction of the dominant medium-term trend.
- **Rule**:
  - **Buy Signal**: Must have `Close > 100 EMA`.
  - **Sell Signal**: Must have `Close < 100 EMA`.

### Filter 2: Volume Confirmation
- **Indicator**: **20-period Simple Moving Average of Volume (Volume MA)**.
- **Purpose**: To ensure there is market conviction behind the signal.
- **Rule**: A signal is only valid if the `Volume` on the signal candle is **greater than its 20-period Volume MA**.

### Filter 3: Volatility Regime Filter
- **Indicator**: **14-period Average True Range (ATR)**, normalized as a percentage of the closing price `(ATR / Close) * 100`.
- **Purpose**: To avoid taking signals during periods of extreme, unpredictable volatility.
- **Rule**: 
  1. Calculate the 95th percentile of this ATR percentage value across the **in-sample data**.
  2. During backtesting, **ignore any signal** where the current ATR percentage exceeds this pre-calculated threshold.

## 4. Final Validation

The complete, multi-filter strategy (using the single best parameter set found in Stage 1) will be run once on the **out-of-sample data**. The win rate, P/L, and drawdown from this final run will be our official performance result.
