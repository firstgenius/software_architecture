import json

from typing import List

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import logging
from kafka import KafkaConsumer
from consul import Consul
import threading

from urllib.parse import parse_qs

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
MSGS = []

def msg_loop():
    consul = Consul()
    key = "kafka-msg-config"
    default_config = {
    "topic": "msg-topic",
    "url": "localhost:9092",
    }

    _, value = consul.kv.get(key)

    if value is None:
        print(f"Config is None. Putting default config value {default_config}.")
        consul.kv.put(key, json.dumps(default_config))
        config = json.dumps(default_config)
    else:
        config = json.loads(value["Value"].decode("ascii"))
        print(f"Obtained config {config}")

    msg_consumer = KafkaConsumer(config["topic"],
                                 group_id='my-group0',
                                 bootstrap_servers=config["url"],
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

    if len(argv) != 4:
        raise ValueError("Second arg: host, third: port, fourth: index")
    host, port, index = argv[1], argv[2], int(argv[3])

    url = f"http://{host}:{port}"

    consul = Consul()
    _, urls = consul.kv.get("MESSAGES")
    curr_url = {f"MESSAGES_{index}": url}
    if urls is None:
        messages_json = json.dumps(curr_url)
    else:
        urls_dict = json.loads(urls['Value'].decode('ascii'))
        urls_dict.update(curr_url)
        messages_json = json.dumps(urls_dict)
    print(f"Updating urls for messages in consul: {messages_json})")
    consul.kv.put("MESSAGES", messages_json)


    server = HTTPServer((host, int(port)), S)
    server.serve_forever()
    server.serve_close()