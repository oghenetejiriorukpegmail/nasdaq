# NASDAQ Display

A web-based application for displaying NASDAQ 100 stock information with technical indicators.

## Features

- Fetches and displays current NASDAQ 100 tickers
- Shows current price for each ticker
- Calculates and displays technical indicators:
  - RSI (Relative Strength Index) - Daily and Weekly
  - Stochastic RSI - Daily and Weekly
- Responsive web interface
- Local HTTP server for viewing the data

## Project Structure

- `main.py` - Main script to run the application
- `nasdaq_tickers.py` - Fetches NASDAQ 100 tickers from the web
- `update_ticker_files.py` - Updates individual HTML files for each ticker
- `update_tickers_json.py` - Updates the tickers.json file with current prices
- `scan.py` - Updates the main index.html file
- `start_server.py` - Starts a local HTTP server to view the data
- `requirements.txt` - Python dependencies

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install -r Stocks_Scanner/requirements.txt
```

## Usage

### Update Data

To update all NASDAQ data:

```bash
python Stocks_Scanner/main.py update
```

### Start Server

To start the HTTP server:

```bash
python Stocks_Scanner/main.py server
```

### Update Data and Start Server

To update data and start the server in one command:

```bash
python Stocks_Scanner/main.py run
```

## Data Sources

- NASDAQ 100 tickers are fetched from [SlickCharts](https://www.slickcharts.com/nasdaq100)
- Stock price and historical data are fetched from Yahoo Finance API

## Technical Indicators

- **RSI (Relative Strength Index)**: A momentum oscillator that measures the speed and change of price movements. RSI oscillates between 0 and 100. Traditionally, RSI is considered overbought when above 70 and oversold when below 30.

- **Stochastic RSI**: A technical indicator derived from the Stochastic Oscillator and applied to the RSI values rather than price data. It provides a more sensitive measure of RSI momentum.

## License

MIT