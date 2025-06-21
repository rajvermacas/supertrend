# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a quantitative trading strategy development project focused on creating and optimizing a Supertrend-based trading system for the Nifty 50 index. The goal is to achieve an 80% win rate through a multi-filter approach that combines trend, volume, and volatility filters.

**Current Status:** Documentation phase complete, ready for implementation following the 5-stage development plan.

## Technology Stack

- **Python 3.x** with standard quant libraries
- **pandas** for data manipulation
- **yfinance** for market data sourcing (^NSEI ticker)
- **pandas-ta** for technical indicators
- **matplotlib/seaborn** for visualizations
- **pytest** for testing framework

## Project Architecture

### Planned Directory Structure
```
Supertrend/
├── main.py                 # Main orchestration script
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Dependencies
├── data/
│   └── nifty_hourly.csv   # Cached hourly market data
└── src/
    ├── __init__.py
    ├── data_loader.py     # Data download/caching with yfinance
    ├── strategy.py        # Strategy logic and multi-filter system
    └── backtester.py      # Core backtesting engine
```

### Key Components

**Data Management:**
- Yahoo Finance API integration for ^NSEI hourly data
- 730-day maximum period for hourly timeframes
- Local CSV caching with force_download option
- 70/30 in-sample/out-of-sample split for bias prevention

**Strategy System:**
- Baseline: Standard Supertrend (ATR=10, Multiplier=3)
- Improved: Multi-filter system with EMA(100), Volume MA(20), ATR volatility filter
- Grid search optimization for parameters

**Backtesting Engine:**
- Trade execution simulation with proper data flow
- Performance metrics calculation
- Equity curve generation

## Development Commands

**Note:** Project is in documentation phase - no build commands exist yet. When implementing:

```bash
# Setup (to be created)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Testing (to be implemented)
pytest tests/ -v
pytest tests/test_specific_module.py -v

# Run main application (to be created)
python main.py
```

## Development Guidelines

### Test-Driven Development
- Follow strict Red-Green-Refactor cycle
- Aim for 100% test coverage
- Mock external API calls (yfinance) in tests
- Comprehensive logging and exception handling required

### Risk Management & Bias Prevention
- **Critical:** Prevent lookahead bias in backtesting
- Maintain strict chronological data flow
- Use proper train/test splits for optimization
- Validate all technical indicators for timing accuracy

### Key Strategy Parameters
- **Baseline Supertrend:** ATR Period=10, Multiplier=3
- **Trend Filter:** 100-period EMA
- **Volume Filter:** 20-period Volume MA
- **Volatility Filter:** 14-period ATR with 95th percentile threshold
- **Optimization Range:** ATR Period (5-20), Multiplier (2.0-5.0)

### Data Specifications
- **Timeframe:** Hourly data only
- **Symbol:** ^NSEI (Nifty 50 Index)
- **Period:** 730 days maximum
- **Validation:** Check for gaps, missing data, and market hours

## 5-Stage Implementation Plan

1. **Foundation & Data Management** - Setup project structure, data pipeline
2. **Technical Indicators** - Implement Supertrend and filter components
3. **Core Backtesting Engine** - Build trade execution and performance tracking
4. **Strategy Implementation** - Integrate baseline and improved strategies
5. **Reporting & Visualization** - Generate equity curves and performance reports

## Output Requirements

**Console Output:** Formatted comparison tables showing baseline vs improved strategy performance
**Files to Generate:**
- `equity_curve.png` - Portfolio growth visualization
- `trade_executions.png` - Price chart with trade entry/exit markers
- `results.md` - Automated performance documentation

## Critical Implementation Notes

- All timestamps must be handled properly for Indian market hours
- Supertrend calculation requires correct ATR and price data alignment
- Volume filters need proper normalization and validation
- Performance metrics should include win rate, drawdown, Sharpe ratio
- Grid search optimization must use walk-forward analysis to prevent overfitting