"""
Live Crypto Dashboard - Main Streamlit Application

A real-time cryptocurrency analytics dashboard powered by the Binance API.
Displays live market data, historical charts, and portfolio tracking.
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional, List

# Import our custom modules
from src.api.binance_client import BinanceClient, BinanceAPIError
from src.ui.styles import inject_custom_css
from src.ui.components import (
    render_dashboard_header, 
    render_metric_grid, 
    render_error_message,
    render_loading_state
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Live Crypto Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
inject_custom_css()


@st.cache_data(ttl=30)  # Cache for 30 seconds
def fetch_btc_eth_data() -> Dict[str, Any]:
    """
    Fetch BTC and ETH ticker data from Binance API.
    
    Returns:
        Dict containing BTC and ETH data or error information
    """
    try:
        client = BinanceClient()
        
        # Fetch BTC and ETH data
        btc_data = client.get_ticker_24hr("BTCUSDT")
        eth_data = client.get_ticker_24hr("ETHUSDT")
        
        return {
            'success': True,
            'btc': btc_data,
            'eth': eth_data
        }
        
    except BinanceAPIError as e:
        logger.error(f"Binance API error: {e}")
        return {
            'success': False,
            'error': f"API Error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }


@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_top_10_cryptos() -> Dict[str, Any]:
    """
    Fetch top 10 cryptocurrencies by volume from Binance API.
    
    Returns:
        Dict containing top 10 crypto data or error information
    """
    try:
        client = BinanceClient()
        
        # Fetch top 10 cryptos by volume
        top_cryptos = client.get_top_volume_symbols(limit=10)
        
        return {
            'success': True,
            'data': top_cryptos
        }
        
    except BinanceAPIError as e:
        logger.error(f"Binance API error fetching top cryptos: {e}")
        return {
            'success': False,
            'error': f"API Error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error fetching top cryptos: {e}")
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }


def format_ticker_data(ticker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format raw ticker data for display.
    
    Args:
        ticker_data: Raw ticker data from Binance API
        
    Returns:
        Formatted data dictionary
    """
    try:
        return {
            'symbol': ticker_data['symbol'].replace('USDT', ''),
            'price': float(ticker_data['lastPrice']),
            'change_24h': float(ticker_data['priceChangePercent']),
            'high_24h': float(ticker_data['highPrice']),
            'low_24h': float(ticker_data['lowPrice']),
            'volume': float(ticker_data['volume'])
        }
    except (KeyError, ValueError) as e:
        logger.error(f"Error formatting ticker data: {e}")
        return {
            'symbol': 'N/A',
            'price': 0.0,
            'change_24h': 0.0,
            'high_24h': 0.0,
            'low_24h': 0.0,
            'volume': 0.0
        }


def format_top_crypto_data(crypto_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format raw top crypto data for table display.
    
    Args:
        crypto_list: List of raw ticker data from Binance API
        
    Returns:
        List of formatted data dictionaries for table display
    """
    formatted_data = []
    
    for crypto in crypto_list:
        try:
            formatted_crypto = {
                'symbol': crypto['symbol'].replace('USDT', ''),
                'price': float(crypto['lastPrice']),
                'change_24h': float(crypto['priceChangePercent']),
                'volume': float(crypto['quoteVolume'])  # USD volume
            }
            formatted_data.append(formatted_crypto)
        except (KeyError, ValueError) as e:
            logger.error(f"Error formatting crypto data: {e}")
            continue
    
    return formatted_data


def render_homepage():
    """
    Render the main dashboard homepage with BTC and ETH KPI cards and top 10 table.
    """
    # Dashboard header
    render_dashboard_header(
        title="Live Crypto Dashboard",
        subtitle="Real-time cryptocurrency market data powered by Binance API"
    )
    
    # Add refresh button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Fetch BTC/ETH data with loading state
    with st.spinner("Loading market data..."):
        data = fetch_btc_eth_data()
    
    if not data['success']:
        # Handle API errors
        render_error_message(
            f"Unable to fetch market data: {data['error']}", 
            "error"
        )
        
        # Show fallback message
        st.info("""
        **Dashboard temporarily unavailable**
        
        The Binance API is currently unavailable. This could be due to:
        - Network connectivity issues
        - API rate limiting
        - Temporary service outage
        
        Please try refreshing the page in a few moments.
        """)
        return
    
    # Format the BTC/ETH data
    btc_formatted = format_ticker_data(data['btc'])
    eth_formatted = format_ticker_data(data['eth'])
    
    # Create KPI metrics for display
    metrics = [
        {
            'title': f"Bitcoin ({btc_formatted['symbol']})",
            'value': f"${btc_formatted['price']:,.2f}",
            'change': btc_formatted['change_24h'],
            'high': f"${btc_formatted['high_24h']:,.2f}",
            'low': f"${btc_formatted['low_24h']:,.2f}"
        },
        {
            'title': f"Ethereum ({eth_formatted['symbol']})",
            'value': f"${eth_formatted['price']:,.2f}",
            'change': eth_formatted['change_24h'],
            'high': f"${eth_formatted['high_24h']:,.2f}",
            'low': f"${eth_formatted['low_24h']:,.2f}"
        }
    ]
    
    # Render KPI cards in a 2-column grid
    render_metric_grid(metrics, columns=2)
    
    st.markdown("---")
    
    # Top 10 Cryptocurrencies Section
    st.markdown("### 📊 Top 10 Cryptocurrencies by Volume")
    
    # Add refresh button specifically for top 10 table
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Top 10", use_container_width=True, key="refresh_top10"):
            # Clear only the top 10 cache
            fetch_top_10_cryptos.clear()
            st.rerun()
    
    # Fetch top 10 data
    with st.spinner("Loading top cryptocurrencies..."):
        top_10_data = fetch_top_10_cryptos()
    
    if top_10_data['success']:
        # Format the data for table display
        formatted_top_10 = format_top_crypto_data(top_10_data['data'])
        
        if formatted_top_10:
            # Render the crypto table
            from src.ui.components import render_crypto_table
            render_crypto_table(formatted_top_10, "Top 10 Cryptocurrencies by 24h Volume")
        else:
            render_error_message("No cryptocurrency data available to display.", "warning")
    else:
        # Handle API errors for top 10
        render_error_message(
            f"Unable to fetch top cryptocurrencies: {top_10_data['error']}", 
            "warning"
        )
        st.info("The top 10 cryptocurrencies table is temporarily unavailable. BTC and ETH data above is still live.")
    
    # Add last update timestamp
    st.markdown("---")
    st.caption("💡 Data updates automatically. BTC/ETH every 30 seconds, Top 10 every minute. Use refresh buttons for immediate updates.")
    
    # Add feature preview section
    st.markdown("### 🚀 Coming Soon")
    st.info("""
    **Additional features in development:**
    - 📈 Interactive historical price charts  
    - 🔍 Cryptocurrency search functionality
    - 💼 Portfolio tracker with real-time calculations
    - 📱 Enhanced mobile experience
    """)


def main():
    """
    Main application entry point.
    """
    try:
        render_homepage()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        render_error_message(
            "An unexpected error occurred. Please refresh the page and try again.",
            "error"
        )
        
        # Show error details in development
        if st.secrets.get("debug", False):
            st.exception(e)


if __name__ == "__main__":
    main()