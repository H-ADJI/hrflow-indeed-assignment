from loguru import logger
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.sync_api import Locator, Page

from src.constants import (
    CLOSE_POPUP_SELECTOR,
    CURRENT_PAGE_NUMBER_SELECTOR,
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
        page.wait_for_timeout(2_000)
        jobs = page.locator(JOBS_PANE_SELECTOR)
        jobs.wait_for(state="visible")
        yield page.content()
        if not go_next_page(page=page):
            break


def visit_job_page(page: Page, job: RawJob):
    logger.debug(f"visiting : {job.full_url}")
    page.goto(job.full_url)
    page.wait_for_timeout(500)
    return page.content()
