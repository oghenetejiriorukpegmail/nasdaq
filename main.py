#!/usr/bin/env python3
"""
NASDAQ Display - Main Script

This script provides a command-line interface to run various functions
of the NASDAQ Display application.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def run_command(command, description):
    """Run a Python module as a subprocess with proper error handling."""
    print_header(description)
    try:
        result = subprocess.run([sys.executable, command], 
                               capture_output=True, 
                               text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("ERRORS:")
            print(result.stderr)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            return True
        else:
            print(f"✗ {description} failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"✗ Error running {command}: {e}")
        return False

def update_data():
    """Update all NASDAQ data files."""
    print_header("Starting NASDAQ data update")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create directories if they don't exist
    os.makedirs("nasdaq_display/tickers", exist_ok=True)
    
    # Step 1: Get NASDAQ tickers
    if not run_command("Stocks_Scanner/nasdaq_tickers.py", "Fetching NASDAQ tickers"):
        return False
    
    # Step 2: Update ticker HTML files
    if not run_command("Stocks_Scanner/update_ticker_files.py", "Updating ticker HTML files"):
        return False
    
    # Step 3: Update tickers.json
    if not run_command("Stocks_Scanner/update_tickers_json.py", "Updating tickers.json"):
        return False
    
    # Step 4: Update index.html
    if not run_command("Stocks_Scanner/scan.py", "Updating index.html"):
        return False
    
    print_header("NASDAQ data update completed")
    return True

def start_server():
    """Start the HTTP server."""
    print_header("Starting HTTP server")
    try:
        # Use subprocess.Popen to run in the background
        process = subprocess.Popen([sys.executable, "Stocks_Scanner/start_server.py"])
        print(f"Server started (PID: {process.pid})")
        print("Server is running in the background. Press Ctrl+C in the terminal to stop.")
        return True
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def main():
    """Main function to parse arguments and run commands."""
    parser = argparse.ArgumentParser(description="NASDAQ Display Application")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update NASDAQ data")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the HTTP server")
    
    # Run command (update + server)
    run_parser = subparsers.add_parser("run", help="Update data and start server")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "update":
        update_data()
    elif args.command == "server":
        start_server()
    elif args.command == "run":
        if update_data():
            start_server()
    else:
        # If no command is provided, show help
        parser.print_help()

if __name__ == "__main__":
    main()