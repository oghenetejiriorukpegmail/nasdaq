import os
import json
import requests
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime

# Define thresholds for recommended buys
WEEKLY_RSI_THRESHOLD = 20.0
WEEKLY_STOCH_RSI_THRESHOLD = 10.0

def update_ticker_files(directory, tickers_file):
    """
    Update individual HTML files for each ticker with current price and technical indicators.
    Also identifies and saves recommended buy opportunities based on RSI thresholds.
    
    Args:
        directory (str): Directory where ticker HTML files will be saved
        tickers_file (str): Path to file containing ticker symbols (one per line)
    
    Returns:
        list: List of recommended buy tickers (with weekly RSI < 20 and weekly stochastic RSI < 10)
    """
    # Initialize list to store recommended buys
    recommended_buys = []
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # Read ticker symbols from file
    try:
        with open(tickers_file, "r") as f:
            tickers = [line.strip() for line in f if line.strip()]
        
        if not tickers:
            print(f"No tickers found in {tickers_file}")
            return
    except Exception as e:
        print(f"Error reading tickers file {tickers_file}: {e}")
        return

    # User agent for API requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Process each ticker
    for symbol in tickers:
        filepath = os.path.join(directory, f"{symbol}.html")
        print(f"Processing {symbol}...")
        
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        
        try:
            # Fetch current stock data from Yahoo Finance API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data or 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                print(f"No data found for {symbol}")
                continue

            # Extract close price
            try:
                close_price = data['chart']['result'][0]['indicators']['quote'][0]['close'][0]
                if close_price is None:
                    print(f"No close price found for {symbol}")
                    close_price = 0.0
            except (KeyError, IndexError) as e:
                print(f"Error extracting close price for {symbol}: {e}")
                close_price = 0.0

            # Fetch historical data for technical indicators
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=60d&interval=1d"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Initialize indicators with default values
            rsi = float('NaN')
            stoch_rsi = float('NaN')
            weekly_rsi = float('NaN')
            weekly_stoch_rsi = float('NaN')
            
            # Process daily data
            if data.get('chart', {}).get('result'):
                try:
                    result = data['chart']['result'][0]
                    timestamps = result.get('timestamp', [])
                    quotes = result.get('indicators', {}).get('quote', [{}])[0]
                    
                    if timestamps and all(key in quotes for key in ['open', 'high', 'low', 'close', 'volume']):
                        historical_data = pd.DataFrame(quotes, index=pd.to_datetime(timestamps, unit='s'))
                        
                        if not historical_data.empty and 'close' in historical_data.columns:
                            # Calculate RSI
                            try:
                                rsi_series = ta.rsi(historical_data["close"], length=14)
                                if isinstance(rsi_series, pd.Series) and not rsi_series.empty:
                                    rsi = rsi_series.iloc[-1]
                            except Exception as e:
                                print(f"Error calculating RSI for {symbol}: {e}")

                            # Calculate Stochastic RSI
                            try:
                                stoch_rsi_series = ta.stochrsi(historical_data["close"])
                                if isinstance(stoch_rsi_series, pd.DataFrame) and not stoch_rsi_series.empty:
                                    stoch_rsi = stoch_rsi_series["STOCHRSIk_14_14_3_3"].iloc[-1]
                            except Exception as e:
                                print(f"Error calculating Stochastic RSI for {symbol}: {e}")
                except Exception as e:
                    print(f"Error processing daily data for {symbol}: {e}")
            
            # Fetch and process weekly data
            try:
                # Use a longer range (6 months) to ensure enough weekly data points
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=6mo&interval=1wk"
                print(f"Fetching weekly data for {symbol} from {url}")
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                weekly_data = response.json()
                
                if weekly_data.get('chart', {}).get('result'):
                    result = weekly_data['chart']['result'][0]
                    timestamps = result.get('timestamp', [])
                    quotes = result.get('indicators', {}).get('quote', [{}])[0]
                    
                    # Print debug info
                    print(f"Weekly data for {symbol}: {len(timestamps)} data points")
                    
                    if timestamps and all(key in quotes for key in ['open', 'high', 'low', 'close', 'volume']):
                        weekly_historical_data = pd.DataFrame(quotes, index=pd.to_datetime(timestamps, unit='s'))
                        
                        if not weekly_historical_data.empty and 'close' in weekly_historical_data.columns:
                            # Check for NaN values and clean data
                            if weekly_historical_data['close'].isna().any():
                                print(f"Warning: NaN values found in weekly data for {symbol}, cleaning...")
                                weekly_historical_data = weekly_historical_data.dropna(subset=['close'])
                            
                            # Calculate weekly RSI
                            try:
                                # Need at least 15 data points for a 14-period RSI
                                if len(weekly_historical_data) >= 15:
                                    weekly_rsi_series = ta.rsi(weekly_historical_data["close"], length=14)
                                    if isinstance(weekly_rsi_series, pd.Series) and not weekly_rsi_series.empty:
                                        weekly_rsi = weekly_rsi_series.iloc[-1]
                                        print(f"Successfully calculated weekly RSI for {symbol}: {weekly_rsi}")
                                else:
                                    print(f"Not enough weekly data points for {symbol} to calculate RSI: {len(weekly_historical_data)}")
                            except Exception as e:
                                print(f"Error calculating weekly RSI for {symbol}: {e}")

                            # Calculate weekly Stochastic RSI
                            try:
                                # For Stochastic RSI we need even more data points
                                if len(weekly_historical_data) >= 30:  # Need more points for stochastic calculation
                                    weekly_stoch_rsi_series = ta.stochrsi(weekly_historical_data["close"])
                                    if isinstance(weekly_stoch_rsi_series, pd.DataFrame) and not weekly_stoch_rsi_series.empty:
                                        weekly_stoch_rsi = weekly_stoch_rsi_series["STOCHRSIk_14_14_3_3"].iloc[-1]
                                        print(f"Successfully calculated weekly Stochastic RSI for {symbol}: {weekly_stoch_rsi}")
                                else:
                                    print(f"Not enough weekly data points for {symbol} to calculate Stochastic RSI: {len(weekly_historical_data)}")
                                    
                                    # Alternative: If we have enough data for RSI but not StochRSI, use a simpler calculation
                                    if len(weekly_historical_data) >= 15 and not pd.isna(weekly_rsi):
                                        # Simple alternative: normalize the RSI value to 0-100 range
                                        weekly_stoch_rsi = (weekly_rsi - 30) * (100 / (70 - 30)) if 30 <= weekly_rsi <= 70 else (
                                            0 if weekly_rsi < 30 else 100)
                                        print(f"Used alternative weekly Stochastic RSI calculation for {symbol}: {weekly_stoch_rsi}")
                            except Exception as e:
                                print(f"Error calculating weekly Stochastic RSI for {symbol}: {e}")
                        else:
                            print(f"Empty or invalid weekly historical data for {symbol}")
                    else:
                        print(f"Missing required fields in weekly data for {symbol}")
                else:
                    print(f"No weekly chart results found for {symbol}")
            except Exception as e:
                print(f"Error processing weekly data for {symbol}: {e}")

            # Check if this stock meets the recommended buy criteria
            if (not pd.isna(weekly_rsi) and not pd.isna(weekly_stoch_rsi) and
                weekly_rsi < WEEKLY_RSI_THRESHOLD and weekly_stoch_rsi < WEEKLY_STOCH_RSI_THRESHOLD):
                recommended_buys.append({
                    'symbol': symbol,
                    'price': close_price,
                    'weekly_rsi': weekly_rsi,
                    'weekly_stoch_rsi': weekly_stoch_rsi
                })
                print(f"Added {symbol} to recommended buys: RSI={weekly_rsi:.2f}, StochRSI={weekly_stoch_rsi:.2f}")

            # Format indicator values for display
            rsi_str = f"{rsi:.2f}" if not pd.isna(rsi) else "N/A"
            stoch_rsi_str = f"{stoch_rsi:.2f}" if not pd.isna(stoch_rsi) else "N/A"
            weekly_rsi_str = f"{weekly_rsi:.2f}" if not pd.isna(weekly_rsi) else "N/A"
            weekly_stoch_rsi_str = f"{weekly_stoch_rsi:.2f}" if not pd.isna(weekly_stoch_rsi) else "N/A"

            # Create HTML content with improved styling
            new_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} - Stock Info</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #0a66c2;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .stock-info {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .info-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
        }}
        .price {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .indicator {{
            margin: 10px 0;
        }}
        .indicator-name {{
            font-weight: bold;
        }}
        .indicator-value {{
            float: right;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 0.8em;
            color: #666;
            text-align: center;
        }}
        a {{
            color: #0a66c2;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>{symbol}</h1>
    <div class="stock-info">
        <div class="info-card">
            <div class="price">Price: ${close_price:.2f}</div>
            <div class="indicator">
                <span class="indicator-name">RSI (Daily):</span>
                <span class="indicator-value">{rsi_str}</span>
            </div>
            <div class="indicator">
                <span class="indicator-name">Stochastic RSI (Daily):</span>
                <span class="indicator-value">{stoch_rsi_str}</span>
            </div>
        </div>
        <div class="info-card">
            <div class="indicator">
                <span class="indicator-name">RSI (Weekly):</span>
                <span class="indicator-value">{weekly_rsi_str}</span>
            </div>
            <div class="indicator">
                <span class="indicator-name">Stochastic RSI (Weekly):</span>
                <span class="indicator-value">{weekly_stoch_rsi_str}</span>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><a href="../index.html">Back to NASDAQ 100 List</a></p>
    </div>
</body>
</html>"""

            # Write HTML file
            with open(filepath, "w") as f:
                f.write(new_content)
                
            print(f"Successfully updated {symbol}")

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    # Save recommended buys to a JSON file for the frontend
    recommended_buys_file = os.path.join(os.path.dirname(directory), "recommended_buys.json")
    with open(recommended_buys_file, "w") as f:
        json.dump(recommended_buys, f, indent=2)
    
    print(f"Found {len(recommended_buys)} recommended buy opportunities")
    return recommended_buys

if __name__ == "__main__":
    update_ticker_files("nasdaq_display/tickers", "Stocks_Scanner/nasdaq100_tickers.txt")
