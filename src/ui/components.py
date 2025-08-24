"""
Reusable UI components for the Crypto Dashboard.

This module provides consistent, styled components that can be used
throughout the Streamlit application for displaying cryptocurrency data.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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


def render_price_chart(chart_data: pd.DataFrame, symbol: str, timeframe: str) -> None:
    """
    Render an interactive Plotly candlestick chart for cryptocurrency price data.
    
    Args:
        chart_data (pd.DataFrame): DataFrame with OHLCV data (columns: timestamp, open, high, low, close, volume)
        symbol (str): Cryptocurrency symbol for chart title
        timeframe (str): Timeframe for chart title (e.g., '1h', '4h', '1d', '1w')
    """
    if chart_data.empty:
        render_error_message("No historical data available for the selected cryptocurrency and timeframe.", "warning")
        return
    
    try:
        # Create candlestick chart
        fig = go.Figure(data=go.Candlestick(
            x=chart_data['timestamp'],
            open=chart_data['open'],
            high=chart_data['high'],
            low=chart_data['low'],
            close=chart_data['close'],
            name=f"{symbol} Price"
        ))
        
        # Add volume as a secondary trace (bar chart)
        fig.add_trace(go.Bar(
            x=chart_data['timestamp'],
            y=chart_data['volume'],
            name="Volume",
            yaxis="y2",
            opacity=0.3,
            marker_color='rgba(158,202,225,0.8)',
            hoverinfo='x+y+name'
        ))
        
        # Update layout for better appearance
        fig.update_layout(
            title=f"{symbol} Price Chart ({timeframe})",
            title_font_size=20,
            title_x=0.5,
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            template="plotly_white",
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode='x'
        )
        
        # Customize candlestick colors
        fig.update_traces(
            increasing_line_color='#2ca02c',
            decreasing_line_color='#d62728',
            selector=dict(type='candlestick')
        )
        
        # Remove range slider for cleaner look
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        render_error_message(f"Error rendering chart: {str(e)}", "error")


def render_chart_controls(available_symbols: List[str]) -> tuple[str, str]:
    """
    Render cryptocurrency selection dropdown and timeframe selector controls.
    
    Args:
        available_symbols (List[str]): List of available cryptocurrency symbols
        
    Returns:
        tuple: (selected_symbol, selected_timeframe)
    """
    # Define available timeframes with labels
    timeframe_options = {
        '1h': '1 Hour',
        '4h': '4 Hours', 
        '1d': '1 Day',
        '1w': '1 Week'
    }
    
    # Create two columns for controls
    col1, col2 = st.columns(2)
    
    with col1:
        selected_symbol = st.selectbox(
            "Select Cryptocurrency",
            options=available_symbols,
            index=0 if available_symbols else None,
            help="Choose a cryptocurrency to view its historical price chart"
        )
    
    with col2:
        selected_timeframe_key = st.selectbox(
            "Select Timeframe",
            options=list(timeframe_options.keys()),
            format_func=lambda x: timeframe_options[x],
            index=2,  # Default to '1d' (1 Day)
            help="Choose the timeframe for the candlestick chart"
        )
    
    return selected_symbol, selected_timeframe_key