from hrflow import Hrflow
from playwright.async_api import Browser, async_playwright,Playwright
from playwright_stealth import stealth_async
import asyncio
from src.indexing import index_job
from src.navigation import feed_pagination, visit_job_page
from src.parsing import extract_details, extract_initial_info
from src.utils import env_settings

hrflow_client = Hrflow(api_secret=env_settings.API_KEY, api_user=env_settings.USER_EMAIL)


async def main():
    p: Playwright
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",  # noqa
        )
        page = await context.new_page()
        details_page = await context.new_page()
        await stealth_async(page=page)
        await stealth_async(page=details_page)
        await page.goto("https://uk.indeed.com/")
        location_input = page.locator("//input[@id='text-input-where']")
        await location_input.fill("united kingdom")
        await location_input.press(key="Enter")
        try:
            async for page_content in feed_pagination(page=page):
                for job_info in extract_initial_info(indeed_feed_page=page_content):
                    if job_page_content := await visit_job_page(page=details_page, job=job_info):
                        job_details, job_metadata = extract_details(page_content=job_page_content)
                        job_info.update_data(job_details=job_details, job_metadata=job_metadata)
                        index_job(client=hrflow_client, extracted_job=job_info)

        finally:
            await details_page.screenshot(path="./assets/bugetails.jpg")
            await page.screenshot(path="./assets/bugfeed.jpg")
            await page.pause()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main=main())