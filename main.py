"""
Main script for Supertrend Strategy Optimization
Orchestrates the complete process from data loading to results presentation
"""

import logging
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.config import Config
from src.strategy_runner import StrategyRunner
from src.reporter import Reporter
from src.visualizer import Visualizer
from src.doc_generator import DocGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to orchestrate the complete Supertrend strategy development
    
    Implements all 5 stages: Data Management, Technical Indicators, 
    Backtesting, Strategy Optimization, and Reporting & Visualization
    """
    logger.info("=== Supertrend Strategy Optimization ===")
    logger.info("Complete Strategy Development and Analysis")
    
    try:
        # Stage 1: Data Management
        logger.info("Stage 1: Loading and preparing market data...")
        data_loader = DataLoader(
            ticker=Config.TICKER,
            period=Config.PERIOD,
            interval=Config.INTERVAL
        )
        data = data_loader.get_data(force_download=False)
        logger.info(f"Data loaded: {len(data)} rows from {data.index[0]} to {data.index[-1]}")
        
        # Stage 2-4: Strategy Development and Optimization
        logger.info("Stages 2-4: Running strategy comparison and optimization...")
        strategy_runner = StrategyRunner(data)
        
        # Run complete strategy comparison
        comparison_results = strategy_runner.run_complete_comparison()
        
        # Stage 5: Reporting and Visualization
        logger.info("Stage 5: Generating reports and visualizations...")
        
        # Console reporting
        reporter = Reporter()
        reporter.print_strategy_comparison(comparison_results['results'])
        
        # Generate visualizations
        visualizer = Visualizer()
        
        # Create equity curves
        equity_curves = {
            'Baseline Strategy': comparison_results['baseline_equity_curve'],
            'Improved Strategy': comparison_results['improved_equity_curve']
        }
        
        logger.info("Creating equity curve chart...")
        visualizer.create_equity_curve(
            equity_curves=equity_curves,
            output_path='equity_curve.png',
            title='Strategy Performance Comparison - Equity Curves'
        )
        
        # Create trade execution chart (using improved strategy trades)
        logger.info("Creating trade execution chart...")
        visualizer.create_trade_execution_chart(
            price_data=data,
            trades=comparison_results['improved_trades'],
            output_path='trade_executions.png',
            title='Improved Strategy - Trade Executions'
        )
        
        # Generate automated documentation
        logger.info("Generating results documentation...")
        doc_generator = DocGenerator()
        doc_generator.generate_results_document(
            results=comparison_results['results'],
            optimization_results=comparison_results['optimization_results'],
            output_path='results.md'
        )
        
        # Summary
        print("\n" + "="*60)
        print("STRATEGY OPTIMIZATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("Generated files:")
        print("  📊 equity_curve.png - Strategy performance comparison")
        print("  📈 trade_executions.png - Trade entry/exit markers")
        print("  📄 results.md - Comprehensive analysis documentation")
        print("\nTarget Win Rate: 80%")
        
        improved_win_rate = comparison_results['results']['improved_out_sample']['win_rate']
        print(f"Achieved Win Rate: {improved_win_rate:.1%}")
        
        if improved_win_rate >= 0.80:
            print("🎯 TARGET ACHIEVED! ✅")
        else:
            print("🎯 Target not achieved ❌")
        
        print("="*60)
        logger.info("Complete strategy optimization finished successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()