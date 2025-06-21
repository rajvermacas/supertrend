"""Parameter optimization engine for strategy tuning."""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Union
from itertools import product

from src.backtester import BacktestEngine
from src.strategy import StrategyEngine
from src.performance import PerformanceMetrics

logger = logging.getLogger(__name__)


class ParameterOptimizer:
    """
    Grid search optimization engine for Supertrend strategy parameters.
    
    This class performs exhaustive parameter optimization while maintaining
    strict separation between in-sample optimization and out-of-sample validation
    to prevent lookahead bias.
    """
    
    VALID_METRICS = ['win_rate', 'total_return', 'max_drawdown', 'profit_factor']
    
    def __init__(self, 
                 atr_period_range: Tuple[int, int] = (5, 20),
                 multiplier_range: Tuple[float, float] = (2.0, 5.0),
                 multiplier_step: float = 0.5,
                 optimization_metric: str = 'win_rate'):
        """
        Initialize ParameterOptimizer.
        
        Args:
            atr_period_range: Tuple of (min, max) ATR periods to test
            multiplier_range: Tuple of (min, max) multipliers to test
            multiplier_step: Step size for multiplier range
            optimization_metric: Metric to optimize ('win_rate', 'total_return', etc.)
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate inputs
        if not isinstance(atr_period_range, tuple) or len(atr_period_range) != 2:
            raise ValueError("atr_period_range must be a tuple of (min, max)")
        
        if not isinstance(multiplier_range, tuple) or len(multiplier_range) != 2:
            raise ValueError("multiplier_range must be a tuple of (min, max)")
        
        if multiplier_step <= 0:
            raise ValueError("multiplier_step must be positive")
        
        if optimization_metric not in self.VALID_METRICS:
            raise ValueError(f"optimization_metric must be one of {self.VALID_METRICS}")
        
        self.atr_period_range = atr_period_range
        self.multiplier_range = multiplier_range
        self.multiplier_step = multiplier_step
        self.optimization_metric = optimization_metric
        
        logger.info(f"ParameterOptimizer initialized:")
        logger.info(f"  ATR Period Range: {atr_period_range}")
        logger.info(f"  Multiplier Range: {multiplier_range} (step: {multiplier_step})")
        logger.info(f"  Optimization Metric: {optimization_metric}")
    
    def generate_parameter_combinations(self) -> List[Dict[str, Union[int, float]]]:
        """
        Generate all parameter combinations for grid search.
        
        Returns:
            List of parameter dictionaries to test
        """
        # Generate ATR period range
        atr_periods = list(range(self.atr_period_range[0], self.atr_period_range[1] + 1))
        
        # Generate multiplier range
        multipliers = []
        current_multiplier = self.multiplier_range[0]
        while current_multiplier <= self.multiplier_range[1] + 1e-6:  # Account for floating point precision
            multipliers.append(round(current_multiplier, 2))
            current_multiplier += self.multiplier_step
        
        # Generate all combinations
        combinations = []
        for atr_period, multiplier in product(atr_periods, multipliers):
            combinations.append({
                'atr_period': int(atr_period),
                'multiplier': float(multiplier)
            })
        
        logger.info(f"Generated {len(combinations)} parameter combinations")
        return combinations
    
    def run_single_backtest(self, data: pd.DataFrame, parameters: Dict[str, Union[int, float]]) -> Dict[str, Any]:
        """
        Run a single backtest with specified parameters.
        
        Args:
            data: Market data for backtesting
            parameters: Dictionary with 'atr_period' and 'multiplier' keys
            
        Returns:
            Dictionary containing parameters and resulting metrics
            
        Raises:
            ValueError: If data is empty or parameters are invalid
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        try:
            atr_period = int(parameters['atr_period'])
            multiplier = float(parameters['multiplier'])
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid parameters: {parameters}") from e
        
        # Initialize backtester
        backtester = BacktestEngine()
        
        # Create strategy configuration with optimized parameters
        strategy_config = {
            'atr_period': atr_period,
            'multiplier': multiplier
        }
        
        # Execute backtest (using baseline strategy)
        result = backtester.execute_strategy(data, strategy_config, use_improved_strategy=False)
        trades = result['trades']
        
        # Calculate performance metrics using the trades from backtester
        # The backtester already calculates these metrics
        perf_metrics = result['performance_metrics']
        metrics = {
            'win_rate': perf_metrics['win_rate_pct'] / 100.0,  # Convert percentage to decimal
            'total_return': perf_metrics['total_return_pct'] / 100.0,  # Convert percentage to decimal
            'max_drawdown': perf_metrics['max_drawdown_pct'] / 100.0,  # Convert percentage to decimal
            'total_trades': perf_metrics['total_trades'],
            'profit_factor': perf_metrics.get('profit_factor', 0.0)
        }
        
        result = {
            'parameters': parameters.copy(),
            'metrics': metrics
        }
        
        return result
    
    def optimize_parameters(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run full parameter optimization on the provided data.
        
        Args:
            data: Market data for optimization (should be in-sample data only)
            
        Returns:
            Dictionary containing optimization results
        """
        logger.info("Starting parameter optimization...")
        
        # Generate all parameter combinations
        combinations = self.generate_parameter_combinations()
        
        # Run backtest for each combination
        all_results = []
        for i, params in enumerate(combinations, 1):
            logger.info(f"Testing combination {i}/{len(combinations)}: {params}")
            
            try:
                result = self.run_single_backtest(data, params)
                all_results.append(result)
            except Exception as e:
                logger.warning(f"Failed to test parameters {params}: {e}")
                continue
        
        if not all_results:
            raise RuntimeError("No valid optimization results obtained")
        
        # Find best parameters based on optimization metric
        best_result = self._select_best_result(all_results)
        
        # Generate optimization summary
        summary = self.get_optimization_summary(all_results, best_result)
        
        optimization_results = {
            'best_parameters': best_result['parameters'],
            'best_metrics': best_result['metrics'],
            'all_results': all_results,
            'optimization_summary': summary
        }
        
        logger.info(f"Optimization complete. Best parameters: {best_result['parameters']}")
        logger.info(f"Best {self.optimization_metric}: {best_result['metrics'][self.optimization_metric]:.4f}")
        
        return optimization_results
    
    def _select_best_result(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best result based on the optimization metric.
        
        Args:
            all_results: List of all optimization results
            
        Returns:
            Best result dictionary
        """
        if self.optimization_metric == 'max_drawdown':
            # For drawdown, we want the minimum value (least drawdown)
            best_result = min(all_results, key=lambda x: x['metrics'][self.optimization_metric])
        else:
            # For other metrics, we want the maximum value
            best_result = max(all_results, key=lambda x: x['metrics'][self.optimization_metric])
        
        return best_result
    
    def get_optimization_summary(self, all_results: List[Dict[str, Any]], 
                                best_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics for the optimization run.
        
        Args:
            all_results: List of all optimization results
            best_result: Best result from optimization
            
        Returns:
            Summary statistics dictionary
        """
        best_metrics = best_result['metrics']
        
        summary = {
            'total_combinations_tested': len(all_results),
            'best_win_rate': best_metrics['win_rate'],
            'best_total_return': best_metrics['total_return'],
            'best_max_drawdown': best_metrics['max_drawdown'],
            'optimization_metric': self.optimization_metric,
            'best_parameter_atr_period': best_result['parameters']['atr_period'],
            'best_parameter_multiplier': best_result['parameters']['multiplier']
        }
        
        # Add profit factor if available
        if 'profit_factor' in best_metrics:
            summary['best_profit_factor'] = best_metrics['profit_factor']
        
        return summary