#!/usr/bin/env python3
import csv
import json
import os
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

class WaitlistHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_POST(self):
        if self.path == '/submit':
            time.sleep(1.0) # retain a slight delay to trigger UI animations seamlessly
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Check if file exists to write headers
                csv_file = 'waitlist.csv'
                file_exists = os.path.isfile(csv_file)
                
                with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['name', 'email', 'budget', 'timestamp'])
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(data)
                
                print(f"[{data.get('timestamp')}] Saved new waitlist entry for {data.get('email', 'unknown')}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                
            except Exception as e:
                print(f"Error saving entry: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server_address = ('0.0.0.0', port)
    print(f"Starting Waitlist Server on http://localhost:{port}")
    print("All form submissions will be saved to waitlist.csv")
    httpd = HTTPServer(server_address, WaitlistHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
