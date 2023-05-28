import json
import hazelcast as hz

from typing import List

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import logging
from consul import Consul

from urllib.parse import parse_qs

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)



consul = Consul()
key = "logging-map-config"
default_config = {"map": "logging_map"}

_, value = consul.kv.get(key)

if value is None:
    print(f"Config is None. Putting default config value {default_config}.")
    consul.kv.put(key, json.dumps(default_config))
    config = json.dumps(default_config)
else:
    config = json.loads(value["Value"].decode("ascii"))
    print(f"Obtained config {config}")


hz_inst = hz.HazelcastClient()
MSG_HASH_MAP = hz_inst.get_map(config["map"])
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
        self.wfile.write("; ".join(list(MSG_HASH_MAP.values().result())).encode("utf-8"))


    def do_POST(self):
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
    
        key, msg = post_data.decode('utf-8').split("=")
        print(key, msg)
        MSG_HASH_MAP.put(key, msg)



        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))



if __name__ == "__main__":
    from sys import argv
    from random import choice

    if len(argv) != 4:
        raise ValueError("Second arg: host, third: port, fourth: index")
    host, port, index = argv[1], argv[2], int(argv[3])

    url = f"http://{host}:{port}"

    consul = Consul()
    _, urls = consul.kv.get("LOGGING")
    curr_url = {f"LOGGING_{index}": url}
    if urls is None:
        logging_json = json.dumps(curr_url)
    else:
        urls_dict = json.loads(urls['Value'].decode('ascii'))
        urls_dict.update(curr_url)
        logging_json = json.dumps(urls_dict)
    print(f"Updating urls for logging in consul: {logging_json})")
    consul.kv.put("LOGGING", logging_json)
    

    server = HTTPServer((host, int(port)), S)
    server.serve_forever()
    server.serve_close()