from dataclasses import dataclass
from typing import Optional

from loguru import logger
from parsel import Selector, SelectorList


# //div[@class='jobsearch-LeftPane']/div[@id='mosaic-jobResults']/div/ul/li/div[@class[contains( . , 'cardOutline')]] select only job cards
#  .//table//td[@class='resultContent']//a[@id]/@href job link
@dataclass
class Job:
    url: str  # .//table//td[@class='resultContent']//a[@id]/@href
    title: str  # .//table//td[@class='resultContent']//a[@id]/span/@title
    company_name: Optional[str] = None  # //span[@class='companyName']
    location: Optional[str] = None  # //div[@class='companyLocation']
    salary: Optional[
        str
    ] = None  # //div[@class='metadata salary-snippet-container']//text()
    job_type: Optional[
        str
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Job type']]
    shift: Optional[
        str
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Shift']]

    def platform_id(self):
        return self.url

def extract_initial_info(jobs_page: str):
    jobs_selector = Selector(jobs_page)
    jobs_selector.remove_namespaces()
    jobs: SelectorList = jobs_selector.xpath(
        "//div[@class='jobsearch-LeftPane']/div[@id='mosaic-jobResults']/div/ul/li/div[@class[contains( . , 'cardOutline')]]"
    )
    logger.debug(len(jobs))
    for selected_job in jobs:
        job = Job(
            url=selected_job.xpath(
                ".//table//td[@class='resultContent']//a[@id]/@href"
            ).get(),
            title=selected_job.xpath(
                ".//table//td[@class='resultContent']//a[@id]/span/@title"
            ).get(),
            job_type=selected_job.xpath(
                ".//div[@class='metadata']/div[svg[@aria-label='Job type']]/text()"
            ).get()
        )
        logger.info(job)
