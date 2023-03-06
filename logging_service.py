import json

from typing import List

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import logging

from urllib.parse import parse_qs

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

HOST = "127.0.0.1"
MSG_HASH_MAP = {}

class S(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if MSG_HASH_MAP:
            self.wfile.write("; ".join(MSG_HASH_MAP.values()).encode("utf-8"))
        else:
            self.wfile.write("")


    def do_POST(self):
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
    
        fields = parse_qs(post_data.decode('utf-8'))

        for key, msg in fields.items():
            MSG_HASH_MAP[key] = msg[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))



if __name__ == "__main__":
    from sys import argv

    port = 8082
    if len(argv) == 2:
        port=int(argv[1])
    
    server = HTTPServer((HOST, port), S)
    server.serve_forever()
    server.serve_close()