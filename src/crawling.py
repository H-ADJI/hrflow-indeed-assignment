import asyncio
import random
from typing import Generator

from hrflow import Hrflow
from loguru import logger
from playwright.async_api import Browser, async_playwright
from playwright_stealth import stealth_async

from src.constants import UK_CITIES
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


class ScrapingWorker(AioObject):
    async def __init__(
        self, browser: Browser, proxy_info: dict = None, _purpose: str = "scraping"
    ) -> None:
        self.proxy = proxy_info
        self.browser = browser
        self.page = None
        self.purpose = _purpose
        self.id = None
        self.id = random.randint(20, 9999)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",  # noqa
        )
        self.page = await self.context.new_page()
        await stealth_async(self.page)
        logger.debug(f"Launched {self.purpose} witj id : {self.id}")

    async def stop(self):
        logger.debug("Exiting the Worker")
        logger.debug(f"worker for {self.purpose} - {self.id}")
        await self.context.close()

    async def feed_jobs_generator(
        self,
        search_query_what: str,
    ) -> Generator[RawJob, None, None]:
        # using normal navigation to have a liget referer
        for city in UK_CITIES[::-1]:
            await self.page.goto(
                f"https://uk.indeed.com/jobs?q=&l={city}", referer="https://google.com"
            )
            logger.info(f" City ===> {city}")
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
        search_query: str = None,
        conccurent_scraper_count: int = 1,
        is_headless: bool = False,
        data_buffer_size: int = -1,
    ):
        self.query = search_query
        self.conccurency_lvl = conccurent_scraper_count
        self.job_queue: asyncio.Queue = asyncio.Queue(maxsize=data_buffer_size)
        self.headless = is_headless
        self.playwright_engine = None
        self.browser = None
        self.worker_pool: list[ScrapingWorker] = []
        self.tasks: list[asyncio.Task] = []

    async def __aenter__(self):
        self.playwright_engine = await async_playwright().start()
        self.browser = await self.playwright_engine.chromium.launch(headless=self.headless)
        self.hrflow_client = Hrflow(
            api_secret=env_settings.API_KEY, api_user=env_settings.USER_EMAIL
        )

        return self

    async def __aexit__(self, exc_type, exc, tb):
        logger.debug("cancelling the tasks")
        for task in self.tasks:
            if not task.cancelled():
                task.cancel()
        logger.debug("closing the workers contexts")
        for worker in self.worker_pool:
            await worker.stop()
        logger.debug("Exiting the Indexer")
        if self.browser:
            logger.debug("Closing browser")
            await self.browser.close()

        if self.playwright_engine:
            logger.debug("Closing playwright")
            logger.debug(self.job_queue.qsize())
            await self.playwright_engine.stop()

    async def job_producer(self):
        worker = await ScrapingWorker(browser=self.browser, _purpose="Feed Scraping")
        self.worker_pool.append(worker)

        async for job in worker.feed_jobs_generator(search_query_what=self.query):
            await self.job_queue.put(job)

    async def job_consumer(self):
        worker = await ScrapingWorker(browser=self.browser, _purpose="Job Details Scraping")
        self.worker_pool.append(worker)

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

        self.tasks.append(producer_task)
        self.tasks.extend(consumer_tasks)

        await producer_task
        logger.info("Done Producing jobs from feed")
        await self.job_queue.join()
        for consumer in consumer_tasks:
            consumer.cancel()
