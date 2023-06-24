import random

from loguru import logger
from playwright.async_api import Page
from playwright.async_api import TimeoutError as NavigationTimeout

from src.constants import (
    CURRENT_PAGE_NUMBER_SELECTOR,
    INDEED_FEED_URL,
    JOB_DETAIL_JSON_SELECTOR,
    JOB_METADATA_JSON_SELECTOR,
    JOBS_PANE_SELECTOR,
    NEXT_PAGE_BUTTON_SELECTOR,
    UK_CITIES,
)
from src.data_models import RawJob


async def go_next_page(page: Page, city: str, page_number: int) -> bool:
    next_button = page.locator(NEXT_PAGE_BUTTON_SELECTOR)
    try:
        await next_button.wait_for(state="attached")
    except NavigationTimeout:
        logger.warning("Next button no longer available")
        return False

    await page.goto(
        INDEED_FEED_URL.format(city=city, page_number=page_number), referer="https://google.com"
    )
    return True


async def feed_pagination(page: Page):
    # using normal navigation to have a legit referer
    while True:
        cities = UK_CITIES.copy()
        for _ in range(len(UK_CITIES)):
            city = random.sample(cities, 1)[0]
            await page.goto(f"https://uk.indeed.com/jobs?q=&l={city}", referer="https://google.com")
            logger.info(f" City ===> {city}")
            page_number = 10
            while True:
                logger.info(
                    f" Going to Page number : {await page.locator(CURRENT_PAGE_NUMBER_SELECTOR).text_content()}"
                )
                await page.wait_for_timeout(1_500)
                jobs = page.locator(JOBS_PANE_SELECTOR)
                await jobs.wait_for(state="attached")
                yield await page.content()
                if not await go_next_page(page=page, city=city, page_number=page_number):
                    break
                page_number += 10
            cities.remove(city)


async def visit_job_page(
    page: Page,
    job: RawJob,
    try_number: int = 1,
    attempts: int = 3,
    cooldown: float = 5_000,
) -> str | None:
    try:
        await page.goto(job.full_url)
        await page.wait_for_timeout(500)
        await page.locator(JOB_DETAIL_JSON_SELECTOR).wait_for(state="attached", timeout=2_000)
        await page.locator(JOB_METADATA_JSON_SELECTOR).wait_for(state="attached", timeout=2_000)

    except NavigationTimeout:
        if "Just a moment" in await page.title():
            logger.warning("Cloudflare detection triggered")
            if try_number <= attempts:
                logger.warning(
                    f"Going to retry for the {try_number+1} attempt after a short cooldown"
                )
                await page.wait_for_timeout(cooldown * try_number)
                return await visit_job_page(page=page, job=job, try_number=try_number + 1)
            logger.warning("Could not bypass Cloudflare detection ")
            return None
        else:
            logger.warning("Some issue occured when extracting data objects from job page")

    return await page.content()
