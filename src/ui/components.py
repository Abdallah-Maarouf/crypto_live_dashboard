"""
Reusable UI components for the Crypto Dashboard.

This module provides consistent, styled components that can be used
throughout the Streamlit application for displaying cryptocurrency data.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from .styles import get_color_for_change, get_change_class


def render_kpi_card(title: str, value: str, change: Optional[float] = None, 
                   high: Optional[str] = None, low: Optional[str] = None):
    """
    Render a KPI card with consistent styling for displaying key metrics.
    
    Args:
        title (str): The title/label for the metric
        value (str): The main value to display (formatted)
        change (float, optional): 24h percentage change
        high (str, optional): 24h high value (formatted)
        low (str, optional): 24h low value (formatted)
    """
    # Use Streamlit's built-in metric component
    if change is not None:
        change_text = f"{change:.2f}%"
        st.metric(
            label=title,
            value=value,
            delta=change_text
        )
    else:
        st.metric(
            label=title,
            value=value
        )
    
    # Add range information if provided
    if high and low:
        st.caption(f"24h Range: {low} - {high}")


def render_crypto_table(data: List[Dict[str, Any]], title: str = "Cryptocurrency Data"):
    """
    Render a styled table for displaying cryptocurrency data with color-coded changes.
    
    Args:
        data (List[Dict]): List of cryptocurrency data dictionaries
        title (str): Title for the table section
    """
    if not data:
        st.warning("No cryptocurrency data available to display.")
        return
    
    # Create section header
    st.subheader(title)
    
    # Prepare data for DataFrame
    table_data = []
    for coin in data:
        symbol = coin.get('symbol', 'N/A')
        price = coin.get('price', 0)
        change = coin.get('change_24h', 0)
        volume = coin.get('volume', 0)
        
        # Format values
        price_formatted = f"${price:,.2f}" if price else "N/A"
        change_formatted = f"{'+' if change >= 0 else ''}{change:.2f}%"
        volume_formatted = f"${volume:,.0f}" if volume else "N/A"
        
        table_data.append({
            'Symbol': symbol,
            'Price (USD)': price_formatted,
            '24h Change': change_formatted,
            'Volume': volume_formatted,
            '_change_value': change  # Hidden column for styling
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Function to style the dataframe
    def style_crypto_table(val, change_val):
        if 'Change' in str(val):
            if change_val >= 0:
                return 'color: #2ca02c; font-weight: 600;'
            else:
                return 'color: #d62728; font-weight: 600;'
        elif 'Symbol' in str(val):
            return 'font-weight: 700;'
        elif 'Price' in str(val):
            return 'font-weight: 600;'
        return ''
    
    # Apply styling and display
    styled_df = df.drop('_change_value', axis=1)
    
    # Use Streamlit's dataframe with custom styling
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Symbol': st.column_config.TextColumn(
                'Symbol',
                width='small'
            ),
            'Price (USD)': st.column_config.TextColumn(
                'Price (USD)',
                width='medium'
            ),
            '24h Change': st.column_config.TextColumn(
                '24h Change',
                width='small'
            ),
            'Volume': st.column_config.TextColumn(
                'Volume',
                width='large'
            )
        }
    )


def render_loading_state(message: str = "Loading data..."):
    """
    Render a consistent loading state with spinner and message.
    
    Args:
        message (str): Loading message to display
    """
    st.markdown(f"""
    <div class="loading-spinner">
        <div class="loading-text">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def render_error_message(message: str, error_type: str = "error"):
    """
    Render a styled error or warning message.
    
    Args:
        message (str): Error message to display
        error_type (str): Type of message ('error' or 'warning')
    """
    css_class = "error-message" if error_type == "error" else "warning-message"
    
    st.markdown(f"""
    <div class="{css_class}">
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_dashboard_header(title: str, subtitle: str):
    """
    Render the main dashboard header with title and subtitle.
    
    Args:
        title (str): Main dashboard title
        subtitle (str): Dashboard subtitle/description
    """
    st.title(title)
    st.markdown(f"*{subtitle}*")
    st.markdown("")


def render_metric_grid(metrics: List[Dict[str, Any]], columns: int = 2):
    """
    Render multiple KPI cards in a responsive grid layout.
    
    Args:
        metrics (List[Dict]): List of metric dictionaries with keys:
                             'title', 'value', 'change', 'high', 'low'
        columns (int): Number of columns in the grid
    """
    cols = st.columns(columns)
    
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            render_kpi_card(
                title=metric.get('title', ''),
                value=metric.get('value', ''),
                change=metric.get('change'),
                high=metric.get('high'),
                low=metric.get('low')
            )


def render_search_results(coin_data: Dict[str, Any]):
    """
    Render search results for a specific cryptocurrency.
    
    Args:
        coin_data (Dict): Dictionary containing coin information
    """
    if not coin_data:
        render_error_message("No data found for the searched cryptocurrency.", "warning")
        return
    
    st.markdown('<div class="section-header">Search Results</div>', unsafe_allow_html=True)
    
    # Create a single metric card for the searched coin
    render_kpi_card(
        title=f"{coin_data.get('symbol', 'N/A')} Price",
        value=f"${coin_data.get('price', 0):,.2f}",
        change=coin_data.get('change_24h', 0),
        high=f"${coin_data.get('high_24h', 0):,.2f}",
        low=f"${coin_data.get('low_24h', 0):,.2f}"
    )


def render_crypto_table(data: List[Dict[str, Any]], title: str = "Cryptocurrency Data"):
    """
    Render a styled table for displaying cryptocurrency data with color-coded changes.
    
    Args:
        data (List[Dict]): List of cryptocurrency data dictionaries
        title (str): Title for the table section
    """
    if not data:
        st.warning("No cryptocurrency data available to display.")
        return
    
    # Create section header
    st.subheader(title)
    
    # Prepare data for DataFrame
    table_data = []
    for coin in data:
        symbol = coin.get('symbol', 'N/A')
        price = coin.get('price', 0)
        change = coin.get('change_24h', 0)
        volume = coin.get('volume', 0)
        
        # Format values
        price_formatted = f"${price:,.2f}" if price else "N/A"
        change_formatted = f"{'+' if change >= 0 else ''}{change:.2f}%"
        volume_formatted = f"${volume:,.0f}" if volume else "N/A"
        
        table_data.append({
            'Symbol': symbol,
            'Price (USD)': price_formatted,
            '24h Change': change_formatted,
            'Volume (USD)': volume_formatted
        })
    
    # Create DataFrame and display
    df = pd.DataFrame(table_data)
    
    # Use Streamlit's dataframe with custom styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Symbol': st.column_config.TextColumn(
                'Symbol',
                width='small'
            ),
            'Price (USD)': st.column_config.TextColumn(
                'Price (USD)',
                width='medium'
            ),
            '24h Change': st.column_config.TextColumn(
                '24h Change',
                width='small'
            ),
            'Volume (USD)': st.column_config.TextColumn(
                'Volume (USD)',
                width='large'
            )
        }
    )


def render_portfolio_summary(portfolio_data: Dict[str, Any]):
    """
    Render portfolio summary with total value and breakdown.
    
    Args:
        portfolio_data (Dict): Portfolio data with total value and holdings
    """
    if not portfolio_data:
        render_error_message("No portfolio data available.", "warning")
        return
    
    st.markdown('<div class="section-header">Portfolio Summary</div>', unsafe_allow_html=True)
    
    # Total portfolio value card
    total_value = portfolio_data.get('total_value', 0)
    render_kpi_card(
        title="Total Portfolio Value",
        value=f"${total_value:,.2f}",
        change=portfolio_data.get('total_change_24h')
    )
    
    # Individual holdings table
    holdings = portfolio_data.get('holdings', [])
    if holdings:
        render_crypto_table(holdings, "Portfolio Holdings")