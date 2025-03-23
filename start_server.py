import http.server
import socketserver
import os
import sys
import webbrowser
from datetime import datetime

# Default port
PORT = 8000

class NasdaqHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the NASDAQ display application."""
    
    def end_headers(self):
        """Add CORS headers to allow requests from any origin."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Override to add timestamp to log messages."""
        sys.stderr.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} - {format % args}\n")

def start_server(directory=None, port=PORT):
    """
    Start the HTTP server for the NASDAQ display application.
    
    Args:
        directory (str, optional): Directory to serve files from. Defaults to current directory.
        port (int, optional): Port to run the server on. Defaults to 8000.
    """
    # Change to the specified directory if provided
    if directory:
        if not os.path.exists(directory):
            print(f"Error: Directory '{directory}' does not exist.")
            return
        os.chdir(directory)
        print(f"Serving files from: {os.path.abspath(directory)}")
    
    # Try to start the server, handling port conflicts
    try:
        Handler = NasdaqHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Server started at http://localhost:{port}")
            print("Press Ctrl+C to stop the server")
            
            # Open the browser automatically
            webbrowser.open(f"http://localhost:{port}")
            
            # Start the server
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98 or e.errno == 10048:  # Port already in use
            print(f"Error: Port {port} is already in use.")
            new_port = port + 1
            print(f"Trying port {new_port}...")
            start_server(directory, new_port)
        else:
            print(f"Error starting server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    # Check if a directory was specified as a command-line argument
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # Default to the nasdaq_display directory
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../nasdaq_display")

    start_server(directory)
