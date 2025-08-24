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
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        
        .dashboard-title {{
            font-size: 2rem;
        }}
        
        .metric-card {{
            padding: 1rem;
        }}
        
        .metric-value {{
            font-size: 1.5rem;
        }}
        
        .crypto-table th,
        .crypto-table td {{
            padding: 0.75rem 0.5rem;
            font-size: 0.85rem;
        }}
        
        .section-header {{
            font-size: 1.25rem;
        }}
    }}
    
    @media (max-width: 480px) {{
        .dashboard-title {{
            font-size: 1.75rem;
        }}
        
        .metric-card {{
            padding: 0.75rem;
        }}
        
        .metric-value {{
            font-size: 1.25rem;
        }}
        
        .crypto-table th,
        .crypto-table td {{
            padding: 0.5rem 0.25rem;
            font-size: 0.8rem;
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