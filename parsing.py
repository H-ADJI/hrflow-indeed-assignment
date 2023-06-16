from parsel import Selector, SelectorList

from data_models import RawJob


def extract_initial_info(jobs_page: str):
    jobs_selector = Selector(jobs_page)
    jobs_selector.remove_namespaces()
    jobs: SelectorList = jobs_selector.xpath(
        "//div[@class='jobsearch-LeftPane']/div[@id='mosaic-jobResults']/div/ul/li/div[@class[contains( . , 'cardOutline')]]"  # noqa
    )
    for selected_job in jobs:
        job = RawJob(
            url=selected_job.xpath(
                ".//table//td[@class='resultContent']//a[@id]/@href"
            ).get(),
            title=selected_job.xpath(
                ".//table//td[@class='resultContent']//a[@id]/span/@title"
            ).get(),
            salary=selected_job.xpath(
                ".//div[@class='metadata']/div[svg[@aria-label='Job type']]/text()"
            ).get(),
        )
        yield job
