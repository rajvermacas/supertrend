# Supertrend Strategy Optimization: Product Requirements Document (PRD)

**Version:** 1.0
**Date:** June 21, 2025
**Author:** Cascade & USER

## 1. Introduction & Project Vision

### 1.1. Project Goal
The primary objective of this project is to develop, backtest, and optimize a Supertrend-based trading strategy for the Nifty 50 index. The ultimate success criterion is to systematically improve the strategy's win rate to a target of **80% or higher** on recent, unseen historical data.

### 1.2. The Core Problem
The standard Supertrend indicator is a popular and effective tool for trend following. However, in its basic form, it is susceptible to generating frequent false signals ("whipsaws"), particularly in sideways, non-trending markets or during periods of high volatility. These false signals can significantly degrade profitability and reduce the overall win rate. This project aims to solve this problem by architecting a multi-filter system that layers complementary technical indicators on top of the baseline Supertrend. The goal of these filters is to confirm the validity of a signal, thereby filtering out low-probability trades and creating a more robust, reliable, and profitable trading model.

### 1.3. Scope of Work
The scope of this project is end-to-end, encompassing:
- **Data Acquisition & Management**: Sourcing, cleaning, and caching the required market data.
- **Strategy Definition**: Formally defining both a baseline "vanilla" strategy and an advanced, multi-filter strategy.
- **Rigorous Backtesting**: Building a backtesting engine to simulate strategy performance based on historical data.
- **Robust Optimization**: Systematically finding the best parameters for the strategy while strictly avoiding lookahead bias.
- **Comprehensive Reporting**: Generating clear, insightful reports, including console summaries, data visualizations, and final documentation.

## 2. System and Data Requirements
*(Reference: For a detailed breakdown of the data strategy, see `resources/context/data_foundation.md`)*

### 2.1. Technical Stack
- **Programming Language**: Python (Version 3.x)
- **Core Libraries**:
    - `pandas`: For data manipulation and analysis.
    - `yfinance`: For downloading historical market data from Yahoo Finance.
    - `pandas-ta`: For efficient calculation of technical indicators, including Supertrend.
    - `matplotlib` / `seaborn` (or similar): For generating visualizations.
- **Dependencies**: All required libraries will be listed in a `requirements.txt` file for easy environment setup.

### 2.2. Data Specification
- **Data Source**: Yahoo Finance API.
- **Asset**: Nifty 50 Index.
- **Ticker Symbol**: `^NSEI`.
- **Data Granularity**: **Hourly (`1h`)**.
- **Historical Period**: The system will fetch the maximum period allowed by the `yfinance` API for hourly data, which is **730 days** (approximately 2 years).
- **Data Caching Mechanism**: To ensure efficiency and avoid redundant API calls, downloaded data will be saved to a local CSV file (`data/nifty_hourly.csv`). The system will automatically load data from this cache on subsequent runs. A `force_download` option will be available to bypass the cache and fetch fresh data.
- **Data Integrity**: Upon initial download, the data will be cleaned by removing unnecessary columns (e.g., 'Dividends', 'Stock Splits') and checked for missing values.

## 3. Core Strategy Definitions
*(Reference: The baseline is detailed in `resources/context/baseline_strategy.md`. The full multi-filter system is detailed in `resources/context/improvement_strategy.md`)*

### 3.1. Baseline Strategy (The Benchmark)
- **Purpose**: To establish a performance benchmark. All improvements will be measured against this simple strategy.
- **Indicator**: Standard Supertrend.
- **Default Parameters**:
    - **ATR Period**: 10
    - **Multiplier**: 3
- **Trading Logic**: A simple "stop-and-reverse" system. A buy signal is generated when the Supertrend line flips from above the price to below it. A sell signal is generated when the line flips from below the price to above it.

### 3.2. Improved Strategy (The Multi-Filter System)
- **Purpose**: To systematically improve the win rate by adding layers of confirmation. A trade signal must pass **all** of the following filters in sequence to be considered valid.
- **Filter 1: Trend Confirmation ("Is the tide with us?")**
    - **Indicator**: **100-period Exponential Moving Average (EMA)**.
    - **Rule**: A Supertrend **buy signal** is valid only if `Close > 100 EMA`. A Supertrend **sell signal** is valid only if `Close < 100 EMA`.
- **Filter 2: Volume Confirmation ("Is there conviction behind the move?")**
    - **Indicator**: **20-period Simple Moving Average of Volume (Volume MA)**.
    - **Rule**: A signal is valid only if the `Volume` on the signal candle is **greater than its 20-period Volume MA**.
- **Filter 3: Volatility Regime Filter ("Is the market too chaotic?")**
    - **Indicator**: **14-period Average True Range (ATR)**, normalized as a percentage of the closing price: `((ATR / Close) * 100)`.
    - **Rule**: A signal is ignored if its corresponding normalized ATR value exceeds the **95th percentile** of historical values, calculated on the in-sample dataset.

## 4. Backtesting and Optimization Framework (Detailed)
*(Reference: The engine design is captured in `resources/context/backtesting_engine.md`. The optimization process and lookahead bias prevention are detailed in `resources/context/improvement_strategy.md`)*

### 4.1. The Backtesting Engine: Granular Mechanics
- **Core Simulation Loop**: The engine will iterate through the data row-by-row. For each candle, it checks its current position (`LONG`, `SHORT`) against the strategy's final signal (`BUY`, `SELL`) and executes trades on a stop-and-reverse basis at the `Close` price.
- **Trade Logging**: When a trade is closed, a detailed record is created, including entry/exit datetimes, entry/exit prices, direction, and P/L.
- **Performance Metric Calculation**:
    - **P/L per Trade**: Calculated as `((Exit Price - Entry Price) / Entry Price)` for longs and `((Entry Price - Exit Price) / Entry Price)` for shorts.
    - **Win Rate**: `(Number of profitable trades) / (Total trades)`.
    - **Equity Curve**: Tracks a hypothetical portfolio value, updated by the P/L of each closed trade.
    - **Maximum Drawdown**: Calculated as the largest percentage drop from a running peak in the equity curve.

### 4.2. Lookahead Bias Prevention: Strict Implementation
- **Data Splitting**: The main script will split the full dataset into `in_sample_data` (first 70%) and `out_of_sample_data` (last 30%).
- **Data Flow Discipline**: The `out_of_sample_data` DataFrame will **never** be passed to the optimization function. It is held back for one final validation run.

### 4.3. Parameter Optimization: The "Grid Search" Process
- **The Search Loop**: The optimization function will perform an exhaustive grid search by looping through every combination of `ATR Period` (5-20) and `Multiplier` (2.0-5.0). For each pair, it will run a full backtest on the **in-sample data**.
- **Identifying Optimal Parameters**: After the search is complete, the code will identify the single `(Period, Multiplier)` pair that produced the highest win rate in the results.
- **Final Validation Run**: The main script will execute **one final backtest** using the identified optimal parameters on the **out-of-sample data**. The results from this run are the official, honest performance metrics of the strategy.

## 5. Deliverables and Reporting
*(Reference: The design for all reports and visualizations is detailed in `resources/context/results_presentation.md`)*

### 5.1. Console Output
A formatted summary table will be printed to the console, comparing the performance metrics of the Baseline vs. Improved strategies, with clear sections for both In-Sample and Out-of-Sample results.

### 5.2. Visualizations
The script will automatically generate and save two key charts:
1.  **`equity_curve.png`**: An equity curve chart comparing the portfolio growth of the baseline and improved strategies.
2.  **`trade_executions.png`**: A price chart with markers for all buy and sell trades from the final strategy.

### 5.3. Documentation
All design decisions are captured in markdown files within `resources/context/`, culminating in this PRD. A final `results.md` file will be generated to summarize the findings.

## 6. Proposed Project Structure
To ensure modularity and maintainability, the project will adhere to the following directory structure:
```
Supertrend/
├── main.py                 # Main script to orchestrate the entire process
├── requirements.txt        # Project dependencies
├── data/
│   └── nifty_hourly.csv    # Cached data file
└── src/
    ├── __init__.py
    ├── data_loader.py      # Module for downloading and loading data
    ├── strategy.py         # Module defining the strategy logic and filters
    └── backtester.py       # Module for the core backtesting engine
```
