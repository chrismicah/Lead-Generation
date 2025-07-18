from playwright.async_api import async_playwright
import asyncio

async def try_browser(browser_type, name):
    print(f'\n[TEST] Trying {name}...')
    try:
        browser = await browser_type.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://www.google.com/maps', timeout=60000)
        print(f'[SUCCESS] {name} loaded Google Maps. Title:', await page.title())
        await browser.close()
        return True
    except Exception as e:
        print(f'[FAIL] {name} failed: {e}')
        return False

async def main():
    async with async_playwright() as p:
        if await try_browser(p.chromium, 'Chromium'):
            return
        if await try_browser(p.firefox, 'Firefox'):
            return
        if await try_browser(p.webkit, 'WebKit'):
            return
        print('[RESULT] All browsers failed to load Google Maps.')

asyncio.run(main()) 