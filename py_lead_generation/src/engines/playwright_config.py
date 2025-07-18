from playwright.async_api import Browser, Page, BrowserType


class PlaywrightEngineConfig:
    '''
    Minimal Playwright config for debugging.
    '''
    BROWSER_PARAMS = {
        'headless': True,
    }
    PAGE_PARAMS = {}

    async def _setup_browser(self) -> None:
        print('[DEBUG] Starting minimal browser setup...')
        chromium: BrowserType = self.playwright.chromium
        print('[DEBUG] Launching browser...')
        self.browser: Browser = await chromium.launch(**self.BROWSER_PARAMS)
        print('[DEBUG] Creating new browser context...')
        self.context = await self.browser.new_context(**self.PAGE_PARAMS)
        print('[DEBUG] Creating new page...')
        self.page: Page = await self.context.new_page()
        print('[DEBUG] Minimal browser setup complete.')
