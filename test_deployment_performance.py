#!/usr/bin/env python3
"""
Deployment Performance Testing Script

Tests cold start performance and loading times for the Crypto Dashboard
to ensure optimal performance on Streamlit Cloud.
"""

import time
import sys
import os
import requests
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import_performance() -> Dict[str, float]:
    """
    Test the time it takes to import all required modules.
    
    Returns:
        Dict with import timing results
    """
    print("🔄 Testing module import performance...")
    
    import_times = {}
    
    # Test core imports
    start_time = time.time()
    import streamlit as st
    import_times['streamlit'] = time.time() - start_time
    
    start_time = time.time()
    import pandas as pd
    import_times['pandas'] = time.time() - start_time
    
    start_time = time.time()
    import plotly.graph_objects as go
    import_times['plotly'] = time.time() - start_time
    
    start_time = time.time()
    import requests
    import_times['requests'] = time.time() - start_time
    
    # Test custom module imports
    start_time = time.time()
    try:
        from src.api.binance_client import BinanceClient
        from src.ui.styles import inject_custom_css
        from src.ui.components import render_dashboard_header
        from src.data.processor import prepare_chart_data
        import_times['custom_modules'] = time.time() - start_time
    except ImportError as e:
        print(f"❌ Custom module import failed: {e}")
        import_times['custom_modules'] = -1
    
    return import_times


def test_api_connectivity() -> Dict[str, Any]:
    """
    Test API connectivity and response times.
    
    Returns:
        Dict with API performance results
    """
    print("🔄 Testing API connectivity and performance...")
    
    api_results = {
        'connectivity': False,
        'response_times': {},
        'errors': []
    }
    
    try:
        from src.api.binance_client import BinanceClient
        client = BinanceClient()
        
        # Test BTC ticker fetch
        start_time = time.time()
        btc_data = client.get_ticker_24hr("BTCUSDT")
        api_results['response_times']['btc_ticker'] = time.time() - start_time
        
        if btc_data and 'lastPrice' in btc_data:
            api_results['connectivity'] = True
            print(f"✅ BTC ticker fetch: {api_results['response_times']['btc_ticker']:.3f}s")
        else:
            api_results['errors'].append("Invalid BTC ticker response format")
        
        # Test exchange info fetch
        start_time = time.time()
        exchange_info = client.get_exchange_info()
        api_results['response_times']['exchange_info'] = time.time() - start_time
        
        if exchange_info and 'symbols' in exchange_info:
            print(f"✅ Exchange info fetch: {api_results['response_times']['exchange_info']:.3f}s")
        else:
            api_results['errors'].append("Invalid exchange info response format")
        
        # Test historical data fetch
        start_time = time.time()
        klines_data = client.get_klines("BTCUSDT", "1d", 10)
        api_results['response_times']['historical_data'] = time.time() - start_time
        
        if klines_data and len(klines_data) > 0:
            print(f"✅ Historical data fetch: {api_results['response_times']['historical_data']:.3f}s")
        else:
            api_results['errors'].append("Invalid historical data response")
            
    except Exception as e:
        api_results['errors'].append(f"API test failed: {str(e)}")
        print(f"❌ API connectivity test failed: {e}")
    
    return api_results


def test_data_processing_performance() -> Dict[str, float]:
    """
    Test data processing performance.
    
    Returns:
        Dict with processing timing results
    """
    print("🔄 Testing data processing performance...")
    
    processing_times = {}
    
    try:
        from src.data.processor import prepare_chart_data, format_price_data, format_percentage_change
        
        # Create sample data for testing
        sample_klines = [
            [1640995200000, "47000.00", "48000.00", "46500.00", "47500.00", "1000.00", 1640998800000],
            [1640998800000, "47500.00", "48500.00", "47000.00", "48000.00", "1200.00", 1641002400000],
            [1641002400000, "48000.00", "49000.00", "47800.00", "48800.00", "1100.00", 1641006000000]
        ]
        
        # Test chart data preparation
        start_time = time.time()
        chart_data = prepare_chart_data(sample_klines)
        processing_times['chart_data_prep'] = time.time() - start_time
        
        # Test price formatting
        start_time = time.time()
        for _ in range(100):  # Test with multiple iterations
            formatted_price = format_price_data(47234.56789)
        processing_times['price_formatting'] = time.time() - start_time
        
        # Test percentage formatting
        start_time = time.time()
        for _ in range(100):  # Test with multiple iterations
            formatted_pct = format_percentage_change(2.34567)
        processing_times['percentage_formatting'] = time.time() - start_time
        
        print(f"✅ Chart data preparation: {processing_times['chart_data_prep']:.3f}s")
        print(f"✅ Price formatting (100x): {processing_times['price_formatting']:.3f}s")
        print(f"✅ Percentage formatting (100x): {processing_times['percentage_formatting']:.3f}s")
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        processing_times['error'] = str(e)
    
    return processing_times


def test_memory_usage() -> Dict[str, Any]:
    """
    Test memory usage of the application.
    
    Returns:
        Dict with memory usage information
    """
    print("🔄 Testing memory usage...")
    
    memory_info = {}
    
    try:
        import psutil
        process = psutil.Process()
        
        # Get initial memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_info['initial_memory_mb'] = initial_memory
        
        # Import all modules and measure memory increase
        import streamlit as st
        import pandas as pd
        import plotly.graph_objects as go
        from src.api.binance_client import BinanceClient
        from src.ui.components import render_dashboard_header
        from src.data.processor import prepare_chart_data
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_info['final_memory_mb'] = final_memory
        memory_info['memory_increase_mb'] = final_memory - initial_memory
        
        print(f"✅ Initial memory: {initial_memory:.1f} MB")
        print(f"✅ Final memory: {final_memory:.1f} MB")
        print(f"✅ Memory increase: {memory_info['memory_increase_mb']:.1f} MB")
        
    except ImportError:
        print("⚠️ psutil not available, skipping memory test")
        memory_info['error'] = "psutil not available"
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        memory_info['error'] = str(e)
    
    return memory_info


def run_performance_tests():
    """
    Run all performance tests and generate a report.
    """
    print("🚀 Starting Crypto Dashboard Performance Tests")
    print("=" * 50)
    
    # Test import performance
    import_results = test_import_performance()
    
    # Test API connectivity
    api_results = test_api_connectivity()
    
    # Test data processing
    processing_results = test_data_processing_performance()
    
    # Test memory usage
    memory_results = test_memory_usage()
    
    # Generate performance report
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE REPORT")
    print("=" * 50)
    
    print("\n🔧 Import Performance:")
    total_import_time = 0
    for module, time_taken in import_results.items():
        if time_taken >= 0:
            print(f"  • {module}: {time_taken:.3f}s")
            total_import_time += time_taken
        else:
            print(f"  • {module}: FAILED")
    print(f"  📈 Total import time: {total_import_time:.3f}s")
    
    print("\n🌐 API Performance:")
    if api_results['connectivity']:
        print("  ✅ API connectivity: SUCCESS")
        for endpoint, time_taken in api_results['response_times'].items():
            print(f"  • {endpoint}: {time_taken:.3f}s")
    else:
        print("  ❌ API connectivity: FAILED")
        for error in api_results['errors']:
            print(f"    - {error}")
    
    print("\n⚡ Processing Performance:")
    for process, time_taken in processing_results.items():
        if process != 'error':
            print(f"  • {process}: {time_taken:.3f}s")
        else:
            print(f"  ❌ Processing error: {time_taken}")
    
    print("\n💾 Memory Usage:")
    if 'error' not in memory_results:
        print(f"  • Initial: {memory_results.get('initial_memory_mb', 0):.1f} MB")
        print(f"  • Final: {memory_results.get('final_memory_mb', 0):.1f} MB")
        print(f"  • Increase: {memory_results.get('memory_increase_mb', 0):.1f} MB")
    else:
        print(f"  ⚠️ {memory_results['error']}")
    
    # Performance recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if total_import_time > 3.0:
        print("  ⚠️ Import time is high (>3s). Consider lazy loading for non-critical modules.")
    else:
        print("  ✅ Import time is acceptable (<3s).")
    
    if api_results['connectivity']:
        avg_api_time = sum(api_results['response_times'].values()) / len(api_results['response_times'])
        if avg_api_time > 2.0:
            print("  ⚠️ API response times are high (>2s avg). Consider implementing better caching.")
        else:
            print("  ✅ API response times are good (<2s avg).")
    
    if 'memory_increase_mb' in memory_results and memory_results['memory_increase_mb'] > 200:
        print("  ⚠️ Memory usage is high (>200MB). Consider optimizing imports and data structures.")
    elif 'memory_increase_mb' in memory_results:
        print("  ✅ Memory usage is reasonable (<200MB).")
    
    print("\n🎯 DEPLOYMENT READINESS:")
    
    # Calculate overall score
    score = 0
    max_score = 4
    
    if total_import_time < 3.0:
        score += 1
    if api_results['connectivity']:
        score += 1
    if 'error' not in processing_results:
        score += 1
    if 'error' not in memory_results and memory_results.get('memory_increase_mb', 0) < 200:
        score += 1
    
    percentage = (score / max_score) * 100
    
    if percentage >= 75:
        print(f"  ✅ READY FOR DEPLOYMENT ({percentage:.0f}% score)")
    elif percentage >= 50:
        print(f"  ⚠️ DEPLOYMENT WITH CAUTION ({percentage:.0f}% score)")
    else:
        print(f"  ❌ NOT READY FOR DEPLOYMENT ({percentage:.0f}% score)")
    
    print("\n" + "=" * 50)
    print("🏁 Performance testing completed!")


if __name__ == "__main__":
    run_performance_tests()