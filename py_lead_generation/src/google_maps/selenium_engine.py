from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from py_lead_generation.src.misc.writer import CsvWriter

class GoogleMapsSeleniumEngine:
    FIELD_NAMES = ['Title', 'Address', 'PhoneNumber', 'WebsiteURL']
    FILENAME = 'google_maps_leads.csv'

    def __init__(self, query: str, location: str, headless: bool = False):
        self.query = query
        self.location = location
        self._entries = []
        self.headless = headless

    def run(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280,800')
        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get('https://www.google.com/maps')
            time.sleep(3)
            # Accept cookies if prompted
            try:
                consent_btn = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Accept all")]')
                consent_btn.click()
                time.sleep(1)
            except Exception:
                pass
            # Search for query and location
            search_box = driver.find_element(By.ID, 'searchboxinput')
            search_box.clear()
            search_box.send_keys(f'{self.query} {self.location}')
            search_box.send_keys(Keys.ENTER)
            time.sleep(5)
            # Collect all business URLs first
            links = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
            urls = [link.get_attribute('href') for link in links]
            wait = WebDriverWait(driver, 10)
            for url in urls[:5]:  # Limit to 5 for demo/speed
                driver.get(url)
                time.sleep(3)
                # Extract details from the panel
                try:
                    name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob'))).text
                except Exception:
                    name = ''
                try:
                    website_btn = driver.find_element(By.XPATH, '//a[contains(@aria-label, "Website")]')
                    website = website_btn.get_attribute('href')
                except Exception:
                    website = ''
                # Address extraction using data-item-id
                try:
                    address_btn = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "address")]')
                    address = address_btn.text.strip()
                except Exception:
                    address = ''
                # Phone extraction using data-item-id
                try:
                    phone_btn = driver.find_element(By.XPATH, '//button[starts-with(@data-item-id, "phone:")]')
                    phone = phone_btn.text.strip()
                except Exception:
                    phone = ''
                entry = {
                    'Title': name,
                    'Address': address,
                    'PhoneNumber': phone,
                    'WebsiteURL': website
                }
                self._entries.append(entry)
                time.sleep(1)
            print(f'[INFO] Scraped {len(self._entries)} detailed results.')
        finally:
            driver.quit()

    def save_to_csv(self, filename: str = None):
        if filename:
            self.FILENAME = filename
        if not self.FILENAME.endswith('.csv'):
            raise ValueError('Use .csv file extension')
        if not self._entries:
            raise NotImplementedError('Entries are empty, call .run() method first to save them')
        csv_writer = CsvWriter(self.FILENAME, self.FIELD_NAMES)
        csv_writer.append(self._entries)

    @property
    def entries(self):
        if not self._entries:
            raise NotImplementedError('Entries are empty, call .run() method first to create them')
        return self._entries 