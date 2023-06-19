import asyncio
from typing import Generator

from hrflow import Hrflow
from playwright.async_api import Browser, async_playwright
from playwright_stealth import stealth_async

from src.constants import SEARCH_QUERY_WHERE_SELECTOR
from src.data_models import RawJob
from src.indexing import index_job
from src.navigation import feed_pagination, visit_job_page
from src.parsing import extract_details, extract_initial_info
from src.utils import env_settings


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
    def __init__(self, browser: Browser, proxy_info: dict = None) -> None:
        self.proxy = proxy_info
        self.browser = browser
        self.page = None

    async def __aenter__(self):
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",  # noqa
        )
        self.page = await self.context.new_page()
        await stealth_async(self.page)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.context.close()

    async def feed_jobs_generator(
        self, search_query_what: str, search_query_where: str
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


class JobIndexing:
    def __init__(
        self,
        search_location: str,
        search_query: str = None,
        conccurent_scraper_count: int = 1,
        is_headless: bool = False,
        data_buffer_size: int = -1,
    ):
        self.query = search_query
        self.location = search_location
        self.conccurency_lvl = conccurent_scraper_count
        self.job_queue: asyncio.Queue = asyncio.Queue(maxsize=data_buffer_size)
        self.headless = is_headless
        self.playwright_engine = None
        self.browser = None

    async def __aenter__(self):
        self.playwright_engine = await async_playwright().start()
        self.browser = await self.playwright_engine.chromium.launch(headless=self.headless)
        self.hrflow_client = Hrflow(
            api_secret=env_settings.API_KEY, api_user=env_settings.USER_EMAIL
        )

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser:
            await self.browser.close()

        if self.playwright_engine:
            await self.playwright_engine.stop()

    async def job_producer(self):
        worker: ScrapingWorker
        async with ScrapingWorker(browser=self.browser) as worker:
            async for job in worker.feed_jobs_generator(
                search_query_what=self.query, search_query_where=self.location
            ):
                await self.job_queue.put(job)

    async def job_consumer(self):
        worker: ScrapingWorker
        async with ScrapingWorker(browser=self.browser) as worker:
            while True:
                initial_job = await self.job_queue.get()
                full_job = await worker.job_details_collector(job=initial_job)
                if full_job:
                    await asyncio.to_thread(
                        index_job, client=self.hrflow_client, extracted_job=full_job
                    )
                self.job_queue.task_done()

    async def run(self):
        producer_task = asyncio.create_task(self.job_producer())
        consumer_tasks = [
            asyncio.create_task(self.job_consumer()) for _ in range(self.conccurency_lvl)
        ]

        await producer_task
        await self.job_queue.join()
        for consumer in consumer_tasks:
            consumer.cancel()
