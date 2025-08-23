"""
Binance API client for fetching cryptocurrency data.
"""

import time
import requests
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors."""
    pass


class BinanceClient:
    """
    Client for interacting with Binance public API endpoints.
    
    Handles HTTP requests with error handling, rate limiting, and exponential backoff.
    """
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self, timeout: int = 5, max_retries: int = 3):
        """
        Initialize the Binance API client.
        
        Args:
            timeout: Request timeout in seconds (default: 5)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'CryptoDashboard/1.0',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Binance API with error handling and exponential backoff.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            BinanceAPIError: If request fails after all retries
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout
                )
                
                # Handle rate limiting (HTTP 429)
                if response.status_code == 429:
                    if attempt < self.max_retries:
                        # Exponential backoff: 1s, 2s, 4s
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited. Retrying in {wait_time}s (attempt {attempt + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise BinanceAPIError("Rate limit exceeded after all retries")
                
                # Handle other HTTP errors
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request failed. Retrying in {wait_time}s (attempt {attempt + 1}): {error_msg}")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise BinanceAPIError(f"Request failed after all retries: {error_msg}")
                
                # Parse JSON response
                try:
                    return response.json()
                except ValueError as e:
                    raise BinanceAPIError(f"Invalid JSON response: {e}")
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request timeout. Retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise BinanceAPIError("Request timeout after all retries")
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request error. Retrying in {wait_time}s (attempt {attempt + 1}): {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise BinanceAPIError(f"Request failed after all retries: {e}")
        
        # This should never be reached, but just in case
        raise BinanceAPIError("Unexpected error in request handling")
    
    def get_server_time(self) -> Dict[str, Any]:
        """
        Get server time from Binance API.
        
        Returns:
            Server time response
        """
        return self._make_request("/time")
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange information from Binance API.
        
        Returns:
            Exchange information response
        """
        return self._make_request("/exchangeInfo")