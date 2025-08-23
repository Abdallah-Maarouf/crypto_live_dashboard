"""
Unit tests for BinanceClient.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from src.api.binance_client import BinanceClient, BinanceAPIError


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