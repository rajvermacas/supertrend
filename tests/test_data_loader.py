"""
Tests for data_loader module
Following TDD approach - RED phase: Write failing tests first
"""

import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
from src.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.data_loader = DataLoader()
        self.test_cache_file = "test_nifty_hourly.csv"
        
    def teardown_method(self):
        """Cleanup test files"""
        if os.path.exists(self.test_cache_file):
            os.remove(self.test_cache_file)
    
    def test_data_loader_initialization(self):
        """Test DataLoader can be initialized"""
        loader = DataLoader()
        assert loader is not None
        assert hasattr(loader, 'ticker')
        assert loader.ticker == '^NSEI'
        assert hasattr(loader, 'period')
        assert loader.period == '730d'
        assert hasattr(loader, 'interval')
        assert loader.interval == '1h'
        
    def test_data_loader_custom_parameters(self):
        """Test DataLoader with custom parameters"""
        loader = DataLoader(ticker='TEST', period='365d', interval='1d')
        assert loader.ticker == 'TEST'
        assert loader.period == '365d'
        assert loader.interval == '1d'
    
    @patch('yfinance.download')
    def test_download_data_success(self, mock_download):
        """Test successful data download from yfinance"""
        # Mock yfinance response
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000, 1100, 1200],
            'Dividends': [0.0, 0.0, 0.0],
            'Stock Splits': [0.0, 0.0, 0.0]
        })
        mock_download.return_value = mock_data
        
        result = self.data_loader.download_data()
        
        # Verify yfinance was called with correct parameters
        mock_download.assert_called_once_with(
            tickers='^NSEI',
            period='730d',
            interval='1h'
        )
        
        # Verify data structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'Dividends' not in result.columns
        assert 'Stock Splits' not in result.columns
        assert all(col in result.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])

    @patch('yfinance.download')
    def test_download_data_multilevel_columns(self, mock_download):
        """Test successful data download with multi-level columns"""
        # Create multi-level columns as yfinance sometimes returns
        arrays = [
            ['Open', 'High', 'Low', 'Close', 'Volume'],
            ['^NSEI', '^NSEI', '^NSEI', '^NSEI', '^NSEI']
        ]
        multi_index = pd.MultiIndex.from_arrays(arrays)
        
        mock_data = pd.DataFrame({
            ('Open', '^NSEI'): [100.0, 101.0, 102.0],
            ('High', '^NSEI'): [105.0, 106.0, 107.0],
            ('Low', '^NSEI'): [99.0, 100.0, 101.0],
            ('Close', '^NSEI'): [104.0, 105.0, 106.0],
            ('Volume', '^NSEI'): [1000, 1100, 1200]
        })
        mock_data.columns = multi_index
        mock_download.return_value = mock_data
        
        result = self.data_loader.download_data()
        
        # Verify data structure - columns should be flattened
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert not isinstance(result.columns, pd.MultiIndex)
        assert all(col in result.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    
    @patch('yfinance.download')
    def test_download_data_failure(self, mock_download):
        """Test handling of yfinance download failure"""
        mock_download.side_effect = Exception("Network error")
        
        with pytest.raises(Exception) as exc_info:
            self.data_loader.download_data()
        
        assert "Failed to download data" in str(exc_info.value)
    
    def test_validate_data_valid(self):
        """Test data validation with valid data"""
        valid_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0],
            'Close': [104.0, 105.0],
            'Volume': [1000, 1100]
        })
        
        # Should not raise any exception
        result = self.data_loader.validate_data(valid_data)
        assert result is True
    
    def test_validate_data_missing_columns(self):
        """Test data validation with missing required columns"""
        invalid_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0]
            # Missing Close and Volume
        })
        
        with pytest.raises(ValueError) as exc_info:
            self.data_loader.validate_data(invalid_data)
        
        assert "Missing required columns" in str(exc_info.value)
    
    def test_validate_data_empty_dataframe(self):
        """Test data validation with empty DataFrame"""
        empty_data = pd.DataFrame()
        
        with pytest.raises(ValueError) as exc_info:
            self.data_loader.validate_data(empty_data)
        
        assert "Data is empty" in str(exc_info.value)
    
    def test_validate_data_missing_values(self):
        """Test data validation with missing values"""
        data_with_nan = pd.DataFrame({
            'Open': [100.0, None],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0],
            'Close': [104.0, 105.0],
            'Volume': [1000, 1100]
        })
        
        with pytest.raises(ValueError) as exc_info:
            self.data_loader.validate_data(data_with_nan)
        
        assert "Data contains missing values" in str(exc_info.value)
    
    def test_save_to_cache(self):
        """Test saving data to cache file"""
        test_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0],
            'Close': [104.0, 105.0],
            'Volume': [1000, 1100]
        })
        
        self.data_loader.save_to_cache(test_data, self.test_cache_file)
        
        # Verify file was created
        assert os.path.exists(self.test_cache_file)
        
        # Verify data can be loaded back
        loaded_data = pd.read_csv(self.test_cache_file, index_col=0, parse_dates=True)
        pd.testing.assert_frame_equal(test_data, loaded_data)
    
    def test_load_from_cache_exists(self):
        """Test loading data from existing cache file"""
        # Create test cache file
        test_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0],
            'Close': [104.0, 105.0],
            'Volume': [1000, 1100]
        })
        test_data.to_csv(self.test_cache_file)
        
        result = self.data_loader.load_from_cache(self.test_cache_file)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert all(col in result.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    
    def test_load_from_cache_not_exists(self):
        """Test loading data from non-existent cache file"""
        result = self.data_loader.load_from_cache("nonexistent_file.csv")
        assert result is None
    
    @patch('src.data_loader.DataLoader.download_data')
    def test_get_data_force_download(self, mock_download):
        """Test get_data with force_download=True"""
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0],
            'Close': [104.0, 105.0],
            'Volume': [1000, 1100]
        })
        mock_download.return_value = mock_data
        
        result = self.data_loader.get_data(force_download=True)
        
        mock_download.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    def test_get_data_from_cache(self):
        """Test get_data loading from cache when available"""
        # Create test cache file
        test_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0],
            'Close': [104.0, 105.0],
            'Volume': [1000, 1100]
        })
        test_data.to_csv("data/nifty_hourly.csv")
        
        try:
            with patch('src.data_loader.DataLoader.download_data') as mock_download:
                result = self.data_loader.get_data(force_download=False)
                
                # Should not call download_data when cache exists
                mock_download.assert_not_called()
                assert isinstance(result, pd.DataFrame)
        finally:
            # Cleanup
            if os.path.exists("data/nifty_hourly.csv"):
                os.remove("data/nifty_hourly.csv")