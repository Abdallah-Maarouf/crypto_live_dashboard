"""
Data processing and formatting utilities for cryptocurrency data.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import re


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
    percentage: float = 0.0


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


def validate_portfolio_input(symbol: str, quantity: str) -> Tuple[bool, str, Optional[float]]:
    """
    Validate portfolio input for symbol and quantity.
    
    Args:
        symbol: Cryptocurrency symbol
        quantity: Quantity as string input
        
    Returns:
        Tuple of (is_valid, error_message, parsed_quantity)
    """
    # Validate symbol format (letters only, 2-10 characters)
    if not symbol or not isinstance(symbol, str):
        return False, "Symbol is required", None
    
    symbol = symbol.strip().upper()
    if not re.match(r'^[A-Z]{2,10}$', symbol):
        return False, "Symbol must be 2-10 letters only", None
    
    # Validate quantity
    if not quantity or not isinstance(quantity, str):
        return False, "Quantity is required", None
    
    try:
        parsed_quantity = float(quantity.strip())
        if parsed_quantity <= 0:
            return False, "Quantity must be positive", None
        if parsed_quantity > 1e12:  # Reasonable upper limit
            return False, "Quantity is too large", None
        return True, "", parsed_quantity
    except ValueError:
        return False, "Quantity must be a valid number", None


def calculate_portfolio_value(holdings: List[Dict[str, Any]], prices: Dict[str, float]) -> Tuple[float, List[PortfolioHolding], List[str]]:
    """
    Calculate total portfolio value and individual coin breakdowns.
    
    Args:
        holdings: List of dictionaries with 'symbol' and 'quantity' keys
        prices: Dictionary mapping symbols to current prices
        
    Returns:
        Tuple of (total_value, portfolio_holdings, missing_symbols)
    """
    if not holdings:
        return 0.0, [], []
    
    portfolio_holdings = []
    missing_symbols = []
    total_value = 0.0
    
    # First pass: calculate individual values
    for holding in holdings:
        symbol = holding.get('symbol', '').upper()
        quantity = holding.get('quantity', 0)
        
        if symbol in prices:
            current_price = prices[symbol]
            current_value = quantity * current_price
            total_value += current_value
            
            portfolio_holdings.append(PortfolioHolding(
                symbol=symbol,
                quantity=quantity,
                current_value=current_value,
                percentage=0.0  # Will be calculated in second pass
            ))
        else:
            missing_symbols.append(symbol)
    
    # Second pass: calculate percentages
    if total_value > 0:
        for holding in portfolio_holdings:
            holding.percentage = (holding.current_value / total_value) * 100
    
    return total_value, portfolio_holdings, missing_symbols


def get_portfolio_breakdown(portfolio_holdings: List[PortfolioHolding]) -> Dict[str, Any]:
    """
    Get detailed portfolio breakdown with summary statistics.
    
    Args:
        portfolio_holdings: List of PortfolioHolding objects
        
    Returns:
        Dictionary with portfolio breakdown details
    """
    if not portfolio_holdings:
        return {
            'total_value': 0.0,
            'total_coins': 0,
            'holdings': [],
            'largest_holding': None,
            'smallest_holding': None
        }
    
    total_value = sum(holding.current_value for holding in portfolio_holdings)
    
    # Sort holdings by value (descending)
    sorted_holdings = sorted(portfolio_holdings, key=lambda x: x.current_value, reverse=True)
    
    breakdown = {
        'total_value': total_value,
        'total_coins': len(portfolio_holdings),
        'holdings': sorted_holdings,
        'largest_holding': sorted_holdings[0] if sorted_holdings else None,
        'smallest_holding': sorted_holdings[-1] if sorted_holdings else None
    }
    
    return breakdown