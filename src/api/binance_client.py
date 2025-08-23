"""
Binance API client for fetching cryptocurrency data.
"""

import time
import requests
from typing import Dict, List, Optional, Any
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def cache_response(ttl_seconds: int):
    """
    Simple caching decorator for API responses.
    
    Args:
        ttl_seconds: Time to live for cached responses in seconds
    """
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            current_time = time.time()
            
            # Clean up expired cache entries first
            keys_to_remove = []
            for key, (_, timestamp) in cache.items():
                if current_time - timestamp >= ttl_seconds:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del cache[key]
            
            # Check if we have a valid cached response
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_data
            
            # Make the actual API call
            logger.debug(f"Cache miss for {func.__name__}, making API call")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache[cache_key] = (result, current_time)
            
            return result
        
        return wrapper
    return decorator


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
    
    @cache_response(3600)  # Cache for 1 hour - exchange info doesn't change frequently
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange information from Binance API.
        
        Returns:
            Exchange information response containing trading rules and symbol information
        """
        return self._make_request("/exchangeInfo")
    
    @cache_response(30)  # Cache for 30 seconds - balance freshness with API limits
    def get_ticker_24hr(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get 24hr ticker price change statistics.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT'). If None, returns all symbols.
            
        Returns:
            24hr ticker statistics for the symbol(s)
        """
        params = {}
        if symbol:
            params['symbol'] = symbol.upper()
        
        return self._make_request("/ticker/24hr", params)
    
    @cache_response(300)  # Cache for 5 minutes - historical data doesn't change frequently
    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List[Any]]:
        """
        Get historical candlestick data (klines).
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., '1h', '4h', '1d', '1w')
            limit: Number of klines to return (default: 500, max: 1000)
            
        Returns:
            List of kline data arrays [open_time, open, high, low, close, volume, close_time, ...]
        """
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': min(limit, 1000)  # Enforce API limit
        }
        
        return self._make_request("/klines", params)