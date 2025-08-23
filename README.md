# Crypto Dashboard

A live cryptocurrency analytics dashboard that provides real-time market data, historical price charts, and portfolio tracking capabilities.

## Features

- **Real-time Market Data**: Live prices, 24h changes, and market statistics for major cryptocurrencies
- **Top 10 Cryptos**: Interactive table showing the most actively traded cryptocurrencies by volume
- **Historical Charts**: Interactive candlestick charts with multiple timeframes (1h, 4h, 1d, 1w)
- **Search Functionality**: Search for specific cryptocurrencies and view their live statistics
- **Portfolio Tracker**: Track your cryptocurrency holdings and monitor portfolio performance
- **Modern UI**: Clean, responsive design optimized for both desktop and mobile

## Tech Stack

- **Frontend**: Streamlit
- **Data Source**: Binance Public API
- **Data Processing**: Pandas
- **Visualizations**: Plotly
- **Deployment**: Streamlit Community Cloud

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd crypto-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Project Structure

```
crypto-dashboard/
├── app.py                 # Main Streamlit application
├── src/
│   ├── api/              # Binance API integration
│   ├── data/             # Data processing and formatting
│   ├── ui/               # UI components and styling
│   └── utils/            # Utility functions and configuration
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── config.yaml          # Application configuration
└── README.md            # Project documentation
```

## Development Status

🚧 **In Development** - This project is currently being built as part of a portfolio demonstration.

## License

This project is open source and available under the [MIT License](LICENSE).