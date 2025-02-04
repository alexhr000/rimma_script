
import os
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options()
    options.binary_location = "/usr/bin/chromium-browser"  # Путь к Chromium
    options.add_argument("--headless")  # Запуск без GUI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    proxy = "gw.dataimpulse.com:823"

    options.add_argument(f"--proxy-server={proxy}")
    service = Service("/usr/bin/chromedriver")  # Путь к ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    return driver