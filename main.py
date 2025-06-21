"""
Main script for Supertrend Strategy Optimization
Orchestrates the entire process from data loading to results presentation
"""

import logging
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to orchestrate the Supertrend strategy development
    
    Currently implements Stage 1: Foundation & Data Management
    """
    logger.info("=== Supertrend Strategy Optimization ===")
    logger.info("Stage 1: Foundation & Data Management")
    
    try:
        # Initialize data loader
        data_loader = DataLoader(
            ticker=Config.TICKER,
            period=Config.PERIOD,
            interval=Config.INTERVAL
        )
        
        # Load data (using cache if available)
        logger.info("Loading market data...")
        data = data_loader.get_data(force_download=False)
        
        # Display basic statistics
        logger.info(f"Data loaded successfully:")
        logger.info(f"- Total rows: {len(data)}")
        logger.info(f"- Date range: {data.index[0]} to {data.index[-1]}")
        logger.info(f"- Columns: {list(data.columns)}")
        
        # Display sample data
        print("\n=== Data Sample ===")
        print(data.head())
        
        print("\n=== Data Info ===")
        print(f"Shape: {data.shape}")
        print(f"Date Range: {data.index[0]} to {data.index[-1]}")
        print(f"Columns: {list(data.columns)}")
        
        logger.info("Stage 1 completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()