import json
import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import transform_ugly
from Crawler import Crawler, get_credentials

import sys

cache = {}


def get_data(username, password):
    if username in cache and time.time() - cache[username][0] < 12 * 60 * 60:
        return cache[username][1]
    else:
        options = Options()
        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

        with Crawler(driver) as crawler:
            crawler.login(username, password)
            time.sleep(0.5)
            schedule = crawler.get_schedule()
            _json = transform_ugly.transform(schedule)
            cache[username] = (time.time(), _json)
            return _json


class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # o = parse.urlparse(self.path)
        # params = parse.parse_qs(o.query)
        # print(params)
        print("Request")
        # self.send_response(202)

        # username = params["username"][0]
        # password = params["password"][0]
        username, password = get_credentials()

        _json = get_data(username, password)
        if _json:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(_json).encode("utf-8"))
        else:
            self.send_response(500)



if __name__ == '__main__':
    server = HTTPServer((sys.argv[1].replace("any", ""), int(sys.argv[2])), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
