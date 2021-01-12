import time

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
# options.add_argument("-headless")
driver = webdriver.Firefox(options=options)
driver.set_window_size(800, 600 + 74)
driver.get("http://localhost:3000")
time.sleep(2)
driver.save_screenshot("test.png")