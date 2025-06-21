"""Strategy runner for complete backtesting and optimization workflow."""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple

from src.data_splitter import DataSplitter
from src.optimizer import ParameterOptimizer
from src.backtester import BacktestEngine
from src.config import BASELINE_CONFIG, IMPROVED_CONFIG

logger = logging.getLogger(__name__)


class StrategyRunner:
    """
    Orchestrates complete strategy testing, optimization, and comparison.
    
    This class manages the full workflow of testing multiple strategy variants,
    optimizing parameters, and comparing performance across in-sample and 
    out-of-sample periods.
    """
    
    def __init__(self, 
                 in_sample_ratio: float = 0.7,
                 optimization_metric: str = 'win_rate'):
        """
        Initialize StrategyRunner.
        
        Args:
            in_sample_ratio: Fraction of data to use for optimization
            optimization_metric: Metric to optimize ('win_rate', 'total_return', etc.)
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not 0 < in_sample_ratio < 1:
            raise ValueError("in_sample_ratio must be between 0 and 1")
        
        self.in_sample_ratio = in_sample_ratio
        self.out_of_sample_ratio = 1.0 - in_sample_ratio
        self.optimization_metric = optimization_metric
        
        # Initialize components
        self.data_splitter = DataSplitter(in_sample_ratio=in_sample_ratio)
        self.optimizer = ParameterOptimizer(optimization_metric=optimization_metric)
        
        logger.info(f"StrategyRunner initialized with {in_sample_ratio:.1%} in-sample ratio")
    
    def run_baseline_strategy(self, data: pd.DataFrame, 
                             parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run baseline Supertrend strategy with specified or default parameters.
        
        Args:
            data: Market data for backtesting
            parameters: Optional strategy parameters (uses defaults if None)
            
        Returns:
            Dictionary containing strategy results
            
        Raises:
            ValueError: If data is empty or invalid
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        # Use default baseline parameters if none provided
        if parameters is None:
            parameters = BASELINE_CONFIG.copy()
        
        # Initialize backtester and run strategy
        backtester = BacktestEngine()
        raw_result = backtester.execute_strategy(data, parameters, use_improved_strategy=False)
        
        # Convert performance metrics to decimal format and structure results
        performance_metrics = raw_result['performance_metrics']
        performance = {
            'win_rate': performance_metrics['win_rate_pct'] / 100.0,
            'total_return': performance_metrics['total_return_pct'] / 100.0,
            'max_drawdown': performance_metrics['max_drawdown_pct'] / 100.0,
            'total_trades': performance_metrics['total_trades'],
            'profit_factor': performance_metrics.get('profit_factor', 0.0)
        }
        
        result = {
            'strategy_type': 'baseline',
            'parameters': parameters.copy(),
            'performance': performance,
            'raw_results': raw_result
        }
        
        logger.info(f"Baseline strategy completed: {performance['win_rate']:.1%} win rate, "
                   f"{performance['total_return']:.1%} return")
        
        return result
    
    def run_improved_strategy(self, data: pd.DataFrame, 
                             parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run improved multi-filter Supertrend strategy.
        
        Args:
            data: Market data for backtesting
            parameters: Optional strategy parameters (uses defaults if None)
            
        Returns:
            Dictionary containing strategy results
            
        Raises:
            ValueError: If data is empty or invalid
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        # Use default improved parameters if none provided
        if parameters is None:
            parameters = IMPROVED_CONFIG.copy()
        
        # Initialize backtester and run improved strategy
        backtester = BacktestEngine()
        raw_result = backtester.execute_strategy(data, parameters, use_improved_strategy=True)
        
        # Convert performance metrics to decimal format
        performance_metrics = raw_result['performance_metrics']
        performance = {
            'win_rate': performance_metrics['win_rate_pct'] / 100.0,
            'total_return': performance_metrics['total_return_pct'] / 100.0,
            'max_drawdown': performance_metrics['max_drawdown_pct'] / 100.0,
            'total_trades': performance_metrics['total_trades'],
            'profit_factor': performance_metrics.get('profit_factor', 0.0)
        }
        
        result = {
            'strategy_type': 'improved',
            'parameters': parameters.copy(),
            'performance': performance,
            'raw_results': raw_result
        }
        
        logger.info(f"Improved strategy completed: {performance['win_rate']:.1%} win rate, "
                   f"{performance['total_return']:.1%} return")
        
        return result
    
    def optimize_baseline_strategy(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Optimize baseline strategy parameters using grid search.
        
        Args:
            data: Market data for optimization (should be in-sample data)
            
        Returns:
            Dictionary containing optimization results
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        logger.info("Starting baseline strategy optimization...")
        
        # Run parameter optimization
        optimization_results = self.optimizer.optimize_parameters(data)
        
        result = {
            'strategy_type': 'baseline_optimized',
            'best_parameters': optimization_results['best_parameters'],
            'best_performance': optimization_results['best_metrics'],
            'optimization_summary': optimization_results['optimization_summary'],
            'raw_optimization_results': optimization_results
        }
        
        best_perf = optimization_results['best_metrics']
        logger.info(f"Optimization completed. Best parameters: {optimization_results['best_parameters']}")
        logger.info(f"Best performance: {best_perf['win_rate']:.1%} win rate, "
                   f"{best_perf['total_return']:.1%} return")
        
        return result
    
    def run_complete_comparison(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run complete strategy comparison with optimization and validation.
        
        This method performs the full workflow:
        1. Split data into in-sample and out-of-sample periods
        2. Run baseline strategy on in-sample data
        3. Optimize baseline parameters on in-sample data
        4. Test all strategies on out-of-sample data
        5. Compare performance and rank strategies
        
        Args:
            data: Complete market data for analysis
            
        Returns:
            Dictionary containing complete comparison results
            
        Raises:
            ValueError: If data is insufficient for splitting
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        if len(data) < 10:  # Minimum reasonable data size
            raise ValueError("Insufficient data for in-sample/out-of-sample split")
        
        logger.info("Starting complete strategy comparison...")
        
        # Step 1: Split data
        in_sample_data, out_of_sample_data = self.data_splitter.split_data(data)
        split_info = self.data_splitter.get_split_info(data, in_sample_data, out_of_sample_data)
        
        logger.info(f"Data split: {split_info['in_sample_rows']} in-sample, "
                   f"{split_info['out_of_sample_rows']} out-of-sample rows")
        
        # Step 2: In-sample analysis
        logger.info("Running in-sample analysis...")
        
        # Run baseline strategy on in-sample data
        baseline_in_sample = self.run_baseline_strategy(in_sample_data)
        
        # Optimize baseline parameters on in-sample data
        optimization_results = self.optimize_baseline_strategy(in_sample_data)
        
        in_sample_results = {
            'baseline': baseline_in_sample,
            'optimization': optimization_results
        }
        
        # Step 3: Out-of-sample validation
        logger.info("Running out-of-sample validation...")
        
        # Test baseline with default parameters
        baseline_default_out = self.run_baseline_strategy(out_of_sample_data)
        
        # Test baseline with optimized parameters
        optimized_params = optimization_results['best_parameters']
        baseline_optimized_out = self.run_baseline_strategy(out_of_sample_data, optimized_params)
        
        # Test improved strategy with optimized baseline parameters as base
        improved_params = IMPROVED_CONFIG.copy()
        improved_params.update(optimized_params)  # Use optimized baseline parameters
        improved_out = self.run_improved_strategy(out_of_sample_data, improved_params)
        
        out_of_sample_results = {
            'baseline_default': baseline_default_out,
            'baseline_optimized': baseline_optimized_out,
            'improved': improved_out
        }
        
        # Step 4: Generate comparison and ranking
        strategy_comparison = self.generate_strategy_comparison(out_of_sample_results)
        
        # Compile complete results
        complete_results = {
            'data_split_info': split_info,
            'in_sample_results': in_sample_results,
            'out_of_sample_results': out_of_sample_results,
            'strategy_comparison': strategy_comparison
        }
        
        best_strategy = strategy_comparison['best_strategy']
        logger.info(f"Complete comparison finished. Best strategy: {best_strategy['strategy']} "
                   f"({best_strategy['win_rate']:.1%} win rate)")
        
        return complete_results
    
    def generate_strategy_comparison(self, strategy_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comparison and ranking of strategy results.
        
        Args:
            strategy_results: Dictionary of strategy results keyed by strategy name
            
        Returns:
            Dictionary containing comparison analysis
        """
        if not strategy_results:
            return {'best_strategy': None, 'performance_ranking': []}
        
        # Extract performance metrics for comparison
        performance_data = []
        for strategy_name, results in strategy_results.items():
            performance = results['performance']
            performance_data.append({
                'strategy': strategy_name,
                'win_rate': performance['win_rate'],
                'total_return': performance['total_return'],
                'max_drawdown': performance['max_drawdown'],
                'total_trades': performance['total_trades'],
                'profit_factor': performance.get('profit_factor', 0.0)
            })
        
        # Sort by optimization metric (default: win_rate)
        if self.optimization_metric == 'max_drawdown':
            # For drawdown, lower is better
            performance_data.sort(key=lambda x: x[self.optimization_metric])
        else:
            # For other metrics, higher is better
            performance_data.sort(key=lambda x: x[self.optimization_metric], reverse=True)
        
        # Identify best strategy
        best_strategy = performance_data[0] if performance_data else None
        
        # Create comparison metrics
        win_rates = [p['win_rate'] for p in performance_data]
        returns = [p['total_return'] for p in performance_data]
        
        comparison = {
            'best_strategy': best_strategy,
            'performance_ranking': performance_data,
            'win_rate_comparison': {
                'highest': max(win_rates) if win_rates else 0,
                'lowest': min(win_rates) if win_rates else 0,
                'average': np.mean(win_rates) if win_rates else 0
            },
            'return_comparison': {
                'highest': max(returns) if returns else 0,
                'lowest': min(returns) if returns else 0,
                'average': np.mean(returns) if returns else 0
            },
            'optimization_metric': self.optimization_metric
        }
        
        return comparison