from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1280,800')
# Uncomment the next line to run headless
# chrome_options.add_argument('--headless')

# You may need to specify the path to chromedriver if it's not in your PATH
# service = Service('/path/to/chromedriver')
# driver = webdriver.Chrome(service=service, options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.google.com/maps')
time.sleep(5)  # Wait for the page to load
print(driver.title)
driver.quit() 