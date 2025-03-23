import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

def get_nasdaq_tickers():
    """
    Get NASDAQ 100 tickers from SlickCharts and fetch current prices from Yahoo Finance.
    
    Returns:
        list: List of dictionaries with ticker symbols and current prices
    """
    url = "https://www.slickcharts.com/nasdaq100"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table containing the tickers
    table = soup.find('table', class_='table table-hover table-borderless table-sm')
    if not table:
        print("Could not find table with tickers")
        return []

    # Extract ticker symbols
    ticker_symbols = []
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if cells and len(cells) > 2:
            ticker_link = cells[2].find('a')
            if ticker_link:
                ticker_symbol = ticker_link.text.strip()
                # Remove '$' sign if present
                if ticker_symbol.startswith('$'):
                    ticker_symbol = ticker_symbol[1:]
                ticker_symbols.append(ticker_symbol)
    
    # Fetch current prices from Yahoo Finance
    tickers = []
    for symbol in ticker_symbols:
        try:
            # Add delay to avoid rate limiting
            time.sleep(0.2)
            
            # Fetch current price from Yahoo Finance API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract the current price
            price = "N/A"
            if data and 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                if 'indicators' in result and 'quote' in result['indicators'] and result['indicators']['quote']:
                    quote = result['indicators']['quote'][0]
                    if 'close' in quote and quote['close'] and quote['close'][0] is not None:
                        price = f"{quote['close'][0]:.2f}"
            
            tickers.append({"symbol": symbol, "price": price})
            print(f"Fetched price for {symbol}: ${price}")
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            tickers.append({"symbol": symbol, "price": "N/A"})
    
    # Sort tickers alphabetically
    tickers.sort(key=lambda x: x["symbol"])
    
    return tickers

def save_tickers_to_json():
    """
    Get NASDAQ tickers with prices and save to JSON and text files.
    
    Returns:
        list: List of ticker dictionaries
    """
    print("Fetching NASDAQ 100 tickers with current prices...")
    tickers = get_nasdaq_tickers()
    
    # Save to JSON file for the web interface
    with open('nasdaq_display/tickers.json', 'w') as f:
        json.dump(tickers, f, indent=4)
    print(f"Saved {len(tickers)} tickers to nasdaq_display/tickers.json")
    
    # Save ticker symbols to text file for update_ticker_files.py
    with open('Stocks_Scanner/nasdaq100_tickers.txt', 'w') as f:
        for ticker in tickers:
            f.write(f"{ticker['symbol']}\n")
    print(f"Saved {len(tickers)} ticker symbols to Stocks_Scanner/nasdaq100_tickers.txt")
    
    return tickers

if __name__ == "__main__":
    save_tickers_to_json()
