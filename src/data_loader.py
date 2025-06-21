"""
Data Loader Module for Supertrend Strategy
Handles downloading, caching, and validation of market data
"""

import pandas as pd
import yfinance as yf
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    DataLoader class for downloading and managing market data from Yahoo Finance
    
    This class provides functionality to:
    - Download hourly market data for Nifty 50 index
    - Cache data locally to avoid redundant API calls
    - Validate data integrity
    - Handle force download option
    """
    
    def __init__(self, ticker: str = '^NSEI', period: str = '730d', interval: str = '1h'):
        """
        Initialize DataLoader with default parameters for Nifty 50
        
        Args:
            ticker (str): Yahoo Finance ticker symbol (default: ^NSEI for Nifty 50)
            period (str): Time period for data download (default: 730d)
            interval (str): Data interval (default: 1h for hourly data)
        """
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.cache_file = "data/nifty_hourly.csv"
        
        logger.info(f"DataLoader initialized: ticker={ticker}, period={period}, interval={interval}")
    
    def download_data(self) -> pd.DataFrame:
        """
        Download data from Yahoo Finance using yfinance
        
        Returns:
            pd.DataFrame: Downloaded market data with cleaned columns
            
        Raises:
            Exception: If data download fails
        """
        try:
            logger.info(f"Downloading data for {self.ticker}...")
            
            # Download data using yfinance
            data = yf.download(
                tickers=self.ticker,
                period=self.period,
                interval=self.interval
            )
            
            if data.empty:
                raise Exception(f"No data received for {self.ticker}")
            
            # Flatten multi-level columns if they exist
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Remove unnecessary columns
            columns_to_remove = ['Dividends', 'Stock Splits']
            for col in columns_to_remove:
                if col in data.columns:
                    data = data.drop(columns=[col])
            
            logger.info(f"Successfully downloaded {len(data)} rows of data")
            return data
            
        except Exception as e:
            logger.error(f"Failed to download data: {str(e)}")
            raise Exception(f"Failed to download data for {self.ticker}: {str(e)}")
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate downloaded data for completeness and integrity
        
        Args:
            data (pd.DataFrame): Data to validate
            
        Returns:
            bool: True if data is valid
            
        Raises:
            ValueError: If data validation fails
        """
        # Check if data is empty
        if data.empty:
            raise ValueError("Data is empty")
        
        # Check for required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for missing values
        if data.isnull().any().any():
            raise ValueError("Data contains missing values")
        
        logger.info("Data validation passed")
        return True
    
    def save_to_cache(self, data: pd.DataFrame, cache_file: str = None) -> None:
        """
        Save data to cache file
        
        Args:
            data (pd.DataFrame): Data to save
            cache_file (str, optional): Cache file path. Uses default if None
        """
        if cache_file is None:
            cache_file = self.cache_file
        
        # Ensure directory exists (only if there's a directory component)
        dir_path = os.path.dirname(cache_file)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Save to CSV
        data.to_csv(cache_file)
        logger.info(f"Data saved to cache: {cache_file}")
    
    def load_from_cache(self, cache_file: str = None) -> Optional[pd.DataFrame]:
        """
        Load data from cache file if it exists
        
        Args:
            cache_file (str, optional): Cache file path. Uses default if None
            
        Returns:
            pd.DataFrame or None: Cached data if file exists, None otherwise
        """
        if cache_file is None:
            cache_file = self.cache_file
        
        if os.path.exists(cache_file):
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                logger.info(f"Data loaded from cache: {cache_file}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_file}: {str(e)}")
                return None
        
        logger.info(f"Cache file not found: {cache_file}")
        return None
    
    def get_data(self, force_download: bool = False) -> pd.DataFrame:
        """
        Get market data, either from cache or by downloading
        
        Args:
            force_download (bool): If True, bypass cache and download fresh data
            
        Returns:
            pd.DataFrame: Market data
        """
        # If force download is requested, bypass cache
        if force_download:
            logger.info("Force download requested, bypassing cache")
            data = self.download_data()
            self.validate_data(data)
            self.save_to_cache(data)
            return data
        
        # Try to load from cache first
        cached_data = self.load_from_cache()
        if cached_data is not None:
            self.validate_data(cached_data)
            return cached_data
        
        # If no cache available, download fresh data
        logger.info("No cache available, downloading fresh data")
        data = self.download_data()
        self.validate_data(data)
        self.save_to_cache(data)
        return data