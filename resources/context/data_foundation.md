# Data Foundation Strategy for Supertrend Backtesting

This document outlines the agreed-upon strategy for sourcing and preparing the data for the Supertrend backtesting project.

## 1. Data Source
- **Library**: We will use the `yfinance` Python library to fetch historical market data.

## 2. Asset & Ticker
- **Asset**: Nifty 50 Index.
- **Ticker**: The data will be fetched using the Yahoo Finance ticker `^NSEI`.

## 3. Time Period & Granularity
- **Granularity**: We will use **hourly (`1h`)** data for our analysis.
- **Historical Period**: Due to `yfinance` limitations for hourly data, we will fetch the maximum available history, which is approximately **2 years (730 days)**.

## 4. Data Handling Process
1.  **Download**: Fetch the data using the specified ticker and interval.
2.  **Validation**: Perform a basic data integrity check to handle any missing values (e.g., `NaN`s).
3.  **Caching**: To improve performance and avoid redundant API calls, the downloaded data will be saved to a local file (e.g., a CSV). Subsequent runs of the script will load data from this local cache.
