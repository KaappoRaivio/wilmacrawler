import json
import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import transform_ugly
from Crawler import Crawler, get_credentials

# import urlparse

cache = {}

def get_data(username, password):
    if username in cache and time.time() - cache[username][0] < 12 * 60 * 60:
        return cache[username]
    else:
        options = Options()
        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

        with Crawler(driver) as crawler:
            crawler.login(username, password)
            time.sleep(0.5)
            s = crawler.get_schedule()
            _json = transform_ugly.transform(s.details, s)
            cache[username] = (time.time(), _json)
            return _json


class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # o = parse.urlparse(self.path)
        # params = parse.parse_qs(o.query)
        # print(params)
        self.send_response(202)

        # username = params["username"][0]
        # password = params["password"][0]
        username, password = get_credentials()

        _json = get_data(username, password)
        if _json:
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(_json).encode("utf-8"))
            self.send_response(200)
        else:
            self.send_response(500)






import sys


if __name__ == '__main__':
    server = HTTPServer(('localhost', int(sys.argv[1])), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
