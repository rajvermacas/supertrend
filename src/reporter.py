"""
Console reporting module for strategy performance comparison.

This module provides formatted console output comparing baseline vs improved
trading strategies with professional table formatting and clear metrics display.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Reporter:
    """
    Console reporter for strategy performance comparison.
    
    Generates formatted tables and professional output for strategy results
    comparison between baseline and improved strategies.
    """
    
    def __init__(self):
        """Initialize Reporter with default formatting settings."""
        logger.info("Reporter initialized")
    
    def format_percentage(self, value: float) -> str:
        """
        Format a decimal value as a percentage string.
        
        Args:
            value: Decimal value to format (e.g., 0.1234 -> "12.34%")
            
        Returns:
            Formatted percentage string
        """
        return f"{value * 100:.2f}%"
    
    def format_number(self, value: float) -> str:
        """
        Format a number with consistent decimal places.
        
        Args:
            value: Number to format
            
        Returns:
            Formatted number string with 3 decimal places
        """
        return f"{value:.3f}"
    
    def print_header(self, title: str) -> None:
        """
        Print a formatted header with separator lines.
        
        Args:
            title: Header title to display
        """
        separator = "=" * len(title)
        print(f"\n{separator}")
        print(title)
        print(separator)
    
    def print_section(self, title: str) -> None:
        """
        Print a formatted section header.
        
        Args:
            title: Section title to display
        """
        separator = "-" * len(title)
        print(f"\n{title}")
        print(separator)
    
    def generate_results_table(self, results: Dict[str, Any]) -> str:
        """
        Generate a formatted results table as a string.
        
        Args:
            results: Dictionary containing strategy results
            
        Returns:
            Formatted table string
        """
        if not results:
            raise ValueError("Results dictionary cannot be empty")
        
        # Extract data for table
        baseline_in = results.get('baseline_in_sample', {})
        baseline_out = results.get('baseline_out_sample', {})
        improved_in = results.get('improved_in_sample', {})
        improved_out = results.get('improved_out_sample', {})
        
        # Create table content
        table_lines = []
        table_lines.append("Strategy Performance Comparison")
        table_lines.append("=" * 50)
        table_lines.append("")
        
        # Metrics rows
        metrics = [
            ('Win Rate', 'win_rate', self.format_percentage),
            ('Total Return', 'total_return', self.format_percentage),
            ('Max Drawdown', 'max_drawdown', self.format_percentage),
            ('Profit Factor', 'profit_factor', self.format_number),
            ('Total Trades', 'total_trades', str),
            ('Avg Return', 'avg_return', self.format_percentage)
        ]
        
        for metric_name, metric_key, formatter in metrics:
            baseline_in_val = formatter(baseline_in.get(metric_key, 0))
            baseline_out_val = formatter(baseline_out.get(metric_key, 0))
            improved_in_val = formatter(improved_in.get(metric_key, 0))
            improved_out_val = formatter(improved_out.get(metric_key, 0))
            
            table_lines.append(f"{metric_name}: {baseline_in_val} | {baseline_out_val} | {improved_in_val} | {improved_out_val}")
        
        return "\n".join(table_lines)
    
    def print_strategy_comparison(self, results: Dict[str, Any]) -> None:
        """
        Print formatted strategy comparison table to console.
        
        Args:
            results: Dictionary containing strategy performance results
            
        Raises:
            ValueError: If results is None or empty
        """
        if not results:
            raise ValueError("Results dictionary cannot be None or empty")
        
        self.print_header("STRATEGY PERFORMANCE COMPARISON")
        
        # Print strategy sections
        self.print_section("Baseline Strategy")
        print("Standard Supertrend with default parameters")
        
        self.print_section("Improved Strategy") 
        print("Multi-filter system with trend, volume, and volatility filters")
        
        # Print results sections
        self.print_section("In-Sample Results")
        print("Training data performance (70% of dataset)")
        
        self.print_section("Out-of-Sample Results")
        print("Validation data performance (30% of dataset)")
        
        # Print detailed table
        table = self.generate_results_table(results)
        print(f"\n{table}")
        
        logger.info("Strategy comparison report printed successfully")