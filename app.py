"""
Live Crypto Dashboard - Main Streamlit Application

A real-time cryptocurrency analytics dashboard powered by the Binance API.
Displays live market data, historical charts, and portfolio tracking.

Optimized for Streamlit Cloud deployment.
"""

import streamlit as st
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Add src directory to Python path for deployment compatibility
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our custom modules with error handling for deployment
try:
    from src.api.binance_client import BinanceClient, BinanceAPIError
    from src.ui.styles import inject_custom_css, inject_mobile_meta_tags
    from src.ui.components import (
        render_dashboard_header, 
        render_metric_grid, 
        render_error_message,
        render_loading_state,
        render_price_chart,
        render_chart_controls
    )
    from src.data.processor import prepare_chart_data
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("Please ensure all required modules are properly installed.")
    st.stop()

# Configure logging for deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Deployment environment detection
IS_CLOUD_DEPLOYMENT = os.getenv('STREAMLIT_SHARING_MODE') is not None or 'streamlit.io' in os.getenv('HOSTNAME', '')

# Page configuration optimized for deployment
st.set_page_config(
    page_title="Live Crypto Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/crypto-dashboard/crypto-dashboard',
        'Report a bug': 'https://github.com/crypto-dashboard/crypto-dashboard/issues',
        'About': "Live Crypto Dashboard - Real-time cryptocurrency analytics powered by Binance API"
    }
)

# Log deployment environment
if IS_CLOUD_DEPLOYMENT:
    logger.info("Running in Streamlit Cloud deployment mode")
else:
    logger.info("Running in local development mode")

# Inject mobile meta tags and custom CSS
inject_mobile_meta_tags()
inject_custom_css()


@st.cache_data(ttl=30, show_spinner=False)  # Cache for 30 seconds, optimized for deployment
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
            'eth': eth_data,
            'timestamp': datetime.now()
        }
        
    except BinanceAPIError as e:
        logger.error(f"Binance API error: {e}")
        return {
            'success': False,
            'error': f"API Error: {str(e)}",
            'timestamp': datetime.now()
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'timestamp': datetime.now()
        }


@st.cache_data(ttl=60, show_spinner=False)  # Cache for 1 minute, optimized for deployment
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
            'data': top_cryptos,
            'timestamp': datetime.now()
        }
        
    except BinanceAPIError as e:
        logger.error(f"Binance API error fetching top cryptos: {e}")
        return {
            'success': False,
            'error': f"API Error: {str(e)}",
            'timestamp': datetime.now()
        }
    except Exception as e:
        logger.error(f"Unexpected error fetching top cryptos: {e}")
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'timestamp': datetime.now()
        }


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour - symbols don't change frequently, optimized for deployment
def fetch_available_symbols() -> List[str]:
    """
    Fetch available cryptocurrency symbols for chart selection.
    
    Returns:
        List of available symbols (without USDT suffix)
    """
    try:
        client = BinanceClient()
        exchange_info = client.get_exchange_info()
        
        # Extract USDT trading pairs and remove common stablecoins
        symbols = []
        excluded_symbols = {'USDCUSDT', 'BUSDUSDT', 'TUSDUSDT', 'DAIUSDT', 'USDPUSDT'}
        
        for symbol_info in exchange_info.get('symbols', []):
            symbol = symbol_info.get('symbol', '')
            status = symbol_info.get('status', '')
            
            # Only include active USDT pairs, exclude stablecoins
            if (symbol.endswith('USDT') and 
                status == 'TRADING' and 
                symbol not in excluded_symbols):
                # Remove USDT suffix for display
                clean_symbol = symbol.replace('USDT', '')
                symbols.append(clean_symbol)
        
        # Sort alphabetically and return top symbols for better UX
        symbols.sort()
        
        # Prioritize major cryptocurrencies at the top
        priority_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOT', 'AVAX', 'MATIC', 'LINK']
        prioritized_symbols = []
        
        # Add priority symbols first (if they exist)
        for priority in priority_symbols:
            if priority in symbols:
                prioritized_symbols.append(priority)
                symbols.remove(priority)
        
        # Add remaining symbols
        prioritized_symbols.extend(symbols)
        
        return prioritized_symbols[:50]  # Limit to 50 symbols for better performance
        
    except Exception as e:
        logger.error(f"Error fetching available symbols: {e}")
        # Return default symbols as fallback
        return ['BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOT', 'AVAX', 'MATIC', 'LINK']


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, optimized for deployment
def fetch_historical_data(symbol: str, timeframe: str) -> Dict[str, Any]:
    """
    Fetch historical candlestick data for a cryptocurrency.
    
    Args:
        symbol: Cryptocurrency symbol (without USDT)
        timeframe: Timeframe (1h, 4h, 1d, 1w)
        
    Returns:
        Dict containing historical data or error information
    """
    try:
        client = BinanceClient()
        
        # Add USDT suffix for API call
        trading_pair = f"{symbol.upper()}USDT"
        
        # Determine limit based on timeframe for reasonable chart data
        limit_map = {
            '1h': 168,   # 1 week of hourly data
            '4h': 168,   # 4 weeks of 4-hour data  
            '1d': 90,    # 3 months of daily data
            '1w': 52     # 1 year of weekly data
        }
        
        limit = limit_map.get(timeframe, 100)
        
        # Fetch klines data
        klines_data = client.get_klines(trading_pair, timeframe, limit)
        
        if not klines_data:
            return {
                'success': False,
                'error': f"No historical data available for {symbol}",
                'timestamp': datetime.now()
            }
        
        # Process the data using our data processor
        chart_data = prepare_chart_data(klines_data)
        
        return {
            'success': True,
            'data': chart_data,
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now()
        }
        
    except BinanceAPIError as e:
        logger.error(f"Binance API error fetching historical data for {symbol}: {e}")
        return {
            'success': False,
            'error': f"API Error: {str(e)}",
            'timestamp': datetime.now()
        }
    except Exception as e:
        logger.error(f"Unexpected error fetching historical data for {symbol}: {e}")
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'timestamp': datetime.now()
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


def check_deployment_health() -> Dict[str, Any]:
    """
    Perform deployment health checks to ensure all systems are operational.
    
    Returns:
        Dict containing health check results
    """
    health_status = {
        'api_connectivity': False,
        'modules_loaded': True,  # If we got here, modules loaded successfully
        'cache_system': False,
        'errors': []
    }
    
    try:
        # Test API connectivity
        client = BinanceClient()
        test_response = client.get_ticker_24hr("BTCUSDT")
        if test_response and 'lastPrice' in test_response:
            health_status['api_connectivity'] = True
        else:
            health_status['errors'].append("API response format unexpected")
    except Exception as e:
        health_status['errors'].append(f"API connectivity failed: {str(e)}")
    
    try:
        # Test cache system
        @st.cache_data(ttl=1)
        def test_cache():
            return {"test": "success"}
        
        result = test_cache()
        if result.get("test") == "success":
            health_status['cache_system'] = True
        else:
            health_status['errors'].append("Cache system test failed")
    except Exception as e:
        health_status['errors'].append(f"Cache system error: {str(e)}")
    
    return health_status


def initialize_session_state():
    """
    Initialize session state variables for data caching and fallback.
    """
    if 'last_btc_eth_data' not in st.session_state:
        st.session_state.last_btc_eth_data = None
    
    if 'last_top_10_data' not in st.session_state:
        st.session_state.last_top_10_data = None
    
    if 'deployment_health_checked' not in st.session_state:
        st.session_state.deployment_health_checked = False
        
    # Perform health check on first load in deployment
    if IS_CLOUD_DEPLOYMENT and not st.session_state.deployment_health_checked:
        health_status = check_deployment_health()
        st.session_state.deployment_health_checked = True
        
        # Log health check results
        if health_status['api_connectivity'] and health_status['cache_system']:
            logger.info("✅ Deployment health check passed")
        else:
            logger.warning(f"⚠️ Deployment health check issues: {health_status['errors']}")
            
        # Store health status for potential display
        st.session_state.health_status = health_status





def render_refresh_controls():
    """
    Render mobile-optimized manual refresh controls.
    """
    # Mobile-first design: full-width button with better touch target
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 Refresh All Data", use_container_width=True, type="secondary"):
            # Clear all cached data
            st.cache_data.clear()
            try:
                st.rerun()
            except Exception:
                # Fallback: just clear cache
                pass
    
    # Add last update info for mobile users
    st.caption("💡 Data refreshes automatically: BTC/ETH (30s), Top 10 (60s), Charts (5min)")


def render_homepage():
    """
    Render the main dashboard homepage with BTC and ETH KPI cards and top 10 table.
    """
    # Initialize session state
    initialize_session_state()
    
    # Dashboard header
    render_dashboard_header(
        title="Live Crypto Dashboard",
        subtitle="Real-time cryptocurrency market data powered by Binance API"
    )
    
    # Manual refresh controls
    render_refresh_controls()
    
    st.markdown("---")
    
    # Fetch BTC/ETH data with loading state
    loading_placeholder = st.empty()
    
    with loading_placeholder:
        with st.spinner("🔄 Loading market data..."):
            data = fetch_btc_eth_data()
    
    # Clear loading placeholder
    loading_placeholder.empty()
    
    if not data['success']:
        # Try to use last successful data if available
        if st.session_state.last_btc_eth_data and st.session_state.last_btc_eth_data['success']:
            st.warning("⚠️ Using cached data due to API error. Data may be stale.")
            data = st.session_state.last_btc_eth_data
        else:
            # Handle API errors with no fallback
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
    else:
        # Store successful data for fallback
        st.session_state.last_btc_eth_data = data
    
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
    
    # Fetch top 10 data with loading state
    loading_placeholder_top10 = st.empty()
    
    with loading_placeholder_top10:
        with st.spinner("🔄 Loading top cryptocurrencies..."):
            top_10_data = fetch_top_10_cryptos()
    
    # Clear loading placeholder
    loading_placeholder_top10.empty()
    
    if top_10_data['success']:
        # Store successful data for fallback
        st.session_state.last_top_10_data = top_10_data
        
        # Format the data for table display
        formatted_top_10 = format_top_crypto_data(top_10_data['data'])
        
        if formatted_top_10:
            # Render the crypto table
            from src.ui.components import render_crypto_table
            render_crypto_table(formatted_top_10, "Top 10 Cryptocurrencies by 24h Volume")
        else:
            render_error_message("No cryptocurrency data available to display.", "warning")
    else:
        # Try to use last successful data if available
        if st.session_state.last_top_10_data and st.session_state.last_top_10_data['success']:
            st.warning("⚠️ Using cached top 10 data due to API error. Data may be stale.")
            cached_data = st.session_state.last_top_10_data
            
            # Format and display cached data
            formatted_top_10 = format_top_crypto_data(cached_data['data'])
            if formatted_top_10:
                from src.ui.components import render_crypto_table
                render_crypto_table(formatted_top_10, "Top 10 Cryptocurrencies by 24h Volume (Cached)")
        else:
            # Handle API errors for top 10 with no fallback
            render_error_message(
                f"Unable to fetch top cryptocurrencies: {top_10_data['error']}", 
                "warning"
            )
            st.info("The top 10 cryptocurrencies table is temporarily unavailable. BTC and ETH data above is still live.")
    
    st.markdown("---")
    
    # Historical Price Charts Section
    st.markdown("### 📈 Historical Price Charts")
    
    # Fetch available symbols for dropdown
    with st.spinner("🔄 Loading available cryptocurrencies..."):
        available_symbols = fetch_available_symbols()
    
    if available_symbols:
        # Render chart controls
        selected_symbol, selected_timeframe = render_chart_controls(available_symbols)
        
        if selected_symbol and selected_timeframe:
            # Fetch historical data
            with st.spinner(f"🔄 Loading {selected_symbol} chart data..."):
                historical_data = fetch_historical_data(selected_symbol, selected_timeframe)
            
            if historical_data['success']:
                # Render the price chart
                render_price_chart(
                    chart_data=historical_data['data'],
                    symbol=selected_symbol,
                    timeframe=selected_timeframe
                )
                
                # Add chart info
                st.caption(f"💡 Chart shows {selected_symbol} price data with {selected_timeframe} intervals. Data is cached for 5 minutes.")
                
            else:
                # Handle chart data errors
                render_error_message(
                    f"Unable to load chart data for {selected_symbol}: {historical_data['error']}", 
                    "warning"
                )
                st.info(f"Historical data for {selected_symbol} may not be available or the symbol might not be supported. Try selecting a different cryptocurrency.")
        
    else:
        render_error_message("Unable to load available cryptocurrencies for chart selection.", "warning")
        st.info("Chart functionality is temporarily unavailable. Please try refreshing the page.")
    
    st.markdown("---")
    
    # Portfolio Tracker Section
    from src.ui.components import render_portfolio_input_form, render_portfolio_tracker
    
    # Render portfolio input form
    portfolio_holdings = render_portfolio_input_form()
    
    # If there are holdings, fetch prices and display portfolio tracker
    if portfolio_holdings:
        # Extract unique symbols from holdings
        portfolio_symbols = list(set([holding['symbol'] for holding in portfolio_holdings]))
        
        # Fetch current prices for portfolio symbols
        portfolio_prices = {}
        
        with st.spinner("🔄 Fetching portfolio prices..."):
            try:
                from src.api.binance_client import BinanceClient
                client = BinanceClient()
                
                for symbol in portfolio_symbols:
                    try:
                        # Add USDT suffix for API call
                        trading_pair = f"{symbol}USDT"
                        ticker_data = client.get_ticker_24hr(trading_pair)
                        portfolio_prices[symbol] = float(ticker_data['lastPrice'])
                    except Exception as e:
                        logger.warning(f"Could not fetch price for {symbol}: {e}")
                        # Symbol will be handled as missing in the portfolio tracker
                        continue
                
            except Exception as e:
                logger.error(f"Error fetching portfolio prices: {e}")
                st.error("❌ Unable to fetch current prices for portfolio calculation. Please try again later.")
                portfolio_prices = {}
        
        # Render portfolio tracker with fetched prices
        if portfolio_prices:
            render_portfolio_tracker(portfolio_holdings, portfolio_prices)
        else:
            st.warning("⚠️ Unable to fetch prices for any of your portfolio holdings. Please check your symbols and try again.")
    
    # Add last update timestamp
    st.markdown("---")
    
    # Show data refresh info
    st.caption("💡 Data is cached for performance: BTC/ETH for 30 seconds, Top 10 for 60 seconds, Charts for 5 minutes. Use 'Refresh All Data' button for immediate updates.")
    
    # Add feature preview section
    st.markdown("### 🚀 Coming Soon")
    st.info("""
    **Additional features in development:**
    - 🔍 Cryptocurrency search functionality
    - 📱 Enhanced mobile experience
    """)


def main():
    """
    Main application entry point with deployment-specific error handling.
    """
    try:
        # Initialize session state and perform health checks
        initialize_session_state()
        
        # Show deployment status if there are health issues
        if (IS_CLOUD_DEPLOYMENT and 
            hasattr(st.session_state, 'health_status') and 
            st.session_state.health_status['errors']):
            
            with st.expander("⚠️ System Status", expanded=False):
                st.warning("Some system components may be experiencing issues:")
                for error in st.session_state.health_status['errors']:
                    st.text(f"• {error}")
                st.info("The dashboard will attempt to function with available components.")
        
        # Render main application
        render_homepage()
        
        # Add deployment footer
        if IS_CLOUD_DEPLOYMENT:
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
                "🚀 Deployed on Streamlit Cloud | "
                "📊 Powered by Binance API | "
                "⚡ Real-time Data"
                "</div>", 
                unsafe_allow_html=True
            )
        
    except ImportError as e:
        logger.error(f"Import error in deployment: {e}")
        st.error("❌ **Deployment Error**: Required modules could not be loaded.")
        st.error("This may be due to missing dependencies or incorrect file structure.")
        st.code(f"Error details: {str(e)}")
        st.stop()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        
        # Enhanced error handling for deployment
        if IS_CLOUD_DEPLOYMENT:
            st.error("❌ **Application Error**: The dashboard encountered an unexpected error.")
            st.error("This may be temporary. Please try refreshing the page.")
            
            # Provide fallback information
            st.info("""
            **Troubleshooting Tips:**
            - Refresh the page to retry
            - Check if the Binance API is accessible
            - Try again in a few minutes
            """)
            
            # Log error details but don't expose them to users in production
            logger.error(f"Full error details: {str(e)}")
            
        else:
            # Development mode - show full error details
            render_error_message(
                "An unexpected error occurred. Please refresh the page and try again.",
                "error"
            )
            
            # Show error details in development
            try:
                if st.secrets.get("debug", False):
                    st.exception(e)
            except:
                # No secrets file available, show exception anyway in dev
                st.exception(e)


if __name__ == "__main__":
    main()