import re

import chompjs
from loguru import logger
from parsel import Selector, SelectorList

from data_models import RawJob


def extract_initial_info(indeed_feed_page: str):
    jobs_selector = Selector(indeed_feed_page)
    jobs_selector.remove_namespaces()
    jobs: SelectorList = jobs_selector.xpath(
        "//div[@class='jobsearch-LeftPane']/div[@id='mosaic-jobResults']/div/ul/li/div[@class[contains( . , 'cardOutline')]]"  # noqa
    )
    for selected_job in jobs:
        job = RawJob(
            in_platform_id=selected_job.xpath(
                ".//table//td[@class='resultContent']//a[@id]/@data-jk"
            ).get(),
            url=selected_job.xpath(
                ".//table//td[@class='resultContent']//a[@id]/@href"
            ).get(),
            title=selected_job.xpath(
                ".//table//td[@class='resultContent']//a[@id]/span/@title"
            ).get(),
            raw_salary=selected_job.xpath(
                ".//div[@class='metadata salary-snippet-container']//text()"
            ).get(),
            company_name=selected_job.xpath(
                ".//span[@class='companyName']/text()"
            ).get(),
            company_location=selected_job.xpath(
                ".//div[@class='companyLocation']/text()"
            ).get(),
            company_rating=selected_job.xpath(
                ".//span[@class='ratingNumber']/span/text()"
            ).get(),
            shift=selected_job.xpath(
                ".//div[@class='metadata']/div[svg[@aria-label='Shift']]/text()"
            ).getall(),
            job_type=selected_job.xpath(
                ".//div[@class='metadata']/div[svg[@aria-label='Job type']]/text()"
            ).getall(),
        )
        yield job


def parse_data_object(raw_data: str) -> dict | None:
    if not raw_data:
        return None
    try:
        return chompjs.parse_js_object(string=raw_data)
    except ValueError:
        logger.warning("this JS object could not be parsed")
        logger.warning(raw_data)
        return None


def parse_metadata_object(raw_data: str) -> dict | None:
    if not raw_data:
        return None
    try:
        match = re.search(r"(?<=_initialData=).*", raw_data)
        if match:
            raw_data_section = match.group()
            clean_raw_data = raw_data_section.rsplit(",", maxsplit=1)[0] + "}}"
            return chompjs.parse_js_object(string=clean_raw_data)
        return None

    except ValueError:
        logger.warning("this JS object could not be parsed")
        logger.warning(raw_data)
        return None


def extract_details(job_page_content: str) -> tuple[dict]:
    job_data_selector = Selector(job_page_content)

    job_raw_data = job_data_selector.xpath(
        "//script[@type='application/ld+json']/text()"
    ).get()
    job_raw_metadata = job_data_selector.xpath(
        "//script[contains(text(), 'window._initialData')]/text()"
    ).get()
    return parse_data_object(job_raw_data), parse_metadata_object(job_raw_metadata)
