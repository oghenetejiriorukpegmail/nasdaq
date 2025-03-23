import os
import json
import re

def update_tickers_json(tickers_dir, tickers_json_path):
    """
    Update the tickers.json file with data extracted from individual ticker HTML files.
    
    Args:
        tickers_dir (str): Directory containing ticker HTML files
        tickers_json_path (str): Path where the tickers.json file will be saved
    """
    if not os.path.exists(tickers_dir):
        print(f"Tickers directory {tickers_dir} does not exist")
        return
        
    tickers = []
    
    # Process each HTML file in the directory
    for filename in os.listdir(tickers_dir):
        if filename.endswith(".html"):
            symbol = filename[:-5]  # Remove .html extension
            filepath = os.path.join(tickers_dir, filename)
            
            try:
                with open(filepath, "r") as f:
                    content = f.read()

                # Extract the price using regex for more robust parsing
                # This handles both the old format (<p>Price: $123.45</p>) and new format (class="price")
                price_match = re.search(r'<div class="price">Price: \$([\d.]+)', content)
                if price_match:
                    price = price_match.group(1)
                else:
                    # Fall back to old format
                    price_match = re.search(r'<p>Price: \$([\d.]+)</p>', content)
                    if price_match:
                        price = price_match.group(1)
                    else:
                        print(f"Could not extract price for {symbol}")
                        price = "N/A"

                tickers.append({"symbol": symbol, "price": price})
                print(f"Added {symbol} with price {price} to tickers.json")
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
    
    # Sort tickers alphabetically by symbol
    tickers.sort(key=lambda x: x["symbol"])
    
    # Write to JSON file
    try:
        with open(tickers_json_path, "w") as f:
            json.dump(tickers, f, indent=4)
        print(f"Successfully updated {tickers_json_path} with {len(tickers)} tickers")
    except Exception as e:
        print(f"Error writing to {tickers_json_path}: {e}")

if __name__ == "__main__":
    update_tickers_json("nasdaq_display/tickers", "nasdaq_display/tickers.json")
