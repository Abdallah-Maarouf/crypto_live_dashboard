"""
UI module for the Crypto Dashboard application.

This module contains styling utilities and reusable UI components
for consistent presentation across the Streamlit application.
"""

from .styles import inject_custom_css, get_color_for_change
from .components import render_kpi_card, render_crypto_table

__all__ = [
    'inject_custom_css',
    'get_color_for_change', 
    'render_kpi_card',
    'render_crypto_table'
]