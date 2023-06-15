from loguru import logger
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.sync_api import Locator, Page


# //a[@aria-label='Next Page'] next page button
# //button[@data-testid="pagination-page-current"] current page number
# //button[@aria-label='close'] close the popup to subscribe to newsletter
# //div[@class='jobsearch-LeftPane'] job container
# //div[@class='jobsearch-LeftPane']/div[@id='mosaic-jobResults']/div/ul/li job cards + garbage elements
# //div[@data-testid='viewJob-skeleton'] pane when job data is loading NO USE
# //div[@id='jobsearch-ViewjobPaneWrapper']  pane containing job details NO USE
def go_next_page(page: Page, tries: int = 2) -> bool:
    next_button = page.locator("//a[@aria-label='Next Page']")
    # scrolling to "next page button"
    try:
        next_button.scroll_into_view_if_needed(timeout=100_000)
    except NavigationTimeout:
        logger.warning("Next button no longer available")
        return False
    # log page number
    logger.debug(
        page.locator("//button[@data-testid='pagination-page-current']").text_content()
    )

    annoying_popup: Locator = page.locator("//button[@aria-label='close']")
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


def paginate(page: Page):
    while True:
        jobs = page.locator("//div[@class='jobsearch-LeftPane']")
        jobs.wait_for(state="visible")
        yield page.content()
        if not go_next_page(page=page):
            break
