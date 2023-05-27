import json
import hazelcast as hz

from typing import List

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import logging

from urllib.parse import parse_qs

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)





hz_inst = hz.HazelcastClient()
MSG_HASH_MAP = hz_inst.get_map("logging_map")
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

    if len(argv) != 2:
        raise ValueError("Second argument should be index of the host and port to be used for logging service instance")
    index=int(argv[1])
    with open("config.json", mode="r") as f:
        conf = json.load(f)

    try:
        host, port = conf["logging"][index].split("/")[-1].split(":")
    except IndexError:
        print("Provided wrong index")
    

    server = HTTPServer((host, int(port)), S)
    server.serve_forever()
    server.serve_close()