import asyncio
import random
from playwright.async_api import Playwright, async_playwright, TimeoutError as PlaywrightTimeout, Browser, Page

from py_lead_generation.src.misc.writer import CsvWriter
from py_lead_generation.src.engines.playwright_config import PlaywrightEngineConfig


class BaseEngine(PlaywrightEngineConfig):
    '''
    `BaseEngine`

    Base engine class expressing methods, which are shared between all engines, does not provide implementation of `AbstractEngine` methods
    '''

    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(self):
        self._entries = []
        self.browser = None
        self.page = None
        self.context = None

    async def run(self) -> None:
        '''
        Uses headless webdriver powered by Playwright

        Creates a web url based on initialized parameters

        Parses results by given query and url one by one

        Assigns collected results to `.entries`

        To save the results call `.save_to_csv()` method after       
        '''
        try:
            async with async_playwright() as playwright:
                self.playwright = playwright
                await self._setup_browser()
                
                try:
                    await asyncio.sleep(1)
                    await self._open_url_and_wait(self.url)
                    urls: list[str] = await self._get_search_results_urls()
                    # Only process the first 2 URLs for debugging
                    urls = urls[:2]
                    self._entries = await self._get_search_results_entries(urls)
                except Exception as e:
                    print(f"Error during execution: {str(e)}")
                    raise
                finally:
                    await self._cleanup_browser()
        except Exception as e:
            print(f"Fatal error: {str(e)}")
            raise

    def save_to_csv(self, filename: str = None) -> None:
        '''
        `filename: str = None` - optional parameter, by default uses `self.FILENAME`
        
        If file with such name already exists, it will not overwrite it but append newly found entries to existing ones

        If file with such name does not exist, it will create a new csv file with predetermined fieldnames
        '''
        if filename:
            self.FILENAME = filename

        if not self.FILENAME.endswith('.csv'):
            raise ValueError('Use .csv file extension')
        if not self._entries:
            raise NotImplementedError(
                'Entries are empty, call .run() method first to save them'
            )
        csv_writer = CsvWriter(self.FILENAME, self.FIELD_NAMES)
        csv_writer.append(self._entries)

    @property
    def entries(self) -> list[dict]:
        '''
        Returns `list[dict]` typed entries once `.run()` method was called
        '''
        if not self._entries:
            raise NotImplementedError(
                'Entries are empty, call .run() method first to create them'
            )
        return self._entries

    @entries.setter
    def entries(self, _) -> None:
        '''
        You cannot do that ;)

        Made for durability reasons
        '''
        raise ValueError('Cannot set value to data. This is not allowed')

    async def _setup_browser(self) -> None:
        '''
        Sets up the browser by initializing `playwright.chromium` and `Browser` along with `Page` after
        '''
        for attempt in range(self.MAX_RETRIES):
            try:
                chromium = self.playwright.chromium
                self.browser = await chromium.launch(**self.BROWSER_PARAMS)
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                return
            except Exception as e:
                print(f"Error setting up browser: {str(e)}")
                if self.page:
                    await self.page.close()
                if self.context:
                    await self.context.close()
                if self.browser:
                    await self.browser.close()
                if attempt == self.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(self.RETRY_DELAY)

    async def _cleanup_browser(self) -> None:
        '''
        Clean up browser resources in the correct order
        '''
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None

    async def _open_url_and_wait(self, url: str, sleep_duration_s: float = 3.0) -> None:
        '''
        Opens a URL with retries and proper error handling
        '''
        for attempt in range(self.MAX_RETRIES):
            try:
                if not self.page:
                    raise Exception("Browser page not initialized")
                
                # Add random delay before navigation
                await asyncio.sleep(random.uniform(1, 2))
                
                # Navigate with a longer timeout and wait for network idle
                await self.page.goto(url, timeout=60000, wait_until='networkidle')
                
                # Add random delay after navigation
                await asyncio.sleep(random.uniform(sleep_duration_s, sleep_duration_s + 2))
                return
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(self.RETRY_DELAY)

    async def _get_search_results_entries(self, urls: list[str]) -> list[dict]:
        '''
        Process URLs and extract data with proper error handling
        '''
        entries = []
        for url in urls:
            try:
                if not self.page:
                    await self._setup_browser()
                
                await self._open_url_and_wait(url, 1.5)
                
                # Add random delay before extracting content
                await asyncio.sleep(random.uniform(1, 2))
                
                html = await self.page.content()
                data = self._parse_data_with_soup(html)
                entry = dict(zip(self.FIELD_NAMES, data))
                entries.append(entry)
                
                # Add random delay after processing each URL
                await asyncio.sleep(random.uniform(2, 3))
                
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
                continue

        return entries
