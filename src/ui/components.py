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
    Render a mobile-optimized table for displaying cryptocurrency data with color-coded changes.
    
    Args:
        data (List[Dict]): List of cryptocurrency data dictionaries
        title (str): Title for the table section
    """
    if not data:
        st.warning("No cryptocurrency data available to display.")
        return
    
    # Create section header
    st.subheader(title)
    
    # Add mobile-friendly table container
    st.markdown('<div class="crypto-table">', unsafe_allow_html=True)
    
    # Prepare data for DataFrame
    table_data = []
    for coin in data:
        symbol = coin.get('symbol', 'N/A')
        price = coin.get('price', 0)
        change = coin.get('change_24h', 0)
        volume = coin.get('volume', 0)
        
        # Format values with mobile-friendly precision
        if price >= 1:
            price_formatted = f"${price:,.2f}"
        elif price >= 0.01:
            price_formatted = f"${price:.4f}"
        else:
            price_formatted = f"${price:.6f}"
            
        change_formatted = f"{'+' if change >= 0 else ''}{change:.2f}%"
        
        # Format volume with appropriate units for mobile
        if volume >= 1e9:
            volume_formatted = f"${volume/1e9:.1f}B"
        elif volume >= 1e6:
            volume_formatted = f"${volume/1e6:.1f}M"
        elif volume >= 1e3:
            volume_formatted = f"${volume/1e3:.1f}K"
        else:
            volume_formatted = f"${volume:,.0f}" if volume else "N/A"
        
        table_data.append({
            'Symbol': symbol,
            'Price': price_formatted,
            '24h Change': change_formatted,
            'Volume': volume_formatted,
            '_change_value': change,  # Hidden column for styling
            '_price_value': price     # Hidden column for sorting
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Mobile-optimized column configuration
    column_config = {
        'Symbol': st.column_config.TextColumn(
            'Symbol',
            width='small',
            help="Cryptocurrency symbol"
        ),
        'Price': st.column_config.TextColumn(
            'Price (USD)',
            width='medium',
            help="Current price in USD"
        ),
        '24h Change': st.column_config.TextColumn(
            '24h Change',
            width='small',
            help="24-hour price change percentage"
        ),
        'Volume': st.column_config.TextColumn(
            'Volume (24h)',
            width='small',
            help="24-hour trading volume"
        )
    }
    
    # Display the dataframe with mobile optimizations
    st.dataframe(
        df.drop(['_change_value', '_price_value'], axis=1),
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
        height=400  # Fixed height for better mobile scrolling
    )
    
    # Close table container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add mobile-friendly table navigation hint
    st.caption("💡 Swipe horizontally to view all columns on mobile devices")


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
    Optimized for both desktop and mobile viewing.
    
    Args:
        chart_data (pd.DataFrame): DataFrame with OHLCV data (columns: timestamp, open, high, low, close, volume)
        symbol (str): Cryptocurrency symbol for chart title
        timeframe (str): Timeframe for chart title (e.g., '1h', '4h', '1d', '1w')
    """
    if chart_data.empty:
        render_error_message("No historical data available for the selected cryptocurrency and timeframe.", "warning")
        return
    
    try:
        from .styles import get_mobile_optimized_chart_config, get_mobile_chart_layout
        
        # Create candlestick chart with proper hover configuration
        fig = go.Figure(data=go.Candlestick(
            x=chart_data['timestamp'],
            open=chart_data['open'],
            high=chart_data['high'],
            low=chart_data['low'],
            close=chart_data['close'],
            name=f"{symbol} Price",
            hoverinfo='x+y+name'
        ))
        
        # Add volume as a secondary trace (bar chart)
        fig.add_trace(go.Bar(
            x=chart_data['timestamp'],
            y=chart_data['volume'],
            name="Volume",
            yaxis="y2",
            opacity=0.3,
            marker_color='rgba(158,202,225,0.8)',
            hovertemplate='<b>Volume</b><br>' +
                         'Date: %{x}<br>' +
                         'Volume: %{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
        
        # Get mobile-optimized layout
        mobile_layout = get_mobile_chart_layout()
        
        # Update layout for responsive design
        fig.update_layout(
            title=f"{symbol} Price Chart ({timeframe})",
            title_font_size=mobile_layout['title']['font']['size'],
            title_x=mobile_layout['title']['x'],
            title_xanchor=mobile_layout['title']['xanchor'],
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False,
                tickfont=dict(size=8)
            ),
            template="plotly_white",
            height=mobile_layout['height'],
            showlegend=True,
            legend=mobile_layout['legend'],
            margin=mobile_layout['margin'],
            hovermode=mobile_layout['hovermode'],
            dragmode=mobile_layout['dragmode'],
            font=mobile_layout['font']
        )
        
        # Update axis styling for mobile
        fig.update_xaxes(
            title_font=mobile_layout['xaxis']['title']['font'],
            tickfont=mobile_layout['xaxis']['tickfont'],
            showgrid=mobile_layout['xaxis']['showgrid'],
            gridwidth=mobile_layout['xaxis']['gridwidth']
        )
        
        fig.update_yaxes(
            title_font=mobile_layout['yaxis']['title']['font'],
            tickfont=mobile_layout['yaxis']['tickfont'],
            showgrid=mobile_layout['yaxis']['showgrid'],
            gridwidth=mobile_layout['yaxis']['gridwidth']
        )
        
        # Customize candlestick colors
        fig.update_traces(
            increasing_line_color='#2ca02c',
            decreasing_line_color='#d62728',
            selector=dict(type='candlestick')
        )
        
        # Remove range slider for cleaner mobile look
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        # Get mobile-optimized config
        mobile_config = get_mobile_optimized_chart_config()
        
        # Display the chart with mobile-optimized configuration
        st.plotly_chart(
            fig, 
            use_container_width=True,
            config=mobile_config
        )
        
    except Exception as e:
        render_error_message(f"Error rendering chart: {str(e)}", "error")


def render_chart_controls(available_symbols: List[str]) -> tuple[str, str]:
    """
    Render mobile-optimized cryptocurrency selection dropdown and timeframe selector controls.
    
    Args:
        available_symbols (List[str]): List of available cryptocurrency symbols
        
    Returns:
        tuple: (selected_symbol, selected_timeframe)
    """
    # Define available timeframes with mobile-friendly labels
    timeframe_options = {
        '1h': '1H',
        '4h': '4H', 
        '1d': '1D',
        '1w': '1W'
    }
    
    # Create responsive columns - stack on mobile
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_symbol = st.selectbox(
            "📈 Cryptocurrency",
            options=available_symbols,
            index=0 if available_symbols else None,
            help="Choose a cryptocurrency to view its historical price chart",
            key="chart_symbol_selector"
        )
    
    with col2:
        selected_timeframe_key = st.selectbox(
            "⏱️ Timeframe",
            options=list(timeframe_options.keys()),
            format_func=lambda x: timeframe_options[x],
            index=2,  # Default to '1d' (1 Day)
            help="Choose the timeframe for the candlestick chart",
            key="chart_timeframe_selector"
        )
    
    # Add helpful hint for mobile users
    st.caption("💡 Use the dropdowns above to select cryptocurrency and timeframe for the chart")
    
    return selected_symbol, selected_timeframe_key


def render_portfolio_input_form() -> List[Dict[str, Any]]:
    """
    Render mobile-optimized portfolio input form for cryptocurrency holdings.
    
    Returns:
        List of portfolio holdings with symbol and quantity
    """
    st.markdown("### 💼 Portfolio Tracker")
    st.markdown("Enter your cryptocurrency holdings to track your portfolio value in real-time.")
    
    # Initialize session state for portfolio holdings
    if 'portfolio_holdings' not in st.session_state:
        st.session_state.portfolio_holdings = []
    
    # Add new holding form with mobile-optimized layout
    with st.expander("➕ Add New Holding", expanded=len(st.session_state.portfolio_holdings) == 0):
        # Mobile-first: stack inputs vertically on small screens
        col1, col2 = st.columns([1, 1])
        
        with col1:
            new_symbol = st.text_input(
                "💰 Crypto Symbol",
                placeholder="BTC, ETH, ADA...",
                help="Enter the symbol without USDT (e.g., BTC for Bitcoin)",
                key="new_symbol_input",
                max_chars=10
            )
        
        with col2:
            new_quantity = st.text_input(
                "📊 Quantity",
                placeholder="0.5, 10.25...",
                help="Enter the amount you own",
                key="new_quantity_input"
            )
        
        # Full-width add button for better mobile experience
        add_button = st.button("➕ Add to Portfolio", type="primary", use_container_width=True)
        
        # Handle adding new holding
        if add_button:
            from src.data.processor import validate_portfolio_input
            
            is_valid, error_message, parsed_quantity = validate_portfolio_input(new_symbol, new_quantity)
            
            if is_valid:
                # Check if symbol already exists
                existing_symbols = [h['symbol'] for h in st.session_state.portfolio_holdings]
                if new_symbol.upper() in existing_symbols:
                    st.error(f"❌ {new_symbol.upper()} is already in your portfolio. Remove it first to update the quantity.")
                else:
                    # Add new holding
                    st.session_state.portfolio_holdings.append({
                        'symbol': new_symbol.upper(),
                        'quantity': parsed_quantity
                    })
                    st.success(f"✅ Added {parsed_quantity} {new_symbol.upper()} to your portfolio!")
                    
                    # Clear input fields by rerunning
                    try:
                        st.rerun()
                    except Exception:
                        # Fallback: just show success message without rerun
                        pass
            else:
                st.error(f"❌ {error_message}")
    
    # Display current holdings with mobile-optimized layout
    if st.session_state.portfolio_holdings:
        st.markdown("#### 📋 Current Holdings")
        
        # Mobile-friendly holdings display
        for i, holding in enumerate(st.session_state.portfolio_holdings):
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    st.markdown(f"**{holding['symbol']}**")
                
                with col2:
                    quantity_display = f"{holding['quantity']:,.8f}".rstrip('0').rstrip('.')
                    st.markdown(f"`{quantity_display}`")
                
                with col3:
                    if st.button("🗑️", key=f"remove_{i}", help=f"Remove {holding['symbol']}", use_container_width=True):
                        st.session_state.portfolio_holdings.pop(i)
                        try:
                            st.rerun()
                        except Exception:
                            # Fallback: just remove from session state
                            pass
                
                # Add separator for better mobile readability
                if i < len(st.session_state.portfolio_holdings) - 1:
                    st.markdown("---")
        
        # Mobile-optimized clear all button
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🗑️ Clear All Holdings", type="secondary", use_container_width=True):
                st.session_state.portfolio_holdings = []
                try:
                    st.rerun()
                except Exception:
                    # Fallback: just clear session state
                    pass
    
    else:
        st.info("📝 No holdings added yet. Add your first cryptocurrency holding above to start tracking your portfolio.")
    
    return st.session_state.portfolio_holdings


def render_portfolio_tracker(holdings: List[Dict[str, Any]], prices: Dict[str, float]):
    """
    Render complete portfolio tracker with real-time calculations and breakdown.
    
    Args:
        holdings: List of portfolio holdings with symbol and quantity
        prices: Dictionary mapping symbols to current prices
    """
    if not holdings:
        st.info("💡 Add some cryptocurrency holdings above to see your portfolio value and breakdown.")
        return
    
    from src.data.processor import calculate_portfolio_value, get_portfolio_breakdown
    
    # Calculate portfolio value and breakdown
    total_value, portfolio_holdings, missing_symbols = calculate_portfolio_value(holdings, prices)
    
    # Handle missing symbols
    if missing_symbols:
        st.warning(f"⚠️ Unable to fetch prices for: {', '.join(missing_symbols)}. These holdings are excluded from calculations.")
    
    if not portfolio_holdings:
        st.error("❌ No valid holdings could be priced. Please check your cryptocurrency symbols.")
        return
    
    # Get detailed breakdown
    breakdown = get_portfolio_breakdown(portfolio_holdings)
    
    # Display total portfolio value
    st.markdown("#### 💰 Portfolio Summary")
    
    # Total value metric
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Portfolio Value",
            value=f"${total_value:,.2f}",
            help="Current total value of all holdings in USD"
        )
    
    with col2:
        st.metric(
            label="Number of Assets",
            value=f"{breakdown['total_coins']}",
            help="Number of different cryptocurrencies in portfolio"
        )
    
    with col3:
        if breakdown['largest_holding']:
            largest = breakdown['largest_holding']
            st.metric(
                label="Largest Holding",
                value=f"{largest.symbol}",
                delta=f"{largest.percentage:.1f}%",
                help=f"Your largest holding by value"
            )
    
    st.markdown("---")
    
    # Portfolio breakdown table
    st.markdown("#### 📊 Portfolio Breakdown")
    
    if breakdown['holdings']:
        # Prepare data for display
        breakdown_data = []
        for holding in breakdown['holdings']:
            breakdown_data.append({
                'Symbol': holding.symbol,
                'Quantity': f"{holding.quantity:,.8f}".rstrip('0').rstrip('.'),
                'Current Value': f"${holding.current_value:,.2f}",
                'Portfolio %': f"{holding.percentage:.2f}%",
                '_percentage_value': holding.percentage  # For sorting/styling
            })
        
        # Create DataFrame for better display
        import pandas as pd
        df = pd.DataFrame(breakdown_data)
        
        # Display the table
        st.dataframe(
            df.drop('_percentage_value', axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                'Symbol': st.column_config.TextColumn(
                    'Symbol',
                    width='small',
                    help="Cryptocurrency symbol"
                ),
                'Quantity': st.column_config.TextColumn(
                    'Quantity',
                    width='medium',
                    help="Amount you own"
                ),
                'Current Value': st.column_config.TextColumn(
                    'Current Value',
                    width='medium',
                    help="Current USD value of this holding"
                ),
                'Portfolio %': st.column_config.TextColumn(
                    'Portfolio %',
                    width='small',
                    help="Percentage of total portfolio value"
                )
            }
        )
        
        # Portfolio composition chart
        st.markdown("#### 🥧 Portfolio Composition")
        
        try:
            # Create DataFrame for pie chart
            import pandas as pd
            import plotly.express as px
            
            chart_df = pd.DataFrame({
                'Symbol': [h.symbol for h in breakdown['holdings']],
                'Value': [h.current_value for h in breakdown['holdings']],
                'Percentage': [h.percentage for h in breakdown['holdings']]
            })
            
            # Create pie chart using DataFrame
            fig = px.pie(
                chart_df,
                values='Value',
                names='Symbol',
                title="Portfolio Allocation by Value",
                hover_data=['Percentage']
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>' +
                             'Value: $%{value:,.2f}<br>' +
                             'Portfolio: %{customdata[0]:.2f}%<br>' +
                             '<extra></extra>'
            )
            
            fig.update_layout(
                showlegend=True,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except ImportError:
            # Fallback to simple text display if plotly is not available
            st.info("📊 Portfolio composition chart requires Plotly. Here's your allocation breakdown:")
            for holding in breakdown['holdings']:
                st.write(f"• **{holding.symbol}**: {holding.percentage:.2f}% (${holding.current_value:,.2f})")
        except Exception as e:
            st.error(f"Error creating portfolio chart: {str(e)}")
            # Show simple breakdown as fallback
            for holding in breakdown['holdings']:
                st.write(f"• **{holding.symbol}**: {holding.percentage:.2f}% (${holding.current_value:,.2f})")
        
        # Portfolio insights
        st.markdown("#### 💡 Portfolio Insights")
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            if breakdown['largest_holding']:
                largest = breakdown['largest_holding']
                st.info(f"🔝 **Largest Position:** {largest.symbol} makes up {largest.percentage:.1f}% of your portfolio (${largest.current_value:,.2f})")
        
        with insights_col2:
            if breakdown['smallest_holding'] and breakdown['total_coins'] > 1:
                smallest = breakdown['smallest_holding']
                st.info(f"🔻 **Smallest Position:** {smallest.symbol} makes up {smallest.percentage:.1f}% of your portfolio (${smallest.current_value:,.2f})")
        
        # Diversification insight
        if breakdown['total_coins'] >= 3:
            # Check if portfolio is well diversified (no single holding > 50%)
            max_percentage = max(h.percentage for h in breakdown['holdings'])
            if max_percentage < 50:
                st.success("✅ **Well Diversified:** No single asset dominates your portfolio (largest position < 50%)")
            else:
                st.warning(f"⚠️ **Concentration Risk:** Your largest position ({breakdown['largest_holding'].symbol}) represents {max_percentage:.1f}% of your portfolio")
    
    else:
        st.error("❌ No portfolio data available for display.")
    
    # Add refresh note
    st.caption("💡 Portfolio values are calculated using real-time prices and update automatically when you refresh the page.")