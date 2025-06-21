"""
Test suite for the Visualizer module.

This module tests the visualization functionality that generates
equity curves and trade execution charts for strategy analysis.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import os
from pathlib import Path

from src.visualizer import Visualizer


class TestVisualizer(unittest.TestCase):
    """Test cases for Visualizer class functionality."""
    
    def setUp(self):
        """Set up test fixtures for Visualizer tests."""
        self.visualizer = Visualizer()
        
        # Sample data for testing
        dates = pd.date_range('2023-01-01', periods=100, freq='h')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(19000, 20000, 100),
            'High': np.random.uniform(19500, 20500, 100),
            'Low': np.random.uniform(18500, 19500, 100),
            'Close': np.random.uniform(19000, 20000, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        }, index=dates)
        
        # Sample equity curves
        self.sample_equity = {
            'baseline': pd.Series([100000, 102000, 101500, 103000, 102800], 
                                 index=dates[:5]),
            'improved': pd.Series([100000, 101800, 102500, 104500, 105200], 
                                 index=dates[:5])
        }
        
        # Sample trades
        self.sample_trades = [
            {'entry_datetime': dates[10], 'entry_price': 19200, 
             'exit_datetime': dates[15], 'exit_price': 19400, 'direction': 'LONG'},
            {'entry_datetime': dates[20], 'entry_price': 19600, 
             'exit_datetime': dates[25], 'exit_price': 19300, 'direction': 'SHORT'},
            {'entry_datetime': dates[30], 'entry_price': 19100, 
             'exit_datetime': dates[35], 'exit_price': 19500, 'direction': 'LONG'}
        ]
    
    def test_initialization(self):
        """Test Visualizer initialization."""
        self.assertIsInstance(self.visualizer, Visualizer)
    
    def test_initialization_with_custom_style(self):
        """Test Visualizer initialization with custom style."""
        # This test will fail initially - we need to implement style parameter
        custom_visualizer = Visualizer(style='seaborn')
        self.assertIsInstance(custom_visualizer, Visualizer)
        self.assertEqual(custom_visualizer.style, 'seaborn')
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_equity_curve(self, mock_show, mock_savefig):
        """Test equity curve creation."""
        # This test will fail initially - we need to implement this method
        output_path = 'test_equity_curve.png'
        
        self.visualizer.create_equity_curve(
            equity_curves=self.sample_equity,
            output_path=output_path
        )
        
        # Check that savefig was called with correct path
        mock_savefig.assert_called_once()
        call_args = mock_savefig.call_args[0]
        self.assertEqual(call_args[0], output_path)
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_trade_execution_chart(self, mock_show, mock_savefig):
        """Test trade execution chart creation."""
        # This test will fail initially - we need to implement this method
        output_path = 'test_trade_chart.png'
        
        self.visualizer.create_trade_execution_chart(
            price_data=self.sample_data,
            trades=self.sample_trades,
            output_path=output_path
        )
        
        # Check that savefig was called with correct path
        mock_savefig.assert_called_once()
        call_args = mock_savefig.call_args[0]
        self.assertEqual(call_args[0], output_path)
    
    def test_setup_plot_style(self):
        """Test plot style setup."""
        # This test will fail initially - we need to implement this method
        self.visualizer.setup_plot_style()
        # Just test that method exists and runs without error
    
    def test_format_price_axis(self):
        """Test price axis formatting utility."""
        # This test will fail initially - we need to implement this method
        mock_ax = MagicMock()
        self.visualizer.format_price_axis(mock_ax)
        # Test that formatting methods were called
        mock_ax.yaxis.set_major_formatter.assert_called_once()
    
    def test_add_trade_markers(self):
        """Test adding trade entry/exit markers to chart."""
        # This test will fail initially - we need to implement this method
        mock_ax = MagicMock()
        
        self.visualizer.add_trade_markers(
            ax=mock_ax,
            trades=self.sample_trades,
            price_data=self.sample_data
        )
        
        # Check that scatter plot was called for markers
        self.assertTrue(mock_ax.scatter.called)
    
    def test_save_chart(self):
        """Test chart saving functionality."""
        # This test will fail initially - we need to implement this method
        test_path = 'test_output.png'
        mock_fig = MagicMock()
        
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            self.visualizer.save_chart(mock_fig, test_path)
            mock_savefig.assert_called_once_with(
                test_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none'
            )
    
    def test_error_handling_invalid_data(self):
        """Test error handling for invalid data."""
        # This test will fail initially - we need to implement error handling
        with self.assertRaises(ValueError):
            self.visualizer.create_equity_curve({}, 'test.png')
        
        with self.assertRaises(ValueError):
            self.visualizer.create_trade_execution_chart(
                pd.DataFrame(), [], 'test.png'
            )
    
    def test_error_handling_invalid_path(self):
        """Test error handling for invalid output paths."""
        # This test will fail initially - we need to implement error handling
        with self.assertRaises(ValueError):
            self.visualizer.create_equity_curve(self.sample_equity, '')
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_equity_curve_with_titles(self, mock_show, mock_savefig):
        """Test equity curve creation with custom titles."""
        # This test will fail initially - we need to implement title parameter
        self.visualizer.create_equity_curve(
            equity_curves=self.sample_equity,
            output_path='test.png',
            title='Custom Strategy Comparison',
            xlabel='Trading Days',
            ylabel='Portfolio Value (₹)'
        )
        
        mock_savefig.assert_called_once()
    
    def test_create_directory_if_not_exists(self):
        """Test automatic directory creation for output paths."""
        # This test will fail initially - we need to implement directory creation
        test_path = 'test_dir/subdir/chart.png'
        
        with patch('os.makedirs') as mock_makedirs:
            with patch('matplotlib.pyplot.savefig'):
                with patch('matplotlib.pyplot.show'):
                    self.visualizer.create_equity_curve(
                        self.sample_equity, test_path
                    )
                    # Should create directory structure
                    mock_makedirs.assert_called()


if __name__ == '__main__':
    unittest.main()