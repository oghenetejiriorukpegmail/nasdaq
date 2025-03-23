import json
import os
from nasdaq_tickers import get_nasdaq_tickers, save_tickers_to_json
from update_ticker_files import update_ticker_files

def update_index_html():
    # Create the tickers directory if it doesn't exist
    if not os.path.exists("nasdaq_display/tickers"):
        os.makedirs("nasdaq_display/tickers")

    # Update individual ticker HTML files and get recommended buys
    recommended_buys, good_buys = update_ticker_files("nasdaq_display/tickers", "Stocks_Scanner/nasdaq100_tickers.txt")

    # Save good buys to a JSON file
    with open("nasdaq_display/good_buys.json", "w") as f:
        json.dump(good_buys, f, indent=2)

    # Save recommended buys to a JSON file
    with open("nasdaq_display/recommended_buys.json", "w") as f:
        json.dump(recommended_buys, f, indent=2)

    # Fetch NASDAQ 100 ticker data and save to files
    tickers = save_tickers_to_json()

    # Generate HTML content
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASDAQ 100 Tickers</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2 {
            color: #0a66c2;
            text-align: center;
        }
        .recommended-buys {
            background-color: #f8f9fa;
            border: 2px solid #28a745;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .recommended-buys h2 {
            color: #28a745;
            margin-top: 0;
        }
        .recommended-buys p {
            text-align: center;
            color: #666;
            font-style: italic;
            margin: 10px 0;
        }
        .recommended-buys ul {
            list-style-type: none;
            padding: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        .recommended-buys li {
            background-color: white;
            padding: 15px;
            border: 1px solid #28a745;
            border-radius: 6px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .recommended-buys li:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .recommended-buys .metrics {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        #good-buys {
            background-color: #f8f9fa;
            border: 2px solid #28a745;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        #good-buys h2 {
            color: #28a745;
            margin-top: 0;
        }
        #good-buys p {
            text-align: center;
            color: #666;
            font-style: italic;
            margin: 10px 0;
        }
        #good-buys ul {
            list-style-type: none;
            padding: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        #good-buys li {
            background-color: white;
            padding: 15px;
            border: 1px solid #28a745;
            border-radius: 6px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        #good-buys li:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        #good-buys .metrics {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        #tickers-container ul {
            list-style-type: none;
            padding: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }
        #tickers-container li {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        #tickers-container li:hover {
            background-color: #f5f5f5;
        }
        #tickers-container a {
            text-decoration: none;
            color: #333;
            display: block;
        }
        .last-updated {
            text-align: center;
            font-size: 0.8em;
            color: #666;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>NASDAQ 100 Tickers</h1>
    <div id="recommended-buys" class="recommended-buys">
        <h2>Recommended Buy Opportunities</h2>
        <p>Stocks with Weekly RSI < 20 and Weekly Stochastic RSI < 10</p>
    </div>
    <div id="good-buys" class="good-buys">
        <h2>Good Buy Opportunities</h2>
        <p>Stocks with Weekly Stochastic RSI < 20 and RSI < 35</p>
    </div>
    <div id="tickers-container">
    </div>
    <p class="last-updated">Last updated: <span id="update-time"></span></p>

    <script>
        // Format the current date and time
        const now = new Date();
        document.getElementById('update-time').textContent = now.toLocaleString();

        // Fetch and display recommended buys
        fetch('recommended_buys.json')
            .then(response => response.json())
            .then(recommendations => {
                const recommendedBuysContainer = document.getElementById('recommended-buys');
                if (recommendations.length > 0) {
                    let recommendedListHTML = '<ul>';
                    recommendations.forEach(stock => {
                        recommendedListHTML += `
                            <li>
                                <a href="tickers/${stock.symbol}.html">
                                    <strong>${stock.symbol}</strong>: $${stock.price.toFixed(2)}
                                    <div class="metrics">
                                        Weekly RSI: ${stock.weekly_rsi.toFixed(2)}<br>
                                        Weekly Stoch RSI: ${stock.weekly_stoch_rsi.toFixed(2)}
                                    </div>
                                </a>
                            </li>`;
                    });
                    recommendedListHTML += '</ul>';
                    recommendedBuysContainer.innerHTML += recommendedListHTML;
                } else {
                    recommendedBuysContainer.innerHTML += '<p>No recommended buys found at this time.</p>';
                }
            })
            .catch(error => {
                console.error('Error fetching recommended buys:', error);
                document.getElementById('recommended-buys').innerHTML += '<p>Error loading recommended buys.</p>';
            });

        // Fetch and display good buys
        fetch('good_buys.json')
            .then(response => response.json())
            .then(goodBuys => {
                const goodBuysContainer = document.getElementById('good-buys');
                if (goodBuys.length > 0) {
                    let goodBuysHTML = '<ul>';
                    goodBuys.forEach(stock => {
                        goodBuysHTML += `
                            <li>
                                <a href="tickers/${stock.symbol}.html">
                                    <strong>${stock.symbol}</strong>: $${stock.price.toFixed(2)}
                                    <div class="metrics">
                                        Weekly RSI: ${stock.weekly_rsi.toFixed(2)}<br>
                                        Weekly Stoch RSI: ${stock.weekly_stoch_rsi.toFixed(2)}
                                    </div>
                                </a>
                            </li>`;
                    });
                    goodBuysHTML += '</ul>';
                    goodBuysContainer.innerHTML += goodBuysHTML;
                } else {
                    goodBuysContainer.innerHTML += '<p>No good buys found at this time.</p>';
                }
            })
            .catch(error => {
                console.error('Error fetching good buys:', error);
                document.getElementById('good-buys').innerHTML += '<p>Error loading good buys.</p>';
            });

        // Fetch and display all tickers
        fetch('tickers.json')
            .then(response => response.json())
            .then(data => {
                const tickersContainer = document.getElementById('tickers-container');
                let tickerListHTML = '<ul>';
                data.forEach(ticker => {
                    // Check if price is a valid number or already has a $ prefix
                    const displayPrice = ticker.price.startsWith('$') ? ticker.price : `$${ticker.price}`;
                    tickerListHTML += `<li><a href="tickers/${ticker.symbol}.html">${ticker.symbol}: ${displayPrice}</a></li>`;
                });
                tickerListHTML += '</ul>';
                tickersContainer.innerHTML = tickerListHTML;
            })
            .catch(error => console.error('Error fetching tickers:', error));
    </script>
</body>
</html>
"""

    # Write HTML content to index.html
    with open("nasdaq_display/index.html", "w") as f:
        f.write(html_content)

    # Update individual ticker HTML files
    update_ticker_files("nasdaq_display/tickers", "Stocks_Scanner/nasdaq100_tickers.txt")

if __name__ == "__main__":
    update_index_html()
