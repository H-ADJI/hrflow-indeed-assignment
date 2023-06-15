# //div[@class='icl-Autocomplete-ariaResultsAvailableWrapper']/span list for locations list
# //input[@id='text-input-where'] input to click for locations
# //ul[@class='icl-Autocomplete-list ']/li//b
from loguru import logger
from playwright.sync_api import Browser, sync_playwright
from playwright_stealth import stealth_sync

from navigation import paginate

with sync_playwright() as p:
    browser: Browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"  # noqa
    )
    page = context.new_page()
    stealth_sync(page=page)
    page.goto("https://uk.indeed.com/")
    location_input = page.locator("//input[@id='text-input-where']")
    location_input.fill("Davidstow, Cornwall")
    location_input.press(key="Enter")
    for page_number in paginate(page=page):
        logger.debug(page_number)
        page.wait_for_timeout(500)
    browser.close()
