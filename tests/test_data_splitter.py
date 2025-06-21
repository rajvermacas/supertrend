"""Test suite for data splitting functionality."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.data_splitter import DataSplitter


class TestDataSplitter:
    """Test cases for DataSplitter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create sample data with 100 rows
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='h')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(100, 200, 100),
            'High': np.random.uniform(150, 250, 100),
            'Low': np.random.uniform(50, 150, 100),
            'Close': np.random.uniform(100, 200, 100),
            'Volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        self.splitter = DataSplitter()
    
    def test_initialization(self):
        """Test DataSplitter initialization."""
        splitter = DataSplitter()
        assert splitter.in_sample_ratio == 0.7
        assert abs(splitter.out_of_sample_ratio - 0.3) < 1e-10
        
        # Test custom ratios
        custom_splitter = DataSplitter(in_sample_ratio=0.8)
        assert custom_splitter.in_sample_ratio == 0.8
        assert abs(custom_splitter.out_of_sample_ratio - 0.2) < 1e-10
    
    def test_invalid_ratio(self):
        """Test initialization with invalid ratios."""
        with pytest.raises(ValueError, match="in_sample_ratio must be between 0 and 1"):
            DataSplitter(in_sample_ratio=1.5)
        
        with pytest.raises(ValueError, match="in_sample_ratio must be between 0 and 1"):
            DataSplitter(in_sample_ratio=-0.1)
    
    def test_split_data_basic(self):
        """Test basic data splitting functionality."""
        in_sample, out_of_sample = self.splitter.split_data(self.sample_data)
        
        # Check data types
        assert isinstance(in_sample, pd.DataFrame)
        assert isinstance(out_of_sample, pd.DataFrame)
        
        # Check split ratios (70/30)
        expected_in_sample_size = int(len(self.sample_data) * 0.7)
        expected_out_of_sample_size = len(self.sample_data) - expected_in_sample_size
        
        assert len(in_sample) == expected_in_sample_size
        assert len(out_of_sample) == expected_out_of_sample_size
        
        # Check column names are preserved
        assert list(in_sample.columns) == list(self.sample_data.columns)
        assert list(out_of_sample.columns) == list(self.sample_data.columns)
    
    def test_split_data_chronological_order(self):
        """Test that data is split in chronological order."""
        in_sample, out_of_sample = self.splitter.split_data(self.sample_data)
        
        # In-sample data should come first chronologically
        assert in_sample.index.max() <= out_of_sample.index.min()
        
        # Check that in-sample data is the first 70% of rows
        expected_split_point = int(len(self.sample_data) * 0.7)
        expected_in_sample = self.sample_data.iloc[:expected_split_point]
        expected_out_of_sample = self.sample_data.iloc[expected_split_point:]
        
        pd.testing.assert_frame_equal(in_sample, expected_in_sample)
        pd.testing.assert_frame_equal(out_of_sample, expected_out_of_sample)
    
    def test_split_data_custom_ratio(self):
        """Test data splitting with custom ratio."""
        custom_splitter = DataSplitter(in_sample_ratio=0.8)
        in_sample, out_of_sample = custom_splitter.split_data(self.sample_data)
        
        expected_in_sample_size = int(len(self.sample_data) * 0.8)
        expected_out_of_sample_size = len(self.sample_data) - expected_in_sample_size
        
        assert len(in_sample) == expected_in_sample_size
        assert len(out_of_sample) == expected_out_of_sample_size
    
    def test_split_data_empty_dataframe(self):
        """Test splitting empty dataframe."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Data cannot be empty"):
            self.splitter.split_data(empty_df)
    
    def test_split_data_single_row(self):
        """Test splitting dataframe with single row."""
        single_row_df = self.sample_data.iloc[:1]
        
        with pytest.raises(ValueError, match="Data must have at least 2 rows"):
            self.splitter.split_data(single_row_df)
    
    def test_split_data_very_small_dataset(self):
        """Test splitting with very small dataset."""
        small_df = self.sample_data.iloc[:3]  # 3 rows
        in_sample, out_of_sample = self.splitter.split_data(small_df)
        
        # With 3 rows and 70% split: 3 * 0.7 = 2.1 -> 2 rows in-sample, 1 out-of-sample
        assert len(in_sample) == 2
        assert len(out_of_sample) == 1
    
    def test_get_split_info(self):
        """Test getting split information."""
        in_sample, out_of_sample = self.splitter.split_data(self.sample_data)
        info = self.splitter.get_split_info(self.sample_data, in_sample, out_of_sample)
        
        assert isinstance(info, dict)
        assert 'total_rows' in info
        assert 'in_sample_rows' in info
        assert 'out_of_sample_rows' in info
        assert 'in_sample_percentage' in info
        assert 'out_of_sample_percentage' in info
        assert 'split_date' in info
        
        assert info['total_rows'] == len(self.sample_data)
        assert info['in_sample_rows'] == len(in_sample)
        assert info['out_of_sample_rows'] == len(out_of_sample)
        assert abs(info['in_sample_percentage'] - 70.0) < 1.0  # Allow for rounding
        assert abs(info['out_of_sample_percentage'] - 30.0) < 1.0  # Allow for rounding
    
    def test_validate_split_integrity(self):
        """Test split integrity validation."""
        in_sample, out_of_sample = self.splitter.split_data(self.sample_data)
        
        # This should not raise an exception
        self.splitter.validate_split_integrity(self.sample_data, in_sample, out_of_sample)
        
        # Test with corrupted data - should raise exception
        corrupted_in_sample = in_sample.iloc[:-1]  # Remove last row
        
        with pytest.raises(ValueError, match="Split integrity check failed"):
            self.splitter.validate_split_integrity(self.sample_data, corrupted_in_sample, out_of_sample)