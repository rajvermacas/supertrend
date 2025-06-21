"""
Test suite for the DocGenerator module.

This module tests the automated documentation generation functionality
that creates results.md files with strategy analysis and findings.
"""

import unittest
from unittest.mock import patch, mock_open
import pandas as pd
import os
from datetime import datetime

from src.doc_generator import DocGenerator


class TestDocGenerator(unittest.TestCase):
    """Test cases for DocGenerator class functionality."""
    
    def setUp(self):
        """Set up test fixtures for DocGenerator tests."""
        self.doc_generator = DocGenerator()
        
        # Sample strategy results for testing
        self.sample_results = {
            'baseline_in_sample': {
                'win_rate': 0.65,
                'total_return': 0.125,
                'max_drawdown': 0.085,
                'profit_factor': 1.75,
                'total_trades': 45,
                'avg_return': 0.0028,
                'best_trade': 0.045,
                'worst_trade': -0.032
            },
            'baseline_out_sample': {
                'win_rate': 0.62,
                'total_return': 0.098,
                'max_drawdown': 0.092,
                'profit_factor': 1.68,
                'total_trades': 18,
                'avg_return': 0.0054,
                'best_trade': 0.038,
                'worst_trade': -0.028
            },
            'improved_in_sample': {
                'win_rate': 0.78,
                'total_return': 0.156,
                'max_drawdown': 0.065,
                'profit_factor': 2.15,
                'total_trades': 32,
                'avg_return': 0.0049,
                'best_trade': 0.052,
                'worst_trade': -0.018
            },
            'improved_out_sample': {
                'win_rate': 0.82,
                'total_return': 0.142,
                'max_drawdown': 0.058,
                'profit_factor': 2.28,
                'total_trades': 14,
                'avg_return': 0.0101,
                'best_trade': 0.048,
                'worst_trade': -0.015
            }
        }
        
        # Sample optimization results
        self.sample_optimization = {
            'best_parameters': {'atr_period': 12, 'multiplier': 2.5},
            'best_metric_value': 0.82,
            'optimization_metric': 'win_rate',
            'total_combinations_tested': 256
        }
    
    def test_initialization(self):
        """Test DocGenerator initialization."""
        self.assertIsInstance(self.doc_generator, DocGenerator)
    
    def test_format_markdown_percentage(self):
        """Test percentage formatting for markdown."""
        # This test will fail initially - we need to implement this method
        result = self.doc_generator.format_markdown_percentage(0.1234)
        self.assertEqual(result, "**12.34%**")
        
        # Test edge cases
        self.assertEqual(self.doc_generator.format_markdown_percentage(0), "**0.00%**")
        self.assertEqual(self.doc_generator.format_markdown_percentage(1.0), "**100.00%**")
    
    def test_format_markdown_number(self):
        """Test number formatting for markdown."""
        # This test will fail initially - we need to implement this method
        result = self.doc_generator.format_markdown_number(1.23456)
        self.assertEqual(result, "**1.235**")
    
    def test_generate_executive_summary(self):
        """Test executive summary generation."""
        # This test will fail initially - we need to implement this method
        summary = self.doc_generator.generate_executive_summary(self.sample_results)
        
        self.assertIsInstance(summary, str)
        self.assertIn("82.00%", summary)  # Improved out-sample win rate
        self.assertIn("Target Achievement", summary)
        self.assertIn("executive summary", summary.lower())
    
    def test_generate_performance_table(self):
        """Test performance comparison table generation."""
        # This test will fail initially - we need to implement this method
        table = self.doc_generator.generate_performance_table(self.sample_results)
        
        self.assertIsInstance(table, str)
        self.assertIn("| Metric |", table)
        self.assertIn("| Win Rate |", table)
        self.assertIn("82.00%", table)  # Improved out-sample win rate
        self.assertIn("Baseline Strategy", table)
        self.assertIn("Improved Strategy", table)
    
    def test_generate_key_findings(self):
        """Test key findings section generation."""
        # This test will fail initially - we need to implement this method
        findings = self.doc_generator.generate_key_findings(
            self.sample_results, self.sample_optimization
        )
        
        self.assertIsInstance(findings, str)
        self.assertIn("Key Findings", findings)
        self.assertIn("optimal parameters", findings.lower())
        self.assertIn("higher win rate", findings.lower())
    
    def test_generate_methodology_section(self):
        """Test methodology section generation."""
        # This test will fail initially - we need to implement this method
        methodology = self.doc_generator.generate_methodology_section()
        
        self.assertIsInstance(methodology, str)
        self.assertIn("Methodology", methodology)
        self.assertIn("Supertrend", methodology)
        self.assertIn("multi-filter", methodology.lower())
        self.assertIn("70% in-sample", methodology)
    
    def test_generate_conclusions(self):
        """Test conclusions section generation."""
        # This test will fail initially - we need to implement this method
        conclusions = self.doc_generator.generate_conclusions(self.sample_results)
        
        self.assertIsInstance(conclusions, str)
        self.assertIn("Conclusions", conclusions)
        self.assertIn("target", conclusions.lower())
        self.assertIn("recommendation", conclusions.lower())
    
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_results_document(self, mock_file):
        """Test complete results document generation."""
        # This test will fail initially - we need to implement this method
        output_path = 'test_results.md'
        
        self.doc_generator.generate_results_document(
            results=self.sample_results,
            optimization_results=self.sample_optimization,
            output_path=output_path
        )
        
        # Check that file was opened for writing
        mock_file.assert_called_once_with(output_path, 'w', encoding='utf-8')
        
        # Check that content was written
        handle = mock_file()
        handle.write.assert_called()
        
        # Get the written content
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        
        # Verify key sections are present
        self.assertIn("# Supertrend Strategy Optimization Results", written_content)
        self.assertIn("## Executive Summary", written_content)
        self.assertIn("## Performance Comparison", written_content)
        self.assertIn("## Key Findings", written_content)
        self.assertIn("## Methodology", written_content)
        self.assertIn("## Conclusions", written_content)
    
    def test_get_achievement_status(self):
        """Test target achievement status determination."""
        # This test will fail initially - we need to implement this method
        # Target achieved (82% > 80%)
        status = self.doc_generator.get_achievement_status(0.82)
        self.assertEqual(status, "✅ TARGET ACHIEVED")
        
        # Target not achieved
        status = self.doc_generator.get_achievement_status(0.75)
        self.assertEqual(status, "❌ TARGET NOT ACHIEVED")
        
        # Edge case - exactly 80%
        status = self.doc_generator.get_achievement_status(0.80)
        self.assertEqual(status, "✅ TARGET ACHIEVED")
    
    def test_error_handling_invalid_results(self):
        """Test error handling for invalid results data."""
        # This test will fail initially - we need to implement error handling
        with self.assertRaises(ValueError):
            self.doc_generator.generate_results_document({}, {}, 'test.md')
        
        with self.assertRaises(ValueError):
            self.doc_generator.generate_results_document(None, {}, 'test.md')
    
    def test_create_directory_if_not_exists(self):
        """Test automatic directory creation for output paths."""
        # This test will fail initially - we need to implement directory creation
        test_path = 'test_dir/subdir/results.md'
        
        with patch('os.makedirs') as mock_makedirs:
            with patch('builtins.open', mock_open()):
                self.doc_generator.generate_results_document(
                    self.sample_results, self.sample_optimization, test_path
                )
                # Should create directory structure
                mock_makedirs.assert_called()


if __name__ == '__main__':
    unittest.main()