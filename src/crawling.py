import asyncio
from typing import Generator

from playwright.async_api import Browser
from playwright_stealth import stealth_async

from src.constants import SEARCH_QUERY_WHERE_SELECTOR
from src.data_models import RawJob
from src.indexing import index_job
from src.navigation import feed_pagination, visit_job_page
from src.parsing import extract_details, extract_initial_info


class AioObject(object):

    """Inheriting this class allows you to define an async __init__.

    So you can create objects by doing something like `await MyClass(params)`
    """

    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass


class ScrapingWorker:
    def __init__(self, proxy_info: dict = None) -> None:
        self.proxy = proxy_info
        self.page = None

    async def __aenter__(
        self,
        browser: Browser,
    ):
        context = await browser.new_context()
        self.page = await context.new_page()
        await stealth_async(self.page)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.context.close()

    async def feed_jobs_generator(
        self, search_query_what: str = None, search_query_where: str = "united kingdom"
    ) -> Generator[RawJob, None, None]:
        # using normal navigation to have a liget referer
        await self.page.goto("https://uk.indeed.com/", referer="https://google.com")
        location_input = self.page.locator(SEARCH_QUERY_WHERE_SELECTOR)
        await location_input.fill(search_query_where)
        await location_input.press(key="Enter")

        async for page_content in feed_pagination(page=self.page):
            for job in extract_initial_info(indeed_feed_page=page_content):
                yield job

    async def job_details_collector(self, job: RawJob) -> RawJob | None:
        if job_page_content := await visit_job_page(page=self.page, job=job):
            job_details, job_metadata = extract_details(page_content=job_page_content)
            job.update_data(job_details=job_details, job_metadata=job_metadata)
            return job
        return None


class IndeedScraper(AioObject):
    async def __init__(
        self,
        browser: Browser,
        conccurent_scraper: int = 1,
        data_buffer_size: int = -1,
    ):
        self.conccurency_lvl = conccurent_scraper
        self.job_queue: asyncio.Queue = await asyncio.Queue(maxsize=data_buffer_size)
        self.browser = browser

    async def job_producer(
        self, search_query_what: str = None, search_query_where: str = "united kingdom"
    ):
        worker: ScrapingWorker
        async with ScrapingWorker(browser=self.browser) as worker:
            async for job in worker.feed_jobs_generator(
                search_query_what=search_query_what, search_query_where=search_query_where
            ):
                self.job_queue.put(job)

    async def job_consumer(self):
        worker: ScrapingWorker
        async with ScrapingWorker(browser=self.browser) as worker:
            while True:
                initial_job = await self.job_queue.get()
                full_job = await worker.job_details_collector(job=initial_job)
                if full_job:
                    index_job()
