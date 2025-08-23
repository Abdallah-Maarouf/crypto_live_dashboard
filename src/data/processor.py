"""
Data processing and formatting utilities for cryptocurrency data.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd


@dataclass
class CoinData:
    """Data model for cryptocurrency information."""
    symbol: str
    price: float
    change_24h: float
    high_24h: float
    low_24h: float
    volume: float


@dataclass
class PortfolioHolding:
    """Data model for portfolio holdings."""
    symbol: str
    quantity: float
    current_value: float


def format_price_data(price: float) -> str:
    """
    Format price data with appropriate decimal places.
    
    Args:
        price: Raw price value
        
    Returns:
        Formatted price string with appropriate decimal places
    """
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    elif price >= 0.01:
        return f"${price:.6f}"
    else:
        return f"${price:.8f}"


def format_percentage_change(change: float) -> Tuple[str, str]:
    """
    Format percentage change with color coding logic.
    
    Args:
        change: Percentage change value
        
    Returns:
        Tuple of (formatted_string, color)
    """
    if change > 0:
        return f"+{change:.2f}%", "green"
    elif change < 0:
        return f"{change:.2f}%", "red"
    else:
        return f"{change:.2f}%", "gray"


def prepare_chart_data(klines_data: List[List]) -> pd.DataFrame:
    """
    Convert klines data to Plotly-compatible format.
    
    Args:
        klines_data: Raw klines data from Binance API
        
    Returns:
        DataFrame with OHLCV data formatted for Plotly
    """
    if not klines_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(klines_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Convert price columns to float
    price_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in price_columns:
        df[col] = df[col].astype(float)
    
    # Select only needed columns for chart
    chart_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
    
    return chart_df