"""
╔═══════════════════════════════════════════════════════════╗
║  web/server.py — MUserBot Pro Live Web Showcase Server    ║
║  Serves modern interactive dashboard & stats on 0.0.0.0    ║
╚═══════════════════════════════════════════════════════════╝
"""

import http.server
import socketserver
import os
import sys

PORT = int(os.getenv("PORT", "8000"))
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS and iframe embedding for preview
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"🌐 MUserBot Pro Web Dashboard running on http://0.0.0.0:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")

if __name__ == "__main__":
    run_server()
