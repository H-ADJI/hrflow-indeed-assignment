from loguru import logger
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.sync_api import Locator, Page

from src.constants import (
    CLOSE_POPUP_SELECTOR,
    CURRENT_PAGE_NUMBER_SELECTOR,
    JOB_DETAIL_JSON_SELECTOR,
    JOB_METADATA_JSON_SELECTOR,
    JOBS_PANE_SELECTOR,
    NEXT_PAGE_BUTTON_SELECTOR,
)
from src.data_models import RawJob


def go_next_page(page: Page, tries: int = 2) -> bool:
    next_button = page.locator(NEXT_PAGE_BUTTON_SELECTOR)
    # scrolling to "next page button"
    try:
        next_button.scroll_into_view_if_needed(timeout=10_000)
    except NavigationTimeout:
        logger.warning("Next button no longer available")
        return False
    # log page number
    logger.debug(page.locator(CURRENT_PAGE_NUMBER_SELECTOR).text_content())

    annoying_popup: Locator = page.locator(CLOSE_POPUP_SELECTOR)
    # dealing with popup that blocks naviagation
    for i in range(tries):
        if annoying_popup.count() > 0:
            annoying_popup.click()
        try:
            next_button.click(timeout=5_000)
            return True
        except NavigationTimeout:
            logger.info(f"try number {i+1} failed out of {tries}")

    return False


def feed_pagination(page: Page):
    while True:
        page.wait_for_timeout(1_500)
        jobs = page.locator(JOBS_PANE_SELECTOR)
        jobs.wait_for(state="attached")
        yield page.content()
        if not go_next_page(page=page):
            break


def visit_job_page(
    page: Page,
    job: RawJob,
    try_number: int = 1,
    attempts: int = 3,
    cooldown: float = 5_000,
) -> str | None:
    logger.debug(f"visiting : {job.full_url}")
    page.goto(job.full_url)
    page.wait_for_timeout(500)
    try:
        page.locator(JOB_DETAIL_JSON_SELECTOR).wait_for(state="attached", timeout=2_000)
        page.locator(JOB_METADATA_JSON_SELECTOR).wait_for(state="attached", timeout=2_000)

    except NavigationTimeout:
        if "Just a moment" in page.title():
            logger.warning("Clouflare detection triggered")
            if try_number <= attempts:
                logger.warning(
                    f"Going to retry for the {try_number+1} attempt after a short cooldown"
                )
                page.wait_for_timeout(cooldown * try_number)
                return visit_job_page(page=page, job=job, try_number=try_number + 1)
            logger.warning("Could not bypass Clouflare detection ")
            return None
        else:
            logger.warning("Some issue occured when extracting data objects from job page")

    return page.content()
