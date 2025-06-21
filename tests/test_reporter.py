"""
Test suite for the Reporter module.

This module tests the console reporting functionality that generates
formatted performance comparison tables for baseline vs improved strategies.
"""

import unittest
from unittest.mock import patch
import pandas as pd
from io import StringIO
import sys

from src.reporter import Reporter


class TestReporter(unittest.TestCase):
    """Test cases for Reporter class functionality."""
    
    def setUp(self):
        """Set up test fixtures for Reporter tests."""
        self.reporter = Reporter()
        
        # Sample strategy results for testing
        self.sample_results = {
            'baseline_in_sample': {
                'win_rate': 0.65,
                'total_return': 0.125,
                'max_drawdown': 0.085,
                'profit_factor': 1.75,
                'total_trades': 45,
                'avg_return': 0.0028
            },
            'baseline_out_sample': {
                'win_rate': 0.62,
                'total_return': 0.098,
                'max_drawdown': 0.092,
                'profit_factor': 1.68,
                'total_trades': 18,
                'avg_return': 0.0054
            },
            'improved_in_sample': {
                'win_rate': 0.78,
                'total_return': 0.156,
                'max_drawdown': 0.065,
                'profit_factor': 2.15,
                'total_trades': 32,
                'avg_return': 0.0049
            },
            'improved_out_sample': {
                'win_rate': 0.82,
                'total_return': 0.142,
                'max_drawdown': 0.058,
                'profit_factor': 2.28,
                'total_trades': 14,
                'avg_return': 0.0101
            }
        }
    
    def test_initialization(self):
        """Test Reporter initialization."""
        self.assertIsInstance(self.reporter, Reporter)
    
    def test_format_percentage(self):
        """Test percentage formatting utility method."""
        # This test will fail initially - we need to implement this method
        result = self.reporter.format_percentage(0.1234)
        self.assertEqual(result, "12.34%")
        
        # Test edge cases
        self.assertEqual(self.reporter.format_percentage(0), "0.00%")
        self.assertEqual(self.reporter.format_percentage(1.0), "100.00%")
        self.assertEqual(self.reporter.format_percentage(0.001), "0.10%")
    
    def test_format_number(self):
        """Test number formatting utility method."""
        # This test will fail initially - we need to implement this method
        result = self.reporter.format_number(1.23456)  
        self.assertEqual(result, "1.235")
        
        # Test edge cases
        self.assertEqual(self.reporter.format_number(0), "0.000")
        self.assertEqual(self.reporter.format_number(10), "10.000")
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_strategy_comparison(self, mock_stdout):
        """Test printing strategy comparison table."""
        # This test will fail initially - we need to implement this method
        self.reporter.print_strategy_comparison(self.sample_results)
        
        output = mock_stdout.getvalue()
        
        # Check that output contains key elements
        self.assertIn("STRATEGY PERFORMANCE COMPARISON", output)
        self.assertIn("Baseline Strategy", output)
        self.assertIn("Improved Strategy", output)
        self.assertIn("In-Sample Results", output)
        self.assertIn("Out-of-Sample Results", output)
        self.assertIn("Win Rate", output)
        self.assertIn("Total Return", output)
        self.assertIn("82.00%", output)  # Expected improved out-sample win rate
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_header(self, mock_stdout):
        """Test header printing functionality."""
        # This test will fail initially - we need to implement this method
        self.reporter.print_header("TEST HEADER")
        
        output = mock_stdout.getvalue()
        self.assertIn("TEST HEADER", output)
        self.assertIn("=", output)  # Should have separator lines
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_section(self, mock_stdout):
        """Test section printing functionality."""
        # This test will fail initially - we need to implement this method
        self.reporter.print_section("Test Section")
        
        output = mock_stdout.getvalue()
        self.assertIn("Test Section", output)
        self.assertIn("-", output)  # Should have separator lines
    
    def test_generate_results_table(self):
        """Test results table generation."""
        # This test will fail initially - we need to implement this method
        table = self.reporter.generate_results_table(self.sample_results)
        
        self.assertIsInstance(table, str)
        self.assertIn("Win Rate", table)
        self.assertIn("Total Return", table)
        self.assertIn("82.00%", table)  # Improved out-sample win rate
    
    def test_error_handling_invalid_results(self):
        """Test error handling for invalid results data."""
        # This test will fail initially - we need to implement error handling
        with self.assertRaises(ValueError):
            self.reporter.print_strategy_comparison({})
        
        with self.assertRaises(ValueError):
            self.reporter.print_strategy_comparison(None)


if __name__ == '__main__':
    unittest.main()