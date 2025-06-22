"""
Integration tests for the complete Supertrend application workflow.

This module tests the end-to-end functionality that connects all components
of the Supertrend strategy optimization system.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategy_runner import StrategyRunner
from data_loader import DataLoader


class TestMainIntegration:
    """Test suite for main.py integration with core components."""
    
    def test_main_script_execution_smoke_test(self):
        """
        Verify main.py can execute without crashes (smoke test).
        
        This is the critical integration test that currently fails.
        According to QA report CRITICAL-001, main.py crashes with
        "The truth value of a DataFrame is ambiguous" error.
        """
        # This test should fail initially, proving the integration issue exists
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, 'main.py'],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        
        # This assertion will fail until we fix the integration
        assert result.returncode == 0, f"main.py failed with error: {result.stderr}"
        assert "Error in main execution" not in result.stderr
        
    def test_strategy_runner_initialization_without_data(self):
        """
        Test that StrategyRunner can be initialized without data parameter.
        
        According to QA report, main.py incorrectly passes data to StrategyRunner
        constructor when it should be passed to run_complete_comparison method.
        """
        # This should work without passing data to constructor
        strategy_runner = StrategyRunner()
        assert strategy_runner is not None
        
    def test_strategy_runner_data_flow_structure(self):
        """
        Validate the data structure returned by StrategyRunner matches
        what main.py expects to use.
        
        QA report CRITICAL-002 identifies data structure mismatches.
        """
        # Create mock data with sufficient rows for data splitting
        dates = pd.date_range('2023-01-01', periods=50, freq='h')
        mock_data = pd.DataFrame({
            'Open': range(100, 150),
            'High': range(101, 151),
            'Low': range(99, 149),
            'Close': range(100, 150),
            'Volume': range(1000, 1050)
        }, index=dates)
        
        strategy_runner = StrategyRunner()
        
        # This should work now with sufficient data
        comparison_results = strategy_runner.run_complete_comparison(mock_data)
        
        # Verify expected structure that main.py needs
        assert 'out_of_sample_results' in comparison_results
        assert 'improved' in comparison_results['out_of_sample_results']
        assert 'baseline_default' in comparison_results['out_of_sample_results']
        assert 'baseline_optimized' in comparison_results['out_of_sample_results']
        
        # These fields should be accessible for visualization
        improved_results = comparison_results['out_of_sample_results']['improved']
        assert 'raw_results' in improved_results
        assert 'performance_metrics' in improved_results['raw_results']
        
        # Verify strategy comparison structure exists
        assert 'strategy_comparison' in comparison_results
        assert 'best_strategy' in comparison_results['strategy_comparison']
        
    def test_data_loader_integration(self):
        """
        Test DataLoader integration works correctly with main workflow.
        """
        data_loader = DataLoader(
            ticker="^NSEI",
            period="730d", 
            interval="1h"
        )
        
        # Should load data without errors (use correct method name)
        data = data_loader.get_data()
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert len(data) > 100  # Should have reasonable amount of data


class TestErrorHandling:
    """Test suite for error handling in integration scenarios."""
    
    def test_network_failure_handling(self):
        """Test graceful handling of network failures during data download."""
        # This test will be implemented once error handling is added
        pass
        
    def test_corrupted_data_handling(self):
        """Test handling of corrupted or invalid market data."""
        # This test will be implemented once error handling is added  
        pass
        
    def test_configuration_error_handling(self):
        """Test handling of invalid configuration parameters."""
        # This test will be implemented once error handling is added
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])