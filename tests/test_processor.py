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
    prepare_chart_data,
    validate_portfolio_input,
    calculate_portfolio_value,
    get_portfolio_breakdown
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
        assert holding.percentage == 0.0
    
    def test_portfolio_holding_with_percentage(self):
        """Test PortfolioHolding with percentage specified."""
        holding = PortfolioHolding(
            symbol="BTC",
            quantity=1.0,
            current_value=45000.0,
            percentage=75.0
        )
        
        assert holding.percentage == 75.0


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


class TestValidatePortfolioInput:
    """Test portfolio input validation function."""
    
    def test_valid_symbol_and_quantity(self):
        """Test validation with valid symbol and quantity."""
        is_valid, error, quantity = validate_portfolio_input("BTC", "1.5")
        assert is_valid is True
        assert error == ""
        assert quantity == 1.5
    
    def test_valid_symbol_case_insensitive(self):
        """Test validation with lowercase symbol."""
        is_valid, error, quantity = validate_portfolio_input("eth", "10.0")
        assert is_valid is True
        assert error == ""
        assert quantity == 10.0
    
    def test_invalid_symbol_empty(self):
        assert quantity == 1.5
    
    def test_valid_symbol_case_insensitive(self):
        """Test validation with lowercase symbol."""
        is_valid, error, quantity = validate_portfolio_input("eth", "10.0")
        assert is_valid is True
        assert error == ""
        assert quantity == 10.0
    
    def test_invalid_symbol_empty(self):
        """Test validation with empty symbol."""
        is_valid, error, quantity = validate_portfolio_input("", "1.0")
        assert is_valid is False
        assert error == "Symbol is required"
        assert quantity is None
    
    def test_invalid_symbol_too_short(self):
        """Test validation with symbol too short."""
        is_valid, error, quantity = validate_portfolio_input("A", "1.0")
        assert is_valid is False
        assert error == "Symbol must be 2-10 letters only"
        assert quantity is None
    
    def test_invalid_symbol_too_long(self):
        """Test validation with symbol too long."""
        is_valid, error, quantity = validate_portfolio_input("VERYLONGSYMBOL", "1.0")
        assert is_valid is False
        assert error == "Symbol must be 2-10 letters only"
        assert quantity is None
    
    def test_invalid_symbol_with_numbers(self):
        """Test validation with symbol containing numbers."""
        is_valid, error, quantity = validate_portfolio_input("BTC1", "1.0")
        assert is_valid is False
        assert error == "Symbol must be 2-10 letters only"
        assert quantity is None
    
    def test_invalid_quantity_empty(self):
        """Test validation with empty quantity."""
        is_valid, error, quantity = validate_portfolio_input("BTC", "")
        assert is_valid is False
        assert error == "Quantity is required"
        assert quantity is None
    
    def test_invalid_quantity_negative(self):
        """Test validation with negative quantity."""
        is_valid, error, quantity = validate_portfolio_input("BTC", "-1.0")
        assert is_valid is False
        assert error == "Quantity must be positive"
        assert quantity is None
    
    def test_invalid_quantity_zero(self):
        """Test validation with zero quantity."""
        is_valid, error, quantity = validate_portfolio_input("BTC", "0")
        assert is_valid is False
        assert error == "Quantity must be positive"
        assert quantity is None
    
    def test_invalid_quantity_too_large(self):
        """Test validation with extremely large quantity."""
        is_valid, error, quantity = validate_portfolio_input("BTC", "1e13")
        assert is_valid is False
        assert error == "Quantity is too large"
        assert quantity is None
    
    def test_invalid_quantity_not_number(self):
        """Test validation with non-numeric quantity."""
        is_valid, error, quantity = validate_portfolio_input("BTC", "abc")
        assert is_valid is False
        assert error == "Quantity must be a valid number"
        assert quantity is None
    
    def test_valid_decimal_quantity(self):
        """Test validation with decimal quantity."""
        is_valid, error, quantity = validate_portfolio_input("ETH", "0.123456")
        assert is_valid is True
        assert error == ""
        assert quantity == 0.123456


class TestCalculatePortfolioValue:
    """Test portfolio value calculation function."""
    
    def test_calculate_empty_portfolio(self):
        """Test calculation with empty portfolio."""
        total_value, holdings, missing = calculate_portfolio_value([], {})
        assert total_value == 0.0
        assert holdings == []
        assert missing == []
    
    def test_calculate_single_holding(self):
        """Test calculation with single holding."""
        holdings = [{"symbol": "BTC", "quantity": 1.0}]
        prices = {"BTC": 45000.0}
        
        total_value, portfolio_holdings, missing = calculate_portfolio_value(holdings, prices)
        
        assert total_value == 45000.0
        assert len(portfolio_holdings) == 1
        assert portfolio_holdings[0].symbol == "BTC"
        assert portfolio_holdings[0].quantity == 1.0
        assert portfolio_holdings[0].current_value == 45000.0
        assert portfolio_holdings[0].percentage == 100.0
        assert missing == []
    
    def test_calculate_multiple_holdings(self):
        """Test calculation with multiple holdings."""
        holdings = [
            {"symbol": "BTC", "quantity": 1.0},
            {"symbol": "ETH", "quantity": 10.0},
            {"symbol": "ADA", "quantity": 1000.0}
        ]
        prices = {"BTC": 45000.0, "ETH": 3000.0, "ADA": 1.0}
        
        total_value, portfolio_holdings, missing = calculate_portfolio_value(holdings, prices)
        
        assert total_value == 76000.0  # 45000 + 30000 + 1000
        assert len(portfolio_holdings) == 3
        assert missing == []
        
        # Check BTC holding
        btc_holding = next(h for h in portfolio_holdings if h.symbol == "BTC")
        assert btc_holding.current_value == 45000.0
        assert abs(btc_holding.percentage - 59.21) < 0.01  # 45000/76000 * 100
        
        # Check ETH holding
        eth_holding = next(h for h in portfolio_holdings if h.symbol == "ETH")
        assert eth_holding.current_value == 30000.0
        assert abs(eth_holding.percentage - 39.47) < 0.01  # 30000/76000 * 100
        
        # Check ADA holding
        ada_holding = next(h for h in portfolio_holdings if h.symbol == "ADA")
        assert ada_holding.current_value == 1000.0
        assert abs(ada_holding.percentage - 1.32) < 0.01  # 1000/76000 * 100
    
    def test_calculate_with_missing_prices(self):
        """Test calculation with some missing price data."""
        holdings = [
            {"symbol": "BTC", "quantity": 1.0},
            {"symbol": "ETH", "quantity": 10.0},
            {"symbol": "UNKNOWN", "quantity": 100.0}
        ]
        prices = {"BTC": 45000.0, "ETH": 3000.0}
        
        total_value, portfolio_holdings, missing = calculate_portfolio_value(holdings, prices)
        
        assert total_value == 75000.0  # 45000 + 30000
        assert len(portfolio_holdings) == 2
        assert missing == ["UNKNOWN"]
    
    def test_calculate_case_insensitive_symbols(self):
        """Test calculation with lowercase symbols in holdings."""
        holdings = [{"symbol": "btc", "quantity": 1.0}]
        prices = {"BTC": 45000.0}
        
        total_value, portfolio_holdings, missing = calculate_portfolio_value(holdings, prices)
        
        assert total_value == 45000.0
        assert len(portfolio_holdings) == 1
        assert portfolio_holdings[0].symbol == "BTC"
        assert missing == []
    
    def test_calculate_zero_quantity(self):
        """Test calculation with zero quantity holding."""
        holdings = [{"symbol": "BTC", "quantity": 0.0}]
        prices = {"BTC": 45000.0}
        
        total_value, portfolio_holdings, missing = calculate_portfolio_value(holdings, prices)
        
        assert total_value == 0.0
        assert len(portfolio_holdings) == 1
        assert portfolio_holdings[0].current_value == 0.0
        assert portfolio_holdings[0].percentage == 0.0
        assert missing == []


class TestGetPortfolioBreakdown:
    """Test portfolio breakdown function."""
    
    def test_breakdown_empty_portfolio(self):
        """Test breakdown with empty portfolio."""
        breakdown = get_portfolio_breakdown([])
        
        assert breakdown['total_value'] == 0.0
        assert breakdown['total_coins'] == 0
        assert breakdown['holdings'] == []
        assert breakdown['largest_holding'] is None
        assert breakdown['smallest_holding'] is None
    
    def test_breakdown_single_holding(self):
        """Test breakdown with single holding."""
        holdings = [PortfolioHolding("BTC", 1.0, 45000.0, 100.0)]
        breakdown = get_portfolio_breakdown(holdings)
        
        assert breakdown['total_value'] == 45000.0
        assert breakdown['total_coins'] == 1
        assert len(breakdown['holdings']) == 1
        assert breakdown['largest_holding'].symbol == "BTC"
        assert breakdown['smallest_holding'].symbol == "BTC"
    
    def test_breakdown_multiple_holdings_sorted(self):
        """Test breakdown with multiple holdings sorted by value."""
        holdings = [
            PortfolioHolding("ADA", 1000.0, 1000.0, 1.32),
            PortfolioHolding("BTC", 1.0, 45000.0, 59.21),
            PortfolioHolding("ETH", 10.0, 30000.0, 39.47)
        ]
        breakdown = get_portfolio_breakdown(holdings)
        
        assert breakdown['total_value'] == 76000.0
        assert breakdown['total_coins'] == 3
        assert len(breakdown['holdings']) == 3
        
        # Check sorting (should be BTC, ETH, ADA by value)
        assert breakdown['holdings'][0].symbol == "BTC"
        assert breakdown['holdings'][1].symbol == "ETH"
        assert breakdown['holdings'][2].symbol == "ADA"
        
        assert breakdown['largest_holding'].symbol == "BTC"
        assert breakdown['smallest_holding'].symbol == "ADA"
    
    def test_breakdown_equal_values(self):
        """Test breakdown with equal value holdings."""
        holdings = [
            PortfolioHolding("BTC", 0.5, 22500.0, 50.0),
            PortfolioHolding("ETH", 7.5, 22500.0, 50.0)
        ]
        breakdown = get_portfolio_breakdown(holdings)
        
        assert breakdown['total_value'] == 45000.0
        assert breakdown['total_coins'] == 2
        assert breakdown['largest_holding'].current_value == 22500.0
        assert breakdown['smallest_holding'].current_value == 22500.0