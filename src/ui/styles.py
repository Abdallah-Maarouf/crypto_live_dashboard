"""
Styling utilities and CSS injection system for the Crypto Dashboard.

This module provides a centralized styling system with modern color schemes,
responsive design, and consistent component styling.
"""

import streamlit as st


# Color scheme constants
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c', 
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'background': '#f8f9fa',
    'card_bg': '#ffffff',
    'text_primary': '#212529',
    'text_secondary': '#6c757d',
    'border': '#dee2e6',
    'shadow': 'rgba(0,0,0,0.1)'
}


def inject_custom_css():
    """
    Inject custom CSS styles into the Streamlit application.
    
    This function applies a modern, responsive design system with:
    - Consistent color scheme
    - Typography hierarchy
    - Component styling
    - Mobile responsiveness
    """
    css = f"""
    <style>
    /* Global Styles */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    
    /* Typography */
    .dashboard-title {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    
    .dashboard-subtitle {{
        font-size: 1.1rem;
        color: {COLORS['text_secondary']};
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .section-header {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 1rem;
        border-bottom: 2px solid {COLORS['primary']};
        padding-bottom: 0.5rem;
    }}
    
    /* KPI Cards */
    .metric-card {{
        background: {COLORS['card_bg']};
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px {COLORS['shadow']};
        border-left: 4px solid {COLORS['primary']};
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px {COLORS['shadow']};
    }}
    
    .metric-title {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        margin-bottom: 0.25rem;
    }}
    
    .metric-change {{
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    
    .metric-change.positive {{
        color: {COLORS['success']};
    }}
    
    .metric-change.negative {{
        color: {COLORS['danger']};
    }}
    
    .metric-range {{
        font-size: 0.85rem;
        color: {COLORS['text_secondary']};
    }}
    
    /* Crypto Table */
    .crypto-table {{
        background: {COLORS['card_bg']};
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px {COLORS['shadow']};
        margin-bottom: 2rem;
    }}
    
    .crypto-table table {{
        width: 100%;
        border-collapse: collapse;
    }}
    
    .crypto-table th {{
        background: {COLORS['primary']};
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .crypto-table td {{
        padding: 1rem;
        border-bottom: 1px solid {COLORS['border']};
        font-size: 0.95rem;
    }}
    
    .crypto-table tr:last-child td {{
        border-bottom: none;
    }}
    
    .crypto-table tr:hover {{
        background-color: #f8f9fa;
    }}
    
    .crypto-symbol {{
        font-weight: 700;
        color: {COLORS['text_primary']};
    }}
    
    .crypto-price {{
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}
    
    .crypto-change-positive {{
        color: {COLORS['success']};
        font-weight: 600;
    }}
    
    .crypto-change-negative {{
        color: {COLORS['danger']};
        font-weight: 600;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background: #1565c0;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px {COLORS['shadow']};
    }}
    
    /* Loading States */
    .loading-spinner {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }}
    
    .loading-text {{
        color: {COLORS['text_secondary']};
        font-style: italic;
        text-align: center;
        padding: 1rem;
    }}
    
    /* Error States */
    .error-message {{
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COLORS['danger']};
        margin: 1rem 0;
    }}
    
    .warning-message {{
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COLORS['warning']};
        margin: 1rem 0;
    }}
    
    /* Responsive Design and Mobile Optimization */
    
    /* Tablet and small desktop (768px - 1024px) */
    @media (max-width: 1024px) {{
        .main .block-container {{
            max-width: 100%;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }}
        
        .metric-card {{
            padding: 1.25rem;
        }}
        
        .crypto-table th,
        .crypto-table td {{
            padding: 0.875rem 0.75rem;
            font-size: 0.9rem;
        }}
    }}
    
    /* Mobile landscape and small tablets (481px - 768px) */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        
        .dashboard-title {{
            font-size: 2rem;
            margin-bottom: 0.25rem;
        }}
        
        .dashboard-subtitle {{
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }}
        
        .section-header {{
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
        }}
        
        .metric-card {{
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}
        
        .metric-value {{
            font-size: 1.5rem;
        }}
        
        .metric-change {{
            font-size: 0.9rem;
        }}
        
        .metric-range {{
            font-size: 0.8rem;
        }}
        
        /* Table optimizations for tablets */
        .crypto-table {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}
        
        .crypto-table th,
        .crypto-table td {{
            padding: 0.75rem 0.5rem;
            font-size: 0.85rem;
            white-space: nowrap;
        }}
        
        /* Touch-friendly buttons */
        .stButton > button {{
            padding: 0.75rem 1.5rem;
            font-size: 0.9rem;
            min-height: 44px; /* iOS recommended touch target */
        }}
        
        /* Improved selectbox for mobile */
        .stSelectbox > div > div {{
            min-height: 44px;
        }}
        
        /* Better spacing for form elements */
        .stTextInput > div > div > input {{
            min-height: 44px;
            font-size: 16px; /* Prevents zoom on iOS */
        }}
    }}
    
    /* Mobile portrait (320px - 480px) */
    @media (max-width: 480px) {{
        .main .block-container {{
            padding-left: 0.75rem;
            padding-right: 0.75rem;
            padding-top: 0.75rem;
        }}
        
        .dashboard-title {{
            font-size: 1.75rem;
            line-height: 1.2;
        }}
        
        .dashboard-subtitle {{
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}
        
        .section-header {{
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}
        
        .metric-card {{
            padding: 0.75rem;
            margin-bottom: 0.5rem;
        }}
        
        .metric-title {{
            font-size: 0.8rem;
        }}
        
        .metric-value {{
            font-size: 1.25rem;
        }}
        
        .metric-change {{
            font-size: 0.85rem;
        }}
        
        .metric-range {{
            font-size: 0.75rem;
        }}
        
        /* Compact table for mobile */
        .crypto-table th,
        .crypto-table td {{
            padding: 0.5rem 0.25rem;
            font-size: 0.8rem;
        }}
        
        .crypto-table th {{
            font-size: 0.75rem;
        }}
        
        /* Stack columns on very small screens */
        .crypto-table {{
            font-size: 0.8rem;
        }}
        
        /* Mobile-optimized buttons */
        .stButton > button {{
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            width: 100%;
            min-height: 48px; /* Larger touch target for mobile */
        }}
        
        /* Form elements optimization */
        .stSelectbox > div > div {{
            min-height: 48px;
        }}
        
        .stTextInput > div > div > input {{
            min-height: 48px;
            font-size: 16px; /* Prevents zoom on iOS */
            padding: 0.75rem;
        }}
        
        /* Improved spacing for mobile */
        .element-container {{
            margin-bottom: 0.5rem;
        }}
        
        /* Better chart container for mobile */
        .js-plotly-plot {{
            margin: 0 -0.75rem; /* Extend to screen edges */
        }}
    }}
    
    /* Extra small mobile devices (max 320px) */
    @media (max-width: 320px) {{
        .main .block-container {{
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}
        
        .dashboard-title {{
            font-size: 1.5rem;
        }}
        
        .metric-card {{
            padding: 0.5rem;
        }}
        
        .metric-value {{
            font-size: 1.1rem;
        }}
        
        .crypto-table th,
        .crypto-table td {{
            padding: 0.375rem 0.125rem;
            font-size: 0.75rem;
        }}
        
        .crypto-table th {{
            font-size: 0.7rem;
        }}
    }}
    
    /* Landscape orientation optimizations */
    @media (max-height: 500px) and (orientation: landscape) {{
        .main .block-container {{
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }}
        
        .dashboard-title {{
            font-size: 1.5rem;
            margin-bottom: 0.25rem;
        }}
        
        .dashboard-subtitle {{
            margin-bottom: 0.75rem;
        }}
        
        .metric-card {{
            padding: 0.75rem;
            margin-bottom: 0.5rem;
        }}
        
        .section-header {{
            margin-bottom: 0.5rem;
        }}
    }}
    
    /* High DPI displays */
    @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {{
        .crypto-table {{
            border-collapse: separate;
            border-spacing: 0;
        }}
        
        .metric-card {{
            border: 1px solid {COLORS['border']};
        }}
    }}
    
    /* Dark mode support for mobile devices */
    @media (prefers-color-scheme: dark) {{
        .main .block-container {{
            background-color: #1a1a1a;
        }}
        
        .metric-card {{
            background: #2d2d2d;
            color: #ffffff;
        }}
        
        .crypto-table {{
            background: #2d2d2d;
        }}
        
        .crypto-table th {{
            background: #404040;
        }}
        
        .crypto-table td {{
            border-bottom-color: #404040;
        }}
    }}
    
    /* Accessibility improvements for mobile */
    @media (max-width: 768px) {{
        /* Larger touch targets */
        button, .stButton > button, .stSelectbox, .stTextInput {{
            min-height: 44px;
        }}
        
        /* Better focus indicators */
        button:focus, .stButton > button:focus {{
            outline: 2px solid {COLORS['primary']};
            outline-offset: 2px;
        }}
        
        /* Improved readability */
        .crypto-table td, .crypto-table th {{
            line-height: 1.4;
        }}
        
        /* Prevent horizontal scrolling issues */
        .main .block-container {{
            overflow-x: hidden;
        }}
        
        /* Better spacing for touch interaction */
        .stMetric {{
            margin-bottom: 1rem;
        }}
    }}
    
    /* Print styles for mobile */
    @media print {{
        .stButton, .stSelectbox {{
            display: none !important;
        }}
        
        .metric-card {{
            break-inside: avoid;
            page-break-inside: avoid;
        }}
        
        .crypto-table {{
            break-inside: avoid;
            page-break-inside: avoid;
        }}
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def get_color_for_change(change_percent):
    """
    Get the appropriate color for a percentage change value.
    
    Args:
        change_percent (float): The percentage change value
        
    Returns:
        str: Color code for positive (green) or negative (red) changes
    """
    if change_percent >= 0:
        return COLORS['success']
    else:
        return COLORS['danger']


def get_change_class(change_percent):
    """
    Get the appropriate CSS class for a percentage change value.
    
    Args:
        change_percent (float): The percentage change value
        
    Returns:
        str: CSS class name for styling
    """
    if change_percent >= 0:
        return 'positive'
    else:
        return 'negative'


def is_mobile_device():
    """
    Detect if the user is on a mobile device based on user agent.
    This is a simple heuristic and may not be 100% accurate.
    
    Returns:
        bool: True if likely a mobile device, False otherwise
    """
    try:
        # Try to get user agent from Streamlit's session info
        # This is a fallback approach since Streamlit doesn't directly expose user agent
        import streamlit as st
        
        # Check if we're in a narrow viewport (common mobile indicator)
        # This is inferred from Streamlit's responsive behavior
        return False  # Default to desktop for now
        
    except Exception:
        return False


def get_mobile_optimized_chart_config():
    """
    Get chart configuration optimized for mobile devices.
    
    Returns:
        dict: Plotly chart configuration for mobile
    """
    return {
        'displayModeBar': False,  # Hide toolbar on mobile
        'responsive': True,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'crypto_chart',
            'height': 400,
            'width': 800,
            'scale': 1
        },
        'modeBarButtonsToRemove': [
            'pan2d', 'select2d', 'lasso2d', 'resetScale2d',
            'zoomIn2d', 'zoomOut2d', 'autoScale2d'
        ],
        'doubleClick': 'reset',
        'showTips': False,
        'scrollZoom': False
    }


def get_mobile_chart_layout():
    """
    Get chart layout optimized for mobile devices.
    
    Returns:
        dict: Plotly layout configuration for mobile
    """
    return {
        'height': 400,  # Shorter height for mobile
        'margin': dict(l=20, r=20, t=40, b=40),  # Tighter margins
        'font': dict(size=10),  # Smaller font
        'title': dict(
            font=dict(size=14),
            x=0.5,
            xanchor='center'
        ),
        'xaxis': dict(
            title=dict(font=dict(size=10)),
            tickfont=dict(size=8),
            showgrid=True,
            gridwidth=0.5
        ),
        'yaxis': dict(
            title=dict(font=dict(size=10)),
            tickfont=dict(size=8),
            showgrid=True,
            gridwidth=0.5
        ),
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=9)
        ),
        'hovermode': 'x unified',
        'dragmode': False  # Disable dragging on mobile
    }


def inject_mobile_meta_tags():
    """
    Inject mobile-optimized meta tags for better mobile experience.
    """
    mobile_meta = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="theme-color" content="#1f77b4">
    <meta name="apple-mobile-web-app-title" content="Crypto Dashboard">
    """
    
    st.markdown(mobile_meta, unsafe_allow_html=True)