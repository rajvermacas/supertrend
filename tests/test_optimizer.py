"""Test suite for parameter optimization functionality."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from src.optimizer import ParameterOptimizer
from src.backtester import BacktestEngine
from src.strategy import StrategyEngine
from src.performance import PerformanceMetrics


class TestParameterOptimizer:
    """Test cases for ParameterOptimizer class."""
    
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
        
        self.optimizer = ParameterOptimizer()
    
    def test_initialization(self):
        """Test ParameterOptimizer initialization."""
        optimizer = ParameterOptimizer()
        assert optimizer.atr_period_range == (5, 20)
        assert optimizer.multiplier_range == (2.0, 5.0)
        assert optimizer.multiplier_step == 0.5
        assert optimizer.optimization_metric == 'win_rate'
        
        # Test custom parameters
        custom_optimizer = ParameterOptimizer(
            atr_period_range=(10, 30),
            multiplier_range=(1.0, 3.0),
            multiplier_step=0.25,
            optimization_metric='total_return'
        )
        assert custom_optimizer.atr_period_range == (10, 30)
        assert custom_optimizer.multiplier_range == (1.0, 3.0)
        assert custom_optimizer.multiplier_step == 0.25
        assert custom_optimizer.optimization_metric == 'total_return'
    
    def test_invalid_parameters(self):
        """Test initialization with invalid parameters."""
        with pytest.raises(ValueError, match="atr_period_range must be a tuple"):
            ParameterOptimizer(atr_period_range=[5, 20])
        
        with pytest.raises(ValueError, match="multiplier_range must be a tuple"):
            ParameterOptimizer(multiplier_range=[2.0, 5.0])
        
        with pytest.raises(ValueError, match="multiplier_step must be positive"):
            ParameterOptimizer(multiplier_step=-0.1)
        
        with pytest.raises(ValueError, match="optimization_metric must be one of"):
            ParameterOptimizer(optimization_metric='invalid_metric')
    
    def test_generate_parameter_combinations(self):
        """Test parameter combination generation."""
        combinations = self.optimizer.generate_parameter_combinations()
        
        # Check type and structure
        assert isinstance(combinations, list)
        assert len(combinations) > 0
        
        # Check each combination has correct structure
        for combo in combinations:
            assert isinstance(combo, dict)
            assert 'atr_period' in combo
            assert 'multiplier' in combo
            assert isinstance(combo['atr_period'], int)
            assert isinstance(combo['multiplier'], float)
        
        # Check parameter ranges
        atr_periods = [combo['atr_period'] for combo in combinations]
        multipliers = [combo['multiplier'] for combo in combinations]
        
        assert min(atr_periods) >= 5
        assert max(atr_periods) <= 20
        assert min(multipliers) >= 2.0
        assert max(multipliers) <= 5.0
    
    def test_generate_parameter_combinations_custom_range(self):
        """Test parameter combination generation with custom ranges."""
        custom_optimizer = ParameterOptimizer(
            atr_period_range=(10, 15),
            multiplier_range=(2.5, 3.5),
            multiplier_step=0.25
        )
        
        combinations = custom_optimizer.generate_parameter_combinations()
        
        expected_atr_periods = list(range(10, 16))  # 10 to 15 inclusive
        expected_multipliers = [2.5, 2.75, 3.0, 3.25, 3.5]
        expected_combinations = len(expected_atr_periods) * len(expected_multipliers)
        
        assert len(combinations) == expected_combinations
        
        atr_periods = sorted(list(set(combo['atr_period'] for combo in combinations)))
        multipliers = sorted(list(set(combo['multiplier'] for combo in combinations)))
        
        assert atr_periods == expected_atr_periods
        assert multipliers == expected_multipliers
    
    def test_run_single_backtest(self):
        """Test running a single backtest with specific parameters."""
        params = {'atr_period': 10, 'multiplier': 3.0}
        
        # Mock the backtester to return predictable results
        with patch('src.optimizer.BacktestEngine') as mock_backtest_engine:
            mock_engine = Mock()
            mock_backtest_engine.return_value = mock_engine
            
            # Mock backtester result with correct structure
            mock_result = {
                'trades': [
                    {'pnl_percentage': 0.05, 'direction': 'LONG'},
                    {'pnl_percentage': 0.03, 'direction': 'SHORT'},
                    {'pnl_percentage': -0.02, 'direction': 'LONG'}
                ],
                'performance_metrics': {
                    'win_rate_pct': 75.0,
                    'total_return_pct': 6.0,
                    'max_drawdown_pct': 5.0,
                    'total_trades': 3,
                    'profit_factor': 2.5
                },
                'equity_curve': [],
                'total_signals': 6,
                'strategy_type': 'baseline'
            }
            mock_engine.execute_strategy.return_value = mock_result
            
            result = self.optimizer.run_single_backtest(self.sample_data, params)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'parameters' in result
        assert 'metrics' in result
        assert result['parameters'] == params
        
        metrics = result['metrics']
        assert 'win_rate' in metrics
        assert 'total_return' in metrics
        assert 'max_drawdown' in metrics
        assert 'total_trades' in metrics
        assert 'profit_factor' in metrics
        
        # Check values (converted from percentages to decimals)
        assert metrics['win_rate'] == 0.75
        assert metrics['total_return'] == 0.06
        assert metrics['max_drawdown'] == 0.05
        assert metrics['total_trades'] == 3
        assert metrics['profit_factor'] == 2.5
    
    def test_optimize_parameters(self):
        """Test full parameter optimization process."""
        # Mock the single backtest method to return predictable results
        def mock_single_backtest(data, params):
            # Create varying results based on parameters
            base_win_rate = 0.6
            atr_bonus = (params['atr_period'] - 10) * 0.01
            multiplier_bonus = (params['multiplier'] - 3.0) * 0.02
            win_rate = base_win_rate + atr_bonus + multiplier_bonus
            
            return {
                'parameters': params,
                'metrics': {
                    'win_rate': min(max(win_rate, 0.0), 1.0),
                    'total_return': win_rate * 0.5,
                    'max_drawdown': 0.1,
                    'total_trades': 50
                }
            }
        
        with patch.object(self.optimizer, 'run_single_backtest', side_effect=mock_single_backtest):
            # Test with limited parameter range for faster testing
            test_optimizer = ParameterOptimizer(
                atr_period_range=(10, 12),
                multiplier_range=(3.0, 3.5),
                multiplier_step=0.5
            )
            
            optimization_results = test_optimizer.optimize_parameters(self.sample_data)
        
        # Verify results structure
        assert isinstance(optimization_results, dict)
        assert 'best_parameters' in optimization_results
        assert 'best_metrics' in optimization_results
        assert 'all_results' in optimization_results
        assert 'optimization_summary' in optimization_results
        
        # Verify best parameters are selected correctly
        best_params = optimization_results['best_parameters']
        assert best_params['atr_period'] in [10, 11, 12]
        assert best_params['multiplier'] in [3.0, 3.5]
        
        # Verify all results are captured
        all_results = optimization_results['all_results']
        expected_combinations = 3 * 2  # 3 atr_periods * 2 multipliers
        assert len(all_results) == expected_combinations
        
        # Verify optimization summary
        summary = optimization_results['optimization_summary']
        assert 'total_combinations_tested' in summary
        assert 'best_win_rate' in summary
        assert 'optimization_metric' in summary
        assert summary['total_combinations_tested'] == expected_combinations
    
    def test_optimize_parameters_different_metrics(self):
        """Test optimization with different target metrics."""
        def mock_single_backtest(data, params):
            return {
                'parameters': params,
                'metrics': {
                    'win_rate': 0.65,
                    'total_return': params['multiplier'] * 0.1,  # Higher multiplier = higher return
                    'max_drawdown': 0.1,
                    'total_trades': 30
                }
            }
        
        # Test optimization by total_return
        total_return_optimizer = ParameterOptimizer(
            atr_period_range=(10, 11),
            multiplier_range=(2.0, 4.0),
            multiplier_step=1.0,
            optimization_metric='total_return'
        )
        
        with patch.object(total_return_optimizer, 'run_single_backtest', side_effect=mock_single_backtest):
            results = total_return_optimizer.optimize_parameters(self.sample_data)
        
        # Best parameters should have highest multiplier (4.0) for best total_return
        assert results['best_parameters']['multiplier'] == 4.0
    
    def test_get_optimization_summary(self):
        """Test optimization summary generation."""
        # Create mock results
        all_results = [
            {
                'parameters': {'atr_period': 10, 'multiplier': 3.0},
                'metrics': {'win_rate': 0.65, 'total_return': 0.08, 'max_drawdown': 0.05}
            },
            {
                'parameters': {'atr_period': 12, 'multiplier': 3.5},
                'metrics': {'win_rate': 0.72, 'total_return': 0.12, 'max_drawdown': 0.08}
            }
        ]
        
        best_result = all_results[1]  # Second result has better metrics
        
        summary = self.optimizer.get_optimization_summary(all_results, best_result)
        
        assert isinstance(summary, dict)
        assert 'total_combinations_tested' in summary
        assert 'best_win_rate' in summary
        assert 'best_total_return' in summary
        assert 'best_max_drawdown' in summary
        assert 'optimization_metric' in summary
        assert summary['total_combinations_tested'] == 2
        assert summary['best_win_rate'] == 0.72
        assert summary['best_total_return'] == 0.12
        assert summary['best_max_drawdown'] == 0.08
    
    def test_error_handling_empty_data(self):
        """Test error handling with empty data."""
        empty_data = pd.DataFrame()
        params = {'atr_period': 10, 'multiplier': 3.0}
        
        with pytest.raises(ValueError, match="Data cannot be empty"):
            self.optimizer.run_single_backtest(empty_data, params)
    
    def test_error_handling_invalid_parameters(self):
        """Test error handling with invalid parameters."""
        invalid_params = {'atr_period': 'invalid', 'multiplier': 3.0}
        
        with pytest.raises((ValueError, TypeError)):
            self.optimizer.run_single_backtest(self.sample_data, invalid_params)