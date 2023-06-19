
from hrflow import Hrflow
from playwright.sync_api import Browser, sync_playwright
from playwright_stealth import stealth_sync

from src.indexing import index_job
from src.navigation import feed_pagination, visit_job_page
from src.parsing import extract_details, extract_initial_info
from src.utils import env_settings
hrflow_client = Hrflow(api_secret=env_settings.API_KEY, api_user=env_settings.USER_EMAIL)

with sync_playwright() as p:
    browser: Browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",  # noqa
    )
    page = context.new_page()
    details_page = context.new_page()
    stealth_sync(page=page)
    stealth_sync(page=details_page)
    page.goto("https://uk.indeed.com/")
    location_input = page.locator("//input[@id='text-input-where']")
    location_input.fill("united kingdom")
    location_input.press(key="Enter")
    data = []
    try:
        for page_content in feed_pagination(page=page):
            for job_info in extract_initial_info(indeed_feed_page=page_content):
                if job_page_content := visit_job_page(page=details_page, job=job_info):
                    job_details, job_metadata = extract_details(page_content=job_page_content)
                    job_info.update_data(job_details=job_details, job_metadata=job_metadata)
                    index_job(client=hrflow_client, extracted_job=job_info)

    finally:

        details_page.screenshot(path="./assets/bugetails.jpg")
        page.screenshot(path="./assets/bugfeed.jpg")
        page.pause()
    browser.close()
