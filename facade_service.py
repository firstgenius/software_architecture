from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import json
import random

import logging
from kafka import KafkaProducer

import uuid
import requests
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
with open("config.json", mode="r") as f:
    conf = json.load(f)
logging_urls = conf["logging"]
message_urls = conf["message"]
kafka_msg_producer = KafkaProducer(bootstrap_servers="localhost:9092", api_version=(0,11,5))

HOST = "127.0.0.1"

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        try:
            log_url = random.choice(logging_urls)
            logging_response = requests.get(log_url)
        except Exception as e:
            print(f"Logging service at address {log_url} could not be reached. Error: {e}")

        try:
            message_url = random.choice(message_urls)
            print(message_url)
            messaging_response = requests.get(message_url)
        except Exception as e:
            print(f"Message service at address {message_url} could not be reached. Error: {e}")

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


        url = random.choice(logging_urls)
        message = "".join([ msg[0] for  msg in fields.values()])
        data = {str(uuid.uuid4()): message}
        r = requests.post(url = url, data = data)

        kafka_msg_producer.send( "msg-topic", message.encode('utf-8'))
        kafka_msg_producer.flush()


        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))



if __name__ == "__main__":
    from sys import argv

    # port = 8080
    # if len(argv) == 2:
    #     port=int(argv[1])

    host, port = conf["facade"].split("/")[-1].split(":")
    
    server = HTTPServer((host, int(port)), S)
    server.serve_forever()
    server.serve_close()