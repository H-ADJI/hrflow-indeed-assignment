import re

import chompjs
from loguru import logger
from parsel import Selector, SelectorList

from src.constants import (
    COMPANY_LOCATION_SELECTOR,
    COMPANY_NAME_SELECTOR,
    COMPANY_RATING_SELECTOR,
    JOB_CARD_SELECTOR,
    JOB_DETAIL_JSON_SELECTOR,
    JOB_ID_SELECTOR,
    JOB_METADATA_JSON_SELECTOR,
    JOB_SALARY_SELECTOR,
    JOB_SHIFT_SELECTOR,
    JOB_TITLE_SELECTOR,
    JOB_TYPE_SELECTOR,
    JOB_URL_SELECTOR,
)
from src.data_models import RawJob


def extract_initial_info(indeed_feed_page: str):
    """extract all job data fields from indeed feed

    Args:
        indeed_feed_page (str): feed html content

    Yields:
        RawJob: RawJob data class with initial data
    """
    jobs_selector = Selector(indeed_feed_page)
    jobs_selector.remove_namespaces()
    jobs: SelectorList = jobs_selector.xpath(JOB_CARD_SELECTOR)
    for selected_job in jobs:
        job = RawJob(
            in_platform_id=selected_job.xpath(JOB_ID_SELECTOR).get(),
            url=selected_job.xpath(JOB_URL_SELECTOR).get(),
            title=selected_job.xpath(JOB_TITLE_SELECTOR).get(),
            raw_salary=selected_job.xpath(JOB_SALARY_SELECTOR).get(),
            company_name=selected_job.xpath(COMPANY_NAME_SELECTOR).get(),
            company_location=selected_job.xpath(COMPANY_LOCATION_SELECTOR).get(),
            company_rating=selected_job.xpath(COMPANY_RATING_SELECTOR).get(),
            shift=selected_job.xpath(JOB_SHIFT_SELECTOR).get(),
            job_type=selected_job.xpath(JOB_TYPE_SELECTOR).getall(),
        )
        yield job


def parse_data_object(raw_data: str) -> dict | None:
    """Parse JS objects

    Args:
        raw_data (str): Javascript code

    Returns:
        dict | None: Data parsed from JS code
    """
    if not raw_data:
        logger.warning("JS data object not available")
        return None
    try:
        return chompjs.parse_js_object(string=raw_data)
    except ValueError:
        logger.warning("This JS object could not be parsed")
        return None


def parse_metadata_object(raw_data: str) -> dict | None:
    """Parse JS objects

    Args:
        raw_data (str): Javascript code

    Returns:
        dict | None: Data parsed from JS code
    """
    if not raw_data:
        logger.warning("JS metadata object not available")
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
        return None


def extract_details(page_content: str) -> tuple[dict]:
    """Selects and parses JS code containing data from job page html content

    Args:
        page_content (str): job html content

    Returns:
        tuple[dict]: data and metadata dictionaries
    """
    job_data_selector = Selector(page_content)

    job_raw_data = job_data_selector.xpath(JOB_DETAIL_JSON_SELECTOR).get()
    job_raw_metadata = job_data_selector.xpath(JOB_METADATA_JSON_SELECTOR).get()
    return parse_data_object(job_raw_data), parse_metadata_object(job_raw_metadata)
