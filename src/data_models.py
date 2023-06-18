import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from src.utils import nested_get


@dataclass
class RawJob:
    """
    The format / model of the job when scraped from indeed.
    """

    # //script[contains(text(), 'window._initialData')] select json that contains alot of stuff
    # //script[@type="application/ld+json"] json that contains job main data

    in_platform_id: str  # //table//td[@class='resultContent']//a[@id]/@data-jk from feed
    title: str  # .//table//td[@class='resultContent']//a[@id]/span/@title from job feed // job_data.title
    url: str  # .//table//td[@class='resultContent']//a[@id]/@href from job feed
    location_query_param: str = None  # user input
    description: str = None  # job_data.description + parse html
    company_name: Optional[
        str
    ] = None  # job_data.hiringOrganization OR  //span[@class='companyName'] from job feed
    company_rating: Optional[
        str
    ] = None  # //span[@class='ratingNumber']/span/text() from job feed
    company_rating_count: Optional[
        str
    ] = None  # metadata.companyAvatarModel.ratingsModel.count
    company_location: Optional[
        str
    ] = None  # //div[@class='companyLocation'] from job feed
    company_description: Optional[
        str
    ] = None  # metadata.companyAvatarModel.companyDescription
    company_logo: Optional[str] = None  # metadata.companyAvatarModel.companyLogoUrl
    company_indeed_profile: Optional[
        str
    ] = None  # metadata.companyAvatarModel.companyOverviewLink
    company_review_page: Optional[
        str
    ] = None  # metadata.companyAvatarModel.companyReviewLink
    location: Optional[str] = None  # job_data.jobLocation.address.addressLocality
    raw_salary: Optional[
        str
    ] = None  # //div[@class='metadata salary-snippet-container']//text() this is from the job feed
    salary_details: Optional[dict] = None  # job_data.baseSalary.currency + .value
    date_posted: Optional[datetime] = None  # job_data.datePosted
    valid_until: Optional[datetime] = None  # job_data.validThrough
    job_type: Optional[  # job_data.employmentType
        list[str]
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Job type']] from job feed (use getall for parsing)
    job_benefits: Optional[list[str]] = None  # metadata.benefitsModel.labels
    shift: Optional[
        str
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Shift']]  from feed OR //div[contains(preceding-sibling::*,'Shift')]//text() from job page

    @property
    def work_mode(self) -> list[str]:
        return self.location

    @property
    def full_url(self) -> str:
        return "https://uk.indeed.com" + self.url.encode().decode()

    def update_data(self, job_details: dict = None, job_metadata: dict = None):
        if job_details:
            if raw_description := job_details.get("description"):
                self.description = re.sub("<[^>]*>", "", raw_description)
            if location := nested_get(
                job_details, query="jobLocation.address.addressLocality"
            ):
                self.location = location
            salary_details: dict
            if salary_details := job_details.get("baseSalary"):
                details: dict = salary_details.get("value")
                details.pop("@type", None)
                self.salary_details = {
                    "currency": salary_details.get("currency"),
                    **details,
                }
            if date_posted := job_details.get("datePosted"):
                self.date_posted = date_posted
            if valid_until := job_details.get("validThrough"):
                self.valid_until = valid_until
            if job_type := job_details.get("employmentType"):
                self.job_type = job_type

        if job_metadata:
            company_data: dict
            if company_data := job_metadata.get("companyAvatarModel"):
                if company_rating_count := nested_get(
                    company_data, query="ratingsModel.count"
                ):
                    self.company_rating_count = company_rating_count

                if company_description := company_data.get("companyDescription"):
                    self.company_description = company_description

                if company_logo := company_data.get("companyLogoUrl"):
                    self.company_logo = company_logo

                if company_indeed_profile := company_data.get("companyOverviewLink"):
                    self.company_indeed_profile = company_indeed_profile

                if company_review_page := company_data.get("companyReviewLink"):
                    self.company_review_page = company_review_page

            if job_benefits := nested_get(job_metadata, query="benefitsModel.labels"):
                self.job_benefits = job_benefits


@dataclass
class Location:
    text: str
    lat: float = None
    lng: float = None


@dataclass
class Section:
    name: str
    title: str
    description: str


@dataclass
class Skill:
    name: str
    type: Literal["hard", "soft"]
    value: str = None


@dataclass
class DateRange:
    name: str
    value_min: datetime
    value_max: datetime


@dataclass
class FloatRange:
    name: str
    value_min: float
    value_max: float
    unit: str


@dataclass
class Tag:
    name: str
    value: str


@dataclass
class Metadata:
    name: str
    value: str


@dataclass
class HrflowJobWrite:
    """
    The Hrflow job model, this will be used to index jobs into hrflow
    """

    reference: str
    name: str
    location: Location
    sections: list[Section]
    url: str = None
    summary: str = None
    created_at: datetime = None
    tags: list[Tag] = None
    skills: list[Skill] = None
    ranges_float: list[FloatRange] = None
    ranges_date: list[DateRange] = None
    metadata: list[Metadata] = None
