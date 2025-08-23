"""
Unit tests for data processing and formatting utilities.
"""

import pytest
import pandas as pd
from src.data.processor import (
    CoinData, 
    PortfolioHolding, 
    format_price_data, 
    format_percentage_change, 
    prepare_chart_data
)


class TestCoinData:
    """Test CoinData dataclass."""
    
    def test_coin_data_creation(self):
        """Test CoinData can be created with all required fields."""
        coin = CoinData(
            symbol="BTC",
            price=45000.0,
            change_24h=2.5,
            high_24h=46000.0,
            low_24h=44000.0,
            volume=1000000.0
        )
        
        assert coin.symbol == "BTC"
        assert coin.price == 45000.0
        assert coin.change_24h == 2.5
        assert coin.high_24h == 46000.0
        assert coin.low_24h == 44000.0
        assert coin.volume == 1000000.0


class TestPortfolioHolding:
    """Test PortfolioHolding dataclass."""
    
    def test_portfolio_holding_creation(self):
        """Test PortfolioHolding can be created with all required fields."""
        holding = PortfolioHolding(
            symbol="ETH",
            quantity=10.5,
            current_value=35000.0
        )
        
        assert holding.symbol == "ETH"
        assert holding.quantity == 10.5
        assert holding.current_value == 35000.0


class TestFormatPriceData:
    """Test price formatting function."""
    
    def test_format_high_price(self):
        """Test formatting for prices >= $1000."""
        result = format_price_data(45234.56)
        assert result == "$45,234.56"
        
    def test_format_medium_price(self):
        """Test formatting for prices >= $1."""
        result = format_price_data(123.456789)
        assert result == "$123.4568"
        
    def test_format_low_price(self):
        """Test formatting for prices >= $0.01."""
        result = format_price_data(0.123456)
        assert result == "$0.123456"
        
    def test_format_very_low_price(self):
        """Test formatting for prices < $0.01."""
        result = format_price_data(0.00123456)
        assert result == "$0.00123456"
        
    def test_format_zero_price(self):
        """Test formatting for zero price."""
        result = format_price_data(0.0)
        assert result == "$0.00000000"


class TestFormatPercentageChange:
    """Test percentage change formatting function."""
    
    def test_positive_change(self):
        """Test formatting positive percentage change."""
        formatted, color = format_percentage_change(5.67)
        assert formatted == "+5.67%"
        assert color == "green"
        
    def test_negative_change(self):
        """Test formatting negative percentage change."""
        formatted, color = format_percentage_change(-3.45)
        assert formatted == "-3.45%"
        assert color == "red"
        
    def test_zero_change(self):
        """Test formatting zero percentage change."""
        formatted, color = format_percentage_change(0.0)
        assert formatted == "0.00%"
        assert color == "gray"
        
    def test_small_positive_change(self):
        """Test formatting small positive change."""
        formatted, color = format_percentage_change(0.01)
        assert formatted == "+0.01%"
        assert color == "green"


class TestPrepareChartData:
    """Test chart data preparation function."""
    
    def test_prepare_chart_data_valid_input(self):
        """Test preparing chart data with valid klines input."""
        # Sample klines data format from Binance API
        klines_data = [
            [
                1499040000000,      # Open time
                "0.01634790",       # Open
                "0.80000000",       # High
                "0.01575800",       # Low
                "0.01577100",       # Close
                "148976.11427815",  # Volume
                1499644799999,      # Close time
                "2434.19055334",    # Quote asset volume
                308,                # Number of trades
                "1756.87402397",    # Taker buy base asset volume
                "28.46694368",      # Taker buy quote asset volume
                "17928899.62484339" # Ignore
            ],
            [
                1499040060000,
                "0.01577100",
                "0.01577100",
                "0.01577100",
                "0.01577100",
                "0.00000000",
                1499644859999,
                "0.00000000",
                0,
                "0.00000000",
                "0.00000000",
                "0"
            ]
        ]
        
        result = prepare_chart_data(klines_data)
        
        # Check DataFrame structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(result['timestamp'])
        assert result['open'].dtype == float
        assert result['high'].dtype == float
        assert result['low'].dtype == float
        assert result['close'].dtype == float
        assert result['volume'].dtype == float
        
        # Check first row values
        assert result.iloc[0]['open'] == 0.01634790
        assert result.iloc[0]['high'] == 0.80000000
        assert result.iloc[0]['low'] == 0.01575800
        assert result.iloc[0]['close'] == 0.01577100
        assert result.iloc[0]['volume'] == 148976.11427815
    
    def test_prepare_chart_data_empty_input(self):
        """Test preparing chart data with empty input."""
        result = prepare_chart_data([])
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert result.empty
    
    def test_prepare_chart_data_single_candle(self):
        """Test preparing chart data with single candle."""
        klines_data = [
            [
                1499040000000,
                "45000.00",
                "46000.00",
                "44000.00",
                "45500.00",
                "1000.00",
                1499644799999,
                "45500000.00",
                100,
                "500.00",
                "22750000.00",
                "0"
            ]
        ]
        
        result = prepare_chart_data(klines_data)
        
        assert len(result) == 1
        assert result.iloc[0]['open'] == 45000.00
        assert result.iloc[0]['high'] == 46000.00
        assert result.iloc[0]['low'] == 44000.00
        assert result.iloc[0]['close'] == 45500.00
        assert result.iloc[0]['volume'] == 1000.00