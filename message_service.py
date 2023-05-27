import json

from typing import List

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import logging
from kafka import KafkaConsumer
import threading

from urllib.parse import parse_qs

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
MSGS = []

def msg_loop():
    msg_consumer = KafkaConsumer( "msg-topic",
                                 group_id='my-group0',
                                 bootstrap_servers="localhost:9092",
                                 auto_offset_reset='earliest',
                                 api_version=(0,11,5)
                                 )
    for msg in msg_consumer:
        m = msg.value.decode()
        print(f"Message service: Incoming message: {m}")
        MSGS.append(m)


t = threading.Thread(target=msg_loop)
t.start()



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
        self.wfile.write(f"Messages: {'; '.join(MSGS)}".encode("utf-8"))

    def do_POST(self):
        
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("Not implemented yet.".encode('utf-8'))



if __name__ == "__main__":
    from sys import argv

    # port = 8083
    # if len(argv) == 2:
    #     port=int(argv[1])

    if len(argv) != 2:
        raise ValueError("Second argument should be index of the host and port to be used for logging service instance")
    index=int(argv[1])
    with open("config.json", mode="r") as f:
        conf = json.load(f)

    try:
        host, port = conf["message"][index].split("/")[-1].split(":")
    except IndexError:
        print("Provided wrong index")

    server = HTTPServer((host, int(port)), S)
    server.serve_forever()
    server.serve_close()