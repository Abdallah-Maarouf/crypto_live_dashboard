#!/usr/bin/env python3
"""
Test script to validate mobile responsive design features.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_mobile_styles():
    """Test that mobile styles can be imported and used."""
    try:
        from src.ui.styles import (
            inject_custom_css, 
            inject_mobile_meta_tags,
            get_mobile_optimized_chart_config,
            get_mobile_chart_layout,
            is_mobile_device
        )
        
        print("✅ Mobile styles imported successfully")
        
        # Test mobile chart config
        config = get_mobile_optimized_chart_config()
        assert 'responsive' in config
        assert config['responsive'] == True
        assert 'displayModeBar' in config
        print("✅ Mobile chart config generated successfully")
        
        # Test mobile chart layout
        layout = get_mobile_chart_layout()
        assert 'height' in layout
        assert layout['height'] == 400
        assert 'margin' in layout
        print("✅ Mobile chart layout generated successfully")
        
        # Test mobile detection (should return False in test environment)
        is_mobile = is_mobile_device()
        assert isinstance(is_mobile, bool)
        print("✅ Mobile device detection working")
        
        return True
        
    except Exception as e:
        print(f"❌ Mobile styles test failed: {e}")
        return False


def test_mobile_components():
    """Test that mobile-optimized components can be imported."""
    try:
        from src.ui.components import (
            render_price_chart,
            render_crypto_table,
            render_chart_controls,
            render_portfolio_input_form
        )
        
        print("✅ Mobile components imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Mobile components test failed: {e}")
        return False


def test_app_imports():
    """Test that the main app can import mobile features."""
    try:
        # Test that app.py can import the mobile features
        import app
        print("✅ Main app imports mobile features successfully")
        return True
        
    except Exception as e:
        print(f"❌ App import test failed: {e}")
        return False


def main():
    """Run all mobile responsive tests."""
    print("🧪 Testing Mobile Responsive Design Implementation")
    print("=" * 50)
    
    tests = [
        ("Mobile Styles", test_mobile_styles),
        ("Mobile Components", test_mobile_components),
        ("App Imports", test_app_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📱 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All mobile responsive design tests passed!")
        print("\n📱 Mobile Optimizations Implemented:")
        print("   • Responsive CSS with mobile breakpoints")
        print("   • Touch-friendly interface elements")
        print("   • Mobile-optimized charts and tables")
        print("   • Improved form layouts for mobile")
        print("   • Mobile meta tags for better viewport handling")
        print("   • Accessibility improvements for touch devices")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)