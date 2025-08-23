"""
Unit tests for BinanceClient.
"""

import pytest
import requests
import time
from unittest.mock import Mock, patch
from src.api.binance_client import BinanceClient, BinanceAPIError, cache_response


class TestBinanceClient:
    """Test cases for BinanceClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = BinanceClient(timeout=5, max_retries=3)
    
    def test_init(self):
        """Test client initialization."""
        assert self.client.timeout == 5
        assert self.client.max_retries == 3
        assert self.client.BASE_URL == "https://api.binance.com/api/v3"
        assert self.client.session.headers['User-Agent'] == 'CryptoDashboard/1.0'
        assert self.client.session.headers['Content-Type'] == 'application/json'
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'serverTime': 1640995200000}
        mock_get.return_value = mock_response
        
        result = self.client._make_request('/time')
        
        assert result == {'serverTime': 1640995200000}
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/time',
            params=None,
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_make_request_with_params(self, mock_get):
        """Test API request with parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        params = {'symbol': 'BTCUSDT', 'limit': 10}
        result = self.client._make_request('/ticker/24hr', params)
        
        assert result == {'data': 'test'}
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/24hr',
            params=params,
            timeout=5
        )    

    @patch('src.api.binance_client.time.sleep')
    @patch('src.api.binance_client.requests.Session.get')
    def test_rate_limit_retry(self, mock_get, mock_sleep):
        """Test rate limit handling with exponential backoff."""
        # First call returns 429, second call succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'data': 'success'}
        
        mock_get.side_effect = [mock_response_429, mock_response_200]
        
        result = self.client._make_request('/time')
        
        assert result == {'data': 'success'}
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(1)  # 2^0 = 1 second wait
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_rate_limit_max_retries_exceeded(self, mock_get):
        """Test rate limit with max retries exceeded."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with pytest.raises(BinanceAPIError, match="Rate limit exceeded after all retries"):
            self.client._make_request('/time')
        
        assert mock_get.call_count == 4  # Initial + 3 retries
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_http_error_handling(self, mock_get):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        with pytest.raises(BinanceAPIError, match="Request failed after all retries"):
            self.client._make_request('/time')
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_timeout_handling(self, mock_get):
        """Test timeout handling."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with pytest.raises(BinanceAPIError, match="Request timeout after all retries"):
            self.client._make_request('/time')    

    @patch('src.api.binance_client.requests.Session.get')
    def test_invalid_json_response(self, mock_get):
        """Test invalid JSON response handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(BinanceAPIError, match="Invalid JSON response"):
            self.client._make_request('/time')
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_server_time(self, mock_get):
        """Test get_server_time method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'serverTime': 1640995200000}
        mock_get.return_value = mock_response
        
        result = self.client.get_server_time()
        
        assert result == {'serverTime': 1640995200000}
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/time',
            params=None,
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_exchange_info(self, mock_get):
        """Test get_exchange_info method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'timezone': 'UTC', 'serverTime': 1640995200000}
        mock_get.return_value = mock_response
        
        result = self.client.get_exchange_info()
        
        assert result == {'timezone': 'UTC', 'serverTime': 1640995200000}
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/exchangeInfo',
            params=None,
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_ticker_24hr_single_symbol(self, mock_get):
        """Test get_ticker_24hr method with single symbol."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'symbol': 'BTCUSDT',
            'priceChange': '1000.00',
            'priceChangePercent': '2.50',
            'lastPrice': '41000.00',
            'volume': '12345.67',
            'high': '42000.00',
            'low': '40000.00'
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_ticker_24hr('BTCUSDT')
        
        assert result['symbol'] == 'BTCUSDT'
        assert result['lastPrice'] == '41000.00'
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/24hr',
            params={'symbol': 'BTCUSDT'},
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_ticker_24hr_all_symbols(self, mock_get):
        """Test get_ticker_24hr method for all symbols."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'symbol': 'BTCUSDT',
                'priceChange': '1000.00',
                'priceChangePercent': '2.50',
                'lastPrice': '41000.00'
            },
            {
                'symbol': 'ETHUSDT',
                'priceChange': '100.00',
                'priceChangePercent': '3.20',
                'lastPrice': '3200.00'
            }
        ]
        mock_get.return_value = mock_response
        
        result = self.client.get_ticker_24hr()
        
        assert len(result) == 2
        assert result[0]['symbol'] == 'BTCUSDT'
        assert result[1]['symbol'] == 'ETHUSDT'
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/24hr',
            params={},
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_ticker_24hr_lowercase_symbol(self, mock_get):
        """Test get_ticker_24hr method converts lowercase symbol to uppercase."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'symbol': 'BTCUSDT', 'lastPrice': '41000.00'}
        mock_get.return_value = mock_response
        
        result = self.client.get_ticker_24hr('btcusdt')
        
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/ticker/24hr',
            params={'symbol': 'BTCUSDT'},
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_klines_default_limit(self, mock_get):
        """Test get_klines method with default limit."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [
                1640995200000,  # Open time
                "41000.00",     # Open
                "42000.00",     # High
                "40000.00",     # Low
                "41500.00",     # Close
                "123.45",       # Volume
                1640998799999,  # Close time
                "5067750.00",   # Quote asset volume
                1000,           # Number of trades
                "61.73",        # Taker buy base asset volume
                "2533875.00",   # Taker buy quote asset volume
                "0"             # Ignore
            ]
        ]
        mock_get.return_value = mock_response
        
        result = self.client.get_klines('BTCUSDT', '1h')
        
        assert len(result) == 1
        assert result[0][0] == 1640995200000  # Open time
        assert result[0][1] == "41000.00"     # Open price
        assert result[0][4] == "41500.00"     # Close price
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/klines',
            params={'symbol': 'BTCUSDT', 'interval': '1h', 'limit': 500},
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_klines_custom_limit(self, mock_get):
        """Test get_klines method with custom limit."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = self.client.get_klines('ETHUSDT', '4h', 100)
        
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/klines',
            params={'symbol': 'ETHUSDT', 'interval': '4h', 'limit': 100},
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_klines_limit_enforcement(self, mock_get):
        """Test get_klines method enforces API limit of 1000."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = self.client.get_klines('BTCUSDT', '1d', 1500)  # Request more than max
        
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/klines',
            params={'symbol': 'BTCUSDT', 'interval': '1d', 'limit': 1000},  # Should be capped at 1000
            timeout=5
        )
    
    @patch('src.api.binance_client.requests.Session.get')
    def test_get_klines_lowercase_symbol(self, mock_get):
        """Test get_klines method converts lowercase symbol to uppercase."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = self.client.get_klines('btcusdt', '1w', 50)
        
        mock_get.assert_called_once_with(
            'https://api.binance.com/api/v3/klines',
            params={'symbol': 'BTCUSDT', 'interval': '1w', 'limit': 50},
            timeout=5
        )


class TestCaching:
    """Test cases for caching functionality."""
    
    @patch('src.api.binance_client.time.time')
    def test_cache_hit(self, mock_time):
        """Test cache hit returns cached data without making API call."""
        mock_time.side_effect = [1000, 1010]  # 10 seconds later
        
        @cache_response(30)  # 30 second TTL
        def mock_api_call():
            return {'data': 'test_response'}
        
        # First call should execute function
        result1 = mock_api_call()
        assert result1 == {'data': 'test_response'}
        
        # Second call should return cached data
        result2 = mock_api_call()
        assert result2 == {'data': 'test_response'}
        assert result1 is result2  # Should be same object from cache
    
    def test_cache_miss_after_ttl(self):
        """Test cache miss after TTL expires."""
        call_count = 0
        
        @cache_response(1)  # 1 second TTL for easier testing
        def mock_api_call():
            nonlocal call_count
            call_count += 1
            return {'data': f'response_{call_count}'}
        
        # First call
        result1 = mock_api_call()
        assert result1 == {'data': 'response_1'}
        assert call_count == 1
        
        # Wait for cache to expire
        time.sleep(1.1)
        
        # Second call after TTL expires
        result2 = mock_api_call()
        assert result2 == {'data': 'response_2'}
        assert call_count == 2
    
    @patch('src.api.binance_client.time.time')
    def test_cache_with_different_args(self, mock_time):
        """Test cache distinguishes between different function arguments."""
        mock_time.return_value = 1000
        call_count = 0
        
        @cache_response(30)
        def mock_api_call(symbol):
            nonlocal call_count
            call_count += 1
            return {'symbol': symbol, 'call': call_count}
        
        # Different arguments should result in different cache entries
        result1 = mock_api_call('BTC')
        result2 = mock_api_call('ETH')
        result3 = mock_api_call('BTC')  # Should hit cache
        
        assert result1 == {'symbol': 'BTC', 'call': 1}
        assert result2 == {'symbol': 'ETH', 'call': 2}
        assert result3 == {'symbol': 'BTC', 'call': 1}  # Same as result1
        assert call_count == 2  # Only 2 actual calls made
    
    @patch('src.api.binance_client.requests.Session.get')
    @patch('src.api.binance_client.time.time')
    def test_api_method_caching_integration(self, mock_time, mock_get):
        """Test that API methods use caching correctly."""
        mock_time.side_effect = [1000, 1010, 1020]  # Within 30s TTL
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'symbol': 'BTCUSDT', 'price': '41000'}
        mock_get.return_value = mock_response
        
        client = BinanceClient()
        
        # First call should make API request
        result1 = client.get_ticker_24hr('BTCUSDT')
        assert mock_get.call_count == 1
        
        # Second call should use cache
        result2 = client.get_ticker_24hr('BTCUSDT')
        assert mock_get.call_count == 1  # No additional API call
        assert result1 == result2