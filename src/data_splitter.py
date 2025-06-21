"""Data splitting utilities for training/testing separation with bias prevention."""

import pandas as pd
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)


class DataSplitter:
    """
    Handles splitting of time series data into in-sample and out-of-sample periods.
    
    This class ensures proper chronological splitting to prevent lookahead bias
    in strategy optimization and backtesting.
    """
    
    def __init__(self, in_sample_ratio: float = 0.7):
        """
        Initialize DataSplitter.
        
        Args:
            in_sample_ratio: Fraction of data to use for in-sample period (0 < ratio < 1)
            
        Raises:
            ValueError: If in_sample_ratio is not between 0 and 1
        """
        if not 0 < in_sample_ratio < 1:
            raise ValueError("in_sample_ratio must be between 0 and 1")
        
        self.in_sample_ratio = in_sample_ratio
        self.out_of_sample_ratio = 1.0 - in_sample_ratio
        
        logger.info(f"DataSplitter initialized with {in_sample_ratio:.1%} in-sample, "
                   f"{self.out_of_sample_ratio:.1%} out-of-sample")
    
    def split_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data chronologically into in-sample and out-of-sample periods.
        
        Args:
            data: DataFrame with datetime index containing market data
            
        Returns:
            Tuple of (in_sample_data, out_of_sample_data)
            
        Raises:
            ValueError: If data is empty or has insufficient rows
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        if len(data) < 2:
            raise ValueError("Data must have at least 2 rows for splitting")
        
        # Calculate split point
        split_point = int(len(data) * self.in_sample_ratio)
        
        # Ensure we have at least 1 row in each split
        if split_point == 0:
            split_point = 1
        elif split_point == len(data):
            split_point = len(data) - 1
        
        # Split data chronologically
        in_sample_data = data.iloc[:split_point].copy()
        out_of_sample_data = data.iloc[split_point:].copy()
        
        logger.info(f"Data split: {len(in_sample_data)} in-sample rows, "
                   f"{len(out_of_sample_data)} out-of-sample rows")
        
        return in_sample_data, out_of_sample_data
    
    def get_split_info(self, original_data: pd.DataFrame, 
                      in_sample_data: pd.DataFrame, 
                      out_of_sample_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Get detailed information about the data split.
        
        Args:
            original_data: Original complete dataset
            in_sample_data: In-sample portion
            out_of_sample_data: Out-of-sample portion
            
        Returns:
            Dictionary containing split statistics and information
        """
        total_rows = len(original_data)
        in_sample_rows = len(in_sample_data)
        out_of_sample_rows = len(out_of_sample_data)
        
        in_sample_pct = (in_sample_rows / total_rows) * 100
        out_of_sample_pct = (out_of_sample_rows / total_rows) * 100
        
        # Get split date (last date of in-sample data)
        split_date = in_sample_data.index[-1] if not in_sample_data.empty else None
        
        info = {
            'total_rows': total_rows,
            'in_sample_rows': in_sample_rows,
            'out_of_sample_rows': out_of_sample_rows,
            'in_sample_percentage': round(in_sample_pct, 1),
            'out_of_sample_percentage': round(out_of_sample_pct, 1),
            'split_date': split_date,
            'in_sample_start': in_sample_data.index[0] if not in_sample_data.empty else None,
            'in_sample_end': in_sample_data.index[-1] if not in_sample_data.empty else None,
            'out_of_sample_start': out_of_sample_data.index[0] if not out_of_sample_data.empty else None,
            'out_of_sample_end': out_of_sample_data.index[-1] if not out_of_sample_data.empty else None
        }
        
        return info
    
    def validate_split_integrity(self, original_data: pd.DataFrame,
                                in_sample_data: pd.DataFrame,
                                out_of_sample_data: pd.DataFrame) -> None:
        """
        Validate that the split maintains data integrity.
        
        Args:
            original_data: Original complete dataset
            in_sample_data: In-sample portion
            out_of_sample_data: Out-of-sample portion
            
        Raises:
            ValueError: If split integrity checks fail
        """
        # Check total row count
        expected_total = len(in_sample_data) + len(out_of_sample_data)
        if len(original_data) != expected_total:
            raise ValueError(f"Split integrity check failed: original data has {len(original_data)} rows, "
                           f"but splits have {expected_total} rows total")
        
        # Check chronological order
        if not in_sample_data.empty and not out_of_sample_data.empty:
            if in_sample_data.index[-1] >= out_of_sample_data.index[0]:
                raise ValueError("Split integrity check failed: in-sample data overlaps with out-of-sample data")
        
        # Check column consistency
        if not in_sample_data.columns.equals(original_data.columns):
            raise ValueError("Split integrity check failed: in-sample data has different columns")
        
        if not out_of_sample_data.columns.equals(original_data.columns):
            raise ValueError("Split integrity check failed: out-of-sample data has different columns")
        
        logger.info("Split integrity validation passed")