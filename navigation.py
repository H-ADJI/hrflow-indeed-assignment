from loguru import logger
from playwright.async_api import TimeoutError as NavigationTimeout
from playwright.sync_api import Page

# //a[@aria-label='Next Page'] next page button
# //button[@data-testid="pagination-page-current"] current page number


def paginate(page: Page):
    # TODO: handle popups when paginating
    page.wait_for_load_state()
    page.evaluate("window.scrollTo(0,document.body.scrollHeight);")
    next_button = page.locator("//a[@aria-label='Next Page']")
    while True:
        try:
            next_button.wait_for(state="visible", timeout=3000)
        except NavigationTimeout:
            logger.warning("Next button no longer available")
            break
        page.wait_for_timeout(2000)
        current_page = page.locator(
            "//button[@data-testid='pagination-page-current']"
        ).text_content()
        yield current_page
        next_button.click()
