#!/usr/bin/env python3
"""
Deployment Validation Script

Validates that all external dependencies work correctly in a cloud environment
and that the application is ready for Streamlit Cloud deployment.
"""

import sys
import os
import importlib
import subprocess
from typing import Dict, List, Any

def validate_python_version() -> Dict[str, Any]:
    """Validate Python version compatibility."""
    print("🔍 Validating Python version...")
    
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    # Streamlit Cloud supports Python 3.7+
    is_compatible = version_info >= (3, 7)
    
    result = {
        'version': version_str,
        'compatible': is_compatible,
        'recommended': version_info >= (3, 8)
    }
    
    if is_compatible:
        status = "✅" if result['recommended'] else "⚠️"
        print(f"{status} Python {version_str} - {'Recommended' if result['recommended'] else 'Compatible'}")
    else:
        print(f"❌ Python {version_str} - Not compatible (requires 3.7+)")
    
    return result


def validate_requirements() -> Dict[str, Any]:
    """Validate all requirements can be installed and imported."""
    print("🔍 Validating requirements.txt dependencies...")
    
    # Read requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return {'error': 'requirements.txt not found'}
    
    results = {
        'total_packages': len(requirements),
        'successful_imports': 0,
        'failed_imports': [],
        'package_details': {}
    }
    
    # Map requirements to import names
    import_mapping = {
        'streamlit': 'streamlit',
        'requests': 'requests',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'pyyaml': 'yaml',
        'urllib3': 'urllib3',
        'certifi': 'certifi'
    }
    
    for req in requirements:
        # Extract package name (remove version constraints)
        package_name = req.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()
        import_name = import_mapping.get(package_name, package_name)
        
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'unknown')
            results['successful_imports'] += 1
            results['package_details'][package_name] = {
                'status': 'success',
                'version': version,
                'import_name': import_name
            }
            print(f"  ✅ {package_name} ({version})")
            
        except ImportError as e:
            results['failed_imports'].append(package_name)
            results['package_details'][package_name] = {
                'status': 'failed',
                'error': str(e),
                'import_name': import_name
            }
            print(f"  ❌ {package_name} - Import failed: {e}")
    
    return results


def validate_custom_modules() -> Dict[str, Any]:
    """Validate custom application modules."""
    print("🔍 Validating custom modules...")
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    modules_to_test = [
        'src.api.binance_client',
        'src.ui.styles',
        'src.ui.components',
        'src.data.processor'
    ]
    
    results = {
        'total_modules': len(modules_to_test),
        'successful_imports': 0,
        'failed_imports': [],
        'module_details': {}
    }
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            results['successful_imports'] += 1
            results['module_details'][module_name] = {
                'status': 'success',
                'file_path': getattr(module, '__file__', 'unknown')
            }
            print(f"  ✅ {module_name}")
            
        except ImportError as e:
            results['failed_imports'].append(module_name)
            results['module_details'][module_name] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"  ❌ {module_name} - Import failed: {e}")
    
    return results


def validate_file_structure() -> Dict[str, Any]:
    """Validate required file structure for deployment."""
    print("🔍 Validating file structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'src/__init__.py',
        'src/api/__init__.py',
        'src/api/binance_client.py',
        'src/ui/__init__.py',
        'src/ui/styles.py',
        'src/ui/components.py',
        'src/data/__init__.py',
        'src/data/processor.py',
        'src/utils/__init__.py'
    ]
    
    optional_files = [
        'config.yaml',
        '.streamlit/config.toml',
        'README.md',
        '.gitignore'
    ]
    
    results = {
        'required_files': {'total': len(required_files), 'found': 0, 'missing': []},
        'optional_files': {'total': len(optional_files), 'found': 0, 'missing': []},
        'file_details': {}
    }
    
    # Check required files
    for file_path in required_files:
        if os.path.exists(file_path):
            results['required_files']['found'] += 1
            results['file_details'][file_path] = {'status': 'found', 'required': True}
            print(f"  ✅ {file_path}")
        else:
            results['required_files']['missing'].append(file_path)
            results['file_details'][file_path] = {'status': 'missing', 'required': True}
            print(f"  ❌ {file_path} - Missing (required)")
    
    # Check optional files
    for file_path in optional_files:
        if os.path.exists(file_path):
            results['optional_files']['found'] += 1
            results['file_details'][file_path] = {'status': 'found', 'required': False}
            print(f"  ✅ {file_path} (optional)")
        else:
            results['optional_files']['missing'].append(file_path)
            results['file_details'][file_path] = {'status': 'missing', 'required': False}
            print(f"  ⚠️ {file_path} - Missing (optional)")
    
    return results


def validate_api_connectivity() -> Dict[str, Any]:
    """Validate external API connectivity."""
    print("🔍 Validating API connectivity...")
    
    try:
        sys.path.insert(0, 'src')
        from src.api.binance_client import BinanceClient
        
        client = BinanceClient()
        results = {
            'connectivity': False,
            'endpoints_tested': 0,
            'endpoints_working': 0,
            'endpoint_details': {}
        }
        
        # Test ticker endpoint
        try:
            ticker_data = client.get_ticker_24hr("BTCUSDT")
            if ticker_data and 'lastPrice' in ticker_data:
                results['endpoints_working'] += 1
                results['endpoint_details']['ticker'] = {'status': 'success', 'response_keys': list(ticker_data.keys())[:5]}
                print(f"  ✅ Ticker endpoint - BTC price: ${float(ticker_data['lastPrice']):,.2f}")
            else:
                results['endpoint_details']['ticker'] = {'status': 'failed', 'error': 'Invalid response format'}
                print(f"  ❌ Ticker endpoint - Invalid response")
            results['endpoints_tested'] += 1
        except Exception as e:
            results['endpoint_details']['ticker'] = {'status': 'failed', 'error': str(e)}
            print(f"  ❌ Ticker endpoint - Error: {e}")
            results['endpoints_tested'] += 1
        
        # Test exchange info endpoint
        try:
            exchange_info = client.get_exchange_info()
            if exchange_info and 'symbols' in exchange_info:
                results['endpoints_working'] += 1
                results['endpoint_details']['exchange_info'] = {
                    'status': 'success', 
                    'symbols_count': len(exchange_info['symbols'])
                }
                print(f"  ✅ Exchange info endpoint - {len(exchange_info['symbols'])} symbols available")
            else:
                results['endpoint_details']['exchange_info'] = {'status': 'failed', 'error': 'Invalid response format'}
                print(f"  ❌ Exchange info endpoint - Invalid response")
            results['endpoints_tested'] += 1
        except Exception as e:
            results['endpoint_details']['exchange_info'] = {'status': 'failed', 'error': str(e)}
            print(f"  ❌ Exchange info endpoint - Error: {e}")
            results['endpoints_tested'] += 1
        
        # Test klines endpoint
        try:
            klines_data = client.get_klines("BTCUSDT", "1d", 5)
            if klines_data and len(klines_data) > 0:
                results['endpoints_working'] += 1
                results['endpoint_details']['klines'] = {
                    'status': 'success', 
                    'data_points': len(klines_data)
                }
                print(f"  ✅ Klines endpoint - {len(klines_data)} data points retrieved")
            else:
                results['endpoint_details']['klines'] = {'status': 'failed', 'error': 'No data returned'}
                print(f"  ❌ Klines endpoint - No data returned")
            results['endpoints_tested'] += 1
        except Exception as e:
            results['endpoint_details']['klines'] = {'status': 'failed', 'error': str(e)}
            print(f"  ❌ Klines endpoint - Error: {e}")
            results['endpoints_tested'] += 1
        
        # Overall connectivity status
        results['connectivity'] = results['endpoints_working'] > 0
        
    except Exception as e:
        results = {
            'connectivity': False,
            'error': f"Failed to initialize API client: {str(e)}",
            'endpoints_tested': 0,
            'endpoints_working': 0
        }
        print(f"  ❌ API client initialization failed: {e}")
    
    return results


def validate_streamlit_compatibility() -> Dict[str, Any]:
    """Validate Streamlit-specific compatibility."""
    print("🔍 Validating Streamlit compatibility...")
    
    results = {
        'streamlit_available': False,
        'config_valid': False,
        'app_structure_valid': False,
        'details': {}
    }
    
    # Check Streamlit availability
    try:
        import streamlit as st
        results['streamlit_available'] = True
        results['details']['streamlit_version'] = st.__version__
        print(f"  ✅ Streamlit {st.__version__} available")
    except ImportError as e:
        results['details']['streamlit_error'] = str(e)
        print(f"  ❌ Streamlit not available: {e}")
        return results
    
    # Check config file
    if os.path.exists('.streamlit/config.toml'):
        results['config_valid'] = True
        print(f"  ✅ Streamlit config file found")
    else:
        print(f"  ⚠️ Streamlit config file not found (optional)")
    
    # Check app.py structure
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
            
        # Check for required Streamlit patterns
        required_patterns = [
            'st.set_page_config',
            'if __name__ == "__main__"',
            'import streamlit'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in app_content:
                missing_patterns.append(pattern)
        
        if not missing_patterns:
            results['app_structure_valid'] = True
            print(f"  ✅ App structure is valid")
        else:
            results['details']['missing_patterns'] = missing_patterns
            print(f"  ⚠️ App structure issues: missing {missing_patterns}")
            
    except Exception as e:
        results['details']['app_check_error'] = str(e)
        print(f"  ❌ Could not validate app structure: {e}")
    
    return results


def generate_deployment_report(validation_results: Dict[str, Any]) -> None:
    """Generate a comprehensive deployment readiness report."""
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT READINESS REPORT")
    print("=" * 60)
    
    # Calculate overall score
    total_checks = 6
    passed_checks = 0
    
    # Python version check
    if validation_results['python']['compatible']:
        passed_checks += 1
    
    # Requirements check
    req_success_rate = (validation_results['requirements']['successful_imports'] / 
                       validation_results['requirements']['total_packages'])
    if req_success_rate >= 0.9:  # 90% success rate
        passed_checks += 1
    
    # Custom modules check
    mod_success_rate = (validation_results['modules']['successful_imports'] / 
                       validation_results['modules']['total_modules'])
    if mod_success_rate == 1.0:  # 100% success rate for custom modules
        passed_checks += 1
    
    # File structure check
    if not validation_results['files']['required_files']['missing']:
        passed_checks += 1
    
    # API connectivity check
    if validation_results['api']['connectivity']:
        passed_checks += 1
    
    # Streamlit compatibility check
    if (validation_results['streamlit']['streamlit_available'] and 
        validation_results['streamlit']['app_structure_valid']):
        passed_checks += 1
    
    # Overall score
    score_percentage = (passed_checks / total_checks) * 100
    
    print(f"\n🎯 OVERALL SCORE: {passed_checks}/{total_checks} ({score_percentage:.0f}%)")
    
    if score_percentage >= 90:
        print("✅ READY FOR DEPLOYMENT")
        deployment_status = "READY"
    elif score_percentage >= 70:
        print("⚠️ DEPLOYMENT WITH CAUTION")
        deployment_status = "CAUTION"
    else:
        print("❌ NOT READY FOR DEPLOYMENT")
        deployment_status = "NOT_READY"
    
    # Detailed breakdown
    print(f"\n📊 DETAILED RESULTS:")
    
    # Python version
    python_status = "✅" if validation_results['python']['compatible'] else "❌"
    print(f"{python_status} Python Version: {validation_results['python']['version']}")
    
    # Requirements
    req_status = "✅" if req_success_rate >= 0.9 else "❌"
    print(f"{req_status} Dependencies: {validation_results['requirements']['successful_imports']}/{validation_results['requirements']['total_packages']} packages")
    
    # Custom modules
    mod_status = "✅" if mod_success_rate == 1.0 else "❌"
    print(f"{mod_status} Custom Modules: {validation_results['modules']['successful_imports']}/{validation_results['modules']['total_modules']} modules")
    
    # File structure
    file_status = "✅" if not validation_results['files']['required_files']['missing'] else "❌"
    print(f"{file_status} File Structure: {validation_results['files']['required_files']['found']}/{validation_results['files']['required_files']['total']} required files")
    
    # API connectivity
    api_status = "✅" if validation_results['api']['connectivity'] else "❌"
    api_endpoints = validation_results['api'].get('endpoints_working', 0)
    api_total = validation_results['api'].get('endpoints_tested', 0)
    print(f"{api_status} API Connectivity: {api_endpoints}/{api_total} endpoints working")
    
    # Streamlit compatibility
    st_status = "✅" if (validation_results['streamlit']['streamlit_available'] and 
                        validation_results['streamlit']['app_structure_valid']) else "❌"
    print(f"{st_status} Streamlit Compatibility: App structure and imports")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if deployment_status == "READY":
        print("  🚀 Your application is ready for Streamlit Cloud deployment!")
        print("  📝 Next steps:")
        print("    1. Push your code to GitHub")
        print("    2. Connect your repository to Streamlit Cloud")
        print("    3. Deploy and monitor the application")
    
    elif deployment_status == "CAUTION":
        print("  ⚠️ Your application can be deployed but has some issues:")
        
        if not validation_results['python']['recommended']:
            print("    • Consider upgrading to Python 3.8+ for better performance")
        
        if req_success_rate < 0.9:
            failed_deps = validation_results['requirements']['failed_imports']
            print(f"    • Fix missing dependencies: {', '.join(failed_deps)}")
        
        if not validation_results['api']['connectivity']:
            print("    • API connectivity issues may affect functionality")
        
        if validation_results['files']['required_files']['missing']:
            missing_files = validation_results['files']['required_files']['missing']
            print(f"    • Add missing required files: {', '.join(missing_files)}")
    
    else:
        print("  ❌ Critical issues must be resolved before deployment:")
        
        if not validation_results['python']['compatible']:
            print("    • Upgrade Python to version 3.7 or higher")
        
        if validation_results['requirements']['failed_imports']:
            failed_deps = validation_results['requirements']['failed_imports']
            print(f"    • Install missing dependencies: {', '.join(failed_deps)}")
        
        if validation_results['modules']['failed_imports']:
            failed_mods = validation_results['modules']['failed_imports']
            print(f"    • Fix custom module imports: {', '.join(failed_mods)}")
        
        if validation_results['files']['required_files']['missing']:
            missing_files = validation_results['files']['required_files']['missing']
            print(f"    • Create missing required files: {', '.join(missing_files)}")
    
    print("\n" + "=" * 60)


def main():
    """Run all deployment validation checks."""
    print("🚀 Crypto Dashboard Deployment Validation")
    print("=" * 60)
    
    validation_results = {}
    
    # Run all validation checks
    validation_results['python'] = validate_python_version()
    validation_results['requirements'] = validate_requirements()
    validation_results['modules'] = validate_custom_modules()
    validation_results['files'] = validate_file_structure()
    validation_results['api'] = validate_api_connectivity()
    validation_results['streamlit'] = validate_streamlit_compatibility()
    
    # Generate comprehensive report
    generate_deployment_report(validation_results)


if __name__ == "__main__":
    main()