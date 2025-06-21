"""Test suite for strategy runner functionality."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from src.strategy_runner import StrategyRunner


class TestStrategyRunner:
    """Test cases for StrategyRunner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create sample data
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='h')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(100, 200, 100),
            'High': np.random.uniform(150, 250, 100),
            'Low': np.random.uniform(50, 150, 100),
            'Close': np.random.uniform(100, 200, 100),
            'Volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        self.runner = StrategyRunner()
    
    def test_initialization(self):
        """Test StrategyRunner initialization."""
        runner = StrategyRunner()
        assert runner.in_sample_ratio == 0.7
        assert abs(runner.out_of_sample_ratio - 0.3) < 1e-10
        
        # Test custom parameters
        custom_runner = StrategyRunner(
            in_sample_ratio=0.8,
            optimization_metric='total_return'
        )
        assert custom_runner.in_sample_ratio == 0.8
        assert abs(custom_runner.out_of_sample_ratio - 0.2) < 1e-10
        assert custom_runner.optimization_metric == 'total_return'
    
    def test_invalid_initialization(self):
        """Test initialization with invalid parameters."""
        with pytest.raises(ValueError, match="in_sample_ratio must be between 0 and 1"):
            StrategyRunner(in_sample_ratio=1.5)
    
    def test_run_baseline_strategy(self):
        """Test running baseline strategy with fixed parameters."""
        # Mock the backtester to return predictable results
        with patch('src.strategy_runner.BacktestEngine') as mock_backtest_engine:
            mock_engine = Mock()
            mock_backtest_engine.return_value = mock_engine
            
            mock_result = {
                'trades': [],
                'performance_metrics': {
                    'win_rate_pct': 65.0,
                    'total_return_pct': 8.5,
                    'max_drawdown_pct': 12.0,
                    'total_trades': 25,
                    'profit_factor': 1.8
                },
                'equity_curve': [100000, 102000, 105000],
                'total_signals': 50,
                'strategy_type': 'baseline'
            }
            mock_engine.execute_strategy.return_value = mock_result
            
            result = self.runner.run_baseline_strategy(self.sample_data)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'strategy_type' in result
        assert 'parameters' in result
        assert 'performance' in result
        assert 'raw_results' in result
        
        assert result['strategy_type'] == 'baseline'
        assert 'atr_period' in result['parameters']
        assert 'multiplier' in result['parameters']
        
        performance = result['performance']
        assert 'win_rate' in performance
        assert 'total_return' in performance
        assert 'max_drawdown' in performance
        assert performance['win_rate'] == 0.65
        assert performance['total_return'] == 0.085
        assert performance['max_drawdown'] == 0.12
    
    def test_run_improved_strategy(self):
        """Test running improved strategy with multi-filter system."""
        with patch('src.strategy_runner.BacktestEngine') as mock_backtest_engine:
            mock_engine = Mock()
            mock_backtest_engine.return_value = mock_engine
            
            mock_result = {
                'trades': [],
                'performance_metrics': {
                    'win_rate_pct': 78.0,
                    'total_return_pct': 12.3,
                    'max_drawdown_pct': 8.5,
                    'total_trades': 18,
                    'profit_factor': 2.4
                },
                'equity_curve': [100000, 103000, 108000],
                'total_signals': 36,
                'strategy_type': 'improved'
            }
            mock_engine.execute_strategy.return_value = mock_result
            
            result = self.runner.run_improved_strategy(self.sample_data)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert result['strategy_type'] == 'improved'
        assert 'parameters' in result
        assert 'performance' in result
        
        performance = result['performance']
        assert performance['win_rate'] == 0.78
        assert abs(performance['total_return'] - 0.123) < 1e-10
        assert abs(performance['max_drawdown'] - 0.085) < 1e-10
    
    def test_optimize_baseline_strategy(self):
        """Test optimizing baseline strategy parameters."""
        # Mock the optimizer that's already in the runner
        optimization_results = {
            'best_parameters': {'atr_period': 12, 'multiplier': 3.5},
            'best_metrics': {
                'win_rate': 0.72,
                'total_return': 0.095,
                'max_drawdown': 0.08,
                'total_trades': 22,
                'profit_factor': 2.1
            },
            'all_results': [],
            'optimization_summary': {
                'total_combinations_tested': 48,
                'best_win_rate': 0.72,
                'optimization_metric': 'win_rate'
            }
        }
        
        with patch.object(self.runner.optimizer, 'optimize_parameters') as mock_optimize:
            mock_optimize.return_value = optimization_results
            result = self.runner.optimize_baseline_strategy(self.sample_data)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'strategy_type' in result
        assert 'best_parameters' in result
        assert 'best_performance' in result
        assert 'optimization_summary' in result
        assert 'raw_optimization_results' in result
        
        assert result['strategy_type'] == 'baseline_optimized'
        assert result['best_parameters']['atr_period'] == 12
        assert result['best_parameters']['multiplier'] == 3.5
        assert result['best_performance']['win_rate'] == 0.72
    
    def test_run_complete_comparison(self):
        """Test running complete strategy comparison with optimization."""
        # Create mock in-sample and out-of-sample data
        split_point = int(len(self.sample_data) * 0.7)
        in_sample_data = self.sample_data.iloc[:split_point]
        out_of_sample_data = self.sample_data.iloc[split_point:]
        
        # Mock the data splitter that's already in the runner
        with patch.object(self.runner.data_splitter, 'split_data') as mock_split, \
             patch.object(self.runner.data_splitter, 'get_split_info') as mock_info:
            
            mock_split.return_value = (in_sample_data, out_of_sample_data)
            mock_info.return_value = {
                'total_rows': 100,
                'in_sample_rows': 70,
                'out_of_sample_rows': 30,
                'split_date': in_sample_data.index[-1]
            }
            
            # Mock strategy methods
            with patch.object(self.runner, 'run_baseline_strategy') as mock_baseline, \
                 patch.object(self.runner, 'optimize_baseline_strategy') as mock_optimize, \
                 patch.object(self.runner, 'run_improved_strategy') as mock_improved:
                
                # Mock baseline results
                mock_baseline.return_value = {
                    'strategy_type': 'baseline',
                    'parameters': {'atr_period': 10, 'multiplier': 3.0},
                    'performance': {
                        'win_rate': 0.65, 'total_return': 0.08, 'max_drawdown': 0.12,
                        'total_trades': 25, 'profit_factor': 1.5
                    }
                }
                
                # Mock optimization results
                mock_optimize.return_value = {
                    'strategy_type': 'baseline_optimized',
                    'best_parameters': {'atr_period': 12, 'multiplier': 3.5},
                    'best_performance': {
                        'win_rate': 0.72, 'total_return': 0.095, 'max_drawdown': 0.10,
                        'total_trades': 22, 'profit_factor': 1.8
                    }
                }
                
                # Mock improved strategy results
                mock_improved.return_value = {
                    'strategy_type': 'improved',
                    'parameters': {'atr_period': 12, 'multiplier': 3.5},
                    'performance': {
                        'win_rate': 0.78, 'total_return': 0.12, 'max_drawdown': 0.08,
                        'total_trades': 18, 'profit_factor': 2.2
                    }
                }
                
                result = self.runner.run_complete_comparison(self.sample_data)
        
        # Verify complete comparison structure
        assert isinstance(result, dict)
        assert 'data_split_info' in result
        assert 'in_sample_results' in result
        assert 'out_of_sample_results' in result
        assert 'strategy_comparison' in result
        
        # Check data split info
        assert result['data_split_info']['total_rows'] == 100
        assert result['data_split_info']['in_sample_rows'] == 70
        assert result['data_split_info']['out_of_sample_rows'] == 30
        
        # Check in-sample results
        in_sample = result['in_sample_results']
        assert 'baseline' in in_sample
        assert 'optimization' in in_sample
        
        # Check out-of-sample results
        out_sample = result['out_of_sample_results']
        assert 'baseline_default' in out_sample
        assert 'baseline_optimized' in out_sample
        assert 'improved' in out_sample
        
        # Check strategy comparison
        comparison = result['strategy_comparison']
        assert 'best_strategy' in comparison
        assert 'performance_ranking' in comparison
    
    def test_generate_strategy_comparison(self):
        """Test strategy comparison generation."""
        results = {
            'baseline': {'performance': {
                'win_rate': 0.65, 'total_return': 0.08, 'max_drawdown': 0.12,
                'total_trades': 25, 'profit_factor': 1.5
            }},
            'optimized': {'performance': {
                'win_rate': 0.72, 'total_return': 0.095, 'max_drawdown': 0.10,
                'total_trades': 22, 'profit_factor': 1.8
            }},
            'improved': {'performance': {
                'win_rate': 0.78, 'total_return': 0.12, 'max_drawdown': 0.08,
                'total_trades': 18, 'profit_factor': 2.2
            }}
        }
        
        comparison = self.runner.generate_strategy_comparison(results)
        
        assert isinstance(comparison, dict)
        assert 'best_strategy' in comparison
        assert 'performance_ranking' in comparison
        assert 'win_rate_comparison' in comparison
        assert 'return_comparison' in comparison
        
        # Best strategy should be the one with highest win rate (improved)
        assert comparison['best_strategy']['strategy'] == 'improved'
        assert comparison['best_strategy']['win_rate'] == 0.78
        
        # Performance ranking should be ordered by win rate
        ranking = comparison['performance_ranking']
        assert len(ranking) == 3
        assert ranking[0]['strategy'] == 'improved'
        assert ranking[1]['strategy'] == 'optimized' 
        assert ranking[2]['strategy'] == 'baseline'
    
    def test_error_handling_empty_data(self):
        """Test error handling with empty data."""
        empty_data = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Data cannot be empty"):
            self.runner.run_baseline_strategy(empty_data)
    
    def test_error_handling_insufficient_data(self):
        """Test error handling with insufficient data for splitting."""
        small_data = self.sample_data.iloc[:1]  # Only 1 row
        
        with pytest.raises(ValueError, match="Insufficient data for in-sample/out-of-sample split"):
            self.runner.run_complete_comparison(small_data)