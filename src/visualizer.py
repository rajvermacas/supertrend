"""
Visualization module for strategy performance analysis.

This module provides chart generation capabilities including equity curves,
trade execution plots, and performance comparison visualizations.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import seaborn as sns

logger = logging.getLogger(__name__)


class Visualizer:
    """
    Chart generation class for trading strategy analysis.
    
    Creates professional-quality visualizations including equity curves,
    trade execution charts, and performance comparison plots.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """
        Initialize Visualizer with plotting style.
        
        Args:
            style: Matplotlib style to use for plots
        """
        self.style = style
        self.setup_plot_style()
        logger.info(f"Visualizer initialized with style: {style}")
    
    def setup_plot_style(self) -> None:
        """Setup consistent plot styling for all charts."""
        try:
            plt.style.use(self.style)
        except OSError:
            # Fallback to default style if specified style not available
            plt.style.use('default')
            logger.warning(f"Style '{self.style}' not available, using default")
        
        # Set default parameters
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
    
    def create_equity_curve(self, 
                          equity_curves: Dict[str, pd.Series],
                          output_path: str,
                          title: str = 'Strategy Performance Comparison',
                          xlabel: str = 'Date',
                          ylabel: str = 'Portfolio Value (₹)') -> None:
        """
        Create and save equity curve comparison chart.
        
        Args:
            equity_curves: Dictionary with strategy names as keys and 
                         equity curves as pandas Series
            output_path: Path to save the chart
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            
        Raises:
            ValueError: If equity_curves is empty or output_path is invalid
        """
        if not equity_curves:
            raise ValueError("Equity curves dictionary cannot be empty")
        
        if not output_path:
            raise ValueError("Output path cannot be empty")
        
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(output_path)
        if dir_path:  # Only create directory if path contains directory
            os.makedirs(dir_path, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot each equity curve
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for i, (strategy_name, equity_curve) in enumerate(equity_curves.items()):
            ax.plot(equity_curve.index, equity_curve.values, 
                   label=strategy_name.replace('_', ' ').title(),
                   color=colors[i % len(colors)], linewidth=2)
        
        # Format chart
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(loc='upper left', fontsize=11)
        
        # Format axes
        self.format_price_axis(ax)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45)
        
        # Save chart
        self.save_chart(fig, output_path)
        plt.close(fig)
        
        logger.info(f"Equity curve chart saved to: {output_path}")
    
    def create_trade_execution_chart(self,
                                   price_data: pd.DataFrame,
                                   trades: List[Dict[str, Any]],
                                   output_path: str,
                                   title: str = 'Trade Executions') -> None:
        """
        Create and save trade execution chart with buy/sell markers.
        
        Args:
            price_data: DataFrame with OHLCV data
            trades: List of trade dictionaries with entry/exit information
            output_path: Path to save the chart
            title: Chart title
            
        Raises:
            ValueError: If data is empty or output_path is invalid
        """
        if price_data.empty:
            raise ValueError("Price data cannot be empty")
        
        if not output_path:
            raise ValueError("Output path cannot be empty")
        
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(output_path)
        if dir_path:  # Only create directory if path contains directory
            os.makedirs(dir_path, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot price data
        ax.plot(price_data.index, price_data['Close'], 
               label='Close Price', color='#1f77b4', linewidth=1.5)
        
        # Add trade markers
        self.add_trade_markers(ax, trades, price_data)
        
        # Format chart
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (₹)', fontsize=12)
        ax.legend(loc='upper left', fontsize=11)
        
        # Format axes
        self.format_price_axis(ax)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45)
        
        # Save chart
        self.save_chart(fig, output_path)
        plt.close(fig)
        
        logger.info(f"Trade execution chart saved to: {output_path}")
    
    def add_trade_markers(self, ax, trades: List[Dict[str, Any]], 
                         price_data: pd.DataFrame) -> None:
        """
        Add buy and sell markers to the price chart.
        
        Args:
            ax: Matplotlib axes object
            trades: List of trade dictionaries
            price_data: DataFrame with price data for reference
        """
        if not trades:
            return
        
        # Separate entry and exit points
        buy_entries = []
        sell_entries = []
        long_exits = []
        short_exits = []
        
        for trade in trades:
            entry_date = trade['entry_datetime']
            exit_date = trade['exit_datetime']
            entry_price = trade['entry_price']
            exit_price = trade['exit_price']
            direction = trade['direction']
            
            if direction == 'LONG':
                buy_entries.append((entry_date, entry_price))
                long_exits.append((exit_date, exit_price))
            else:  # SHORT
                sell_entries.append((entry_date, entry_price))
                short_exits.append((exit_date, exit_price))
        
        # Plot buy entries (green triangles up)
        if buy_entries:
            dates, prices = zip(*buy_entries)
            ax.scatter(dates, prices, marker='^', color='green', 
                      s=100, label='Buy Entry', zorder=5)
        
        # Plot sell entries (red triangles down)
        if sell_entries:
            dates, prices = zip(*sell_entries)
            ax.scatter(dates, prices, marker='v', color='red', 
                      s=100, label='Sell Entry', zorder=5)
        
        # Plot long exits (red X)
        if long_exits:
            dates, prices = zip(*long_exits)
            ax.scatter(dates, prices, marker='x', color='red', 
                      s=80, label='Long Exit', zorder=5)
        
        # Plot short exits (green X)
        if short_exits:
            dates, prices = zip(*short_exits)
            ax.scatter(dates, prices, marker='x', color='green', 
                      s=80, label='Short Exit', zorder=5)
    
    def format_price_axis(self, ax) -> None:
        """
        Format Y-axis for price display with Indian Rupee formatting.
        
        Args:
            ax: Matplotlib axes object to format
        """
        def rupee_formatter(x, p):
            """Format price values with Indian Rupee symbol."""
            if x >= 100000:
                return f'₹{x/100000:.1f}L'
            elif x >= 1000:
                return f'₹{x/1000:.1f}K'
            else:
                return f'₹{x:.0f}'
        
        ax.yaxis.set_major_formatter(FuncFormatter(rupee_formatter))
    
    def save_chart(self, fig, output_path: str) -> None:
        """
        Save chart with high quality settings.
        
        Args:
            fig: Matplotlib figure object
            output_path: Path to save the chart
        """
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        logger.info(f"Chart saved with high quality to: {output_path}")