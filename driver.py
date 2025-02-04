
import os
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# PROXY_HOST = os.getenv('PROXY_HOST')
# PROXY_PORT = os.getenv('PROXY_PORT')
# PROXY_USER = os.getenv('PROXY_USER')
# PROXY_PASS = os.getenv('PROXY_PASS')
# CHANGE_IP_LINK = os.getenv('CHANGE_IP_LINK')


# def get_driver(use_proxy=False):
    
#     options = Options()
#     # options.add_argument("--headless") 
#     options.add_argument("--disable-gpu")  
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage") 


#     driver = webdriver.Chrome(service=Service(), options=options)

#     return driver



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