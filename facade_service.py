from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

import logging

import uuid
import requests
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

HOST = "127.0.0.1"

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        logging_response = requests.get("http://127.0.0.1:8082/")
        messaging_response = requests.get("http://127.0.0.1:8083/")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"{logging_response.text} : {messaging_response.text}".encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        
        fields = parse_qs(post_data.decode('utf-8'))


        url = "http://127.0.0.1:8082"
        data = {str(uuid.uuid4()): msg[0] for  msg in fields.values()}
        r = requests.post(url = url, data = data)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))



if __name__ == "__main__":
    from sys import argv

    port = 8080
    if len(argv) == 2:
        port=int(argv[1])
    
    server = HTTPServer((HOST, port), S)
    server.serve_forever()
    server.serve_close()