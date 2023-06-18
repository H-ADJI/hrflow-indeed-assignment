import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from src.constants import INDEED_BASE_URL
from src.utils import nested_get


@dataclass
class RawJob:
    """
    The format / model of the job when scraped from indeed.
    """

    in_platform_id: str
    title: str
    url: str
    description: str = None
    company_name: Optional[str] = None
    company_rating: Optional[str] = None
    company_rating_count: Optional[str] = None
    company_location: Optional[str] = None
    company_description: Optional[str] = None
    company_logo: Optional[str] = None
    company_indeed_profile: Optional[str] = None
    company_review_page: Optional[str] = None
    location: Optional[str] = None
    raw_salary: Optional[str] = None
    salary_details: Optional[dict] = None
    date_posted: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    job_type: Optional[list[str]] = None
    job_benefits: Optional[list[str]] = None
    shift: Optional[str] = None

    @property
    def work_mode(self) -> list[str]:
        return self.location

    @property
    def full_url(self) -> str:
        return INDEED_BASE_URL + self.url.encode().decode()

    def update_data(self, job_details: dict = None, job_metadata: dict = None):
        if job_details:
            if raw_description := job_details.get("description"):
                self.description = re.sub("<[^>]*>", "", raw_description)
            if location := nested_get(job_details, query="jobLocation.address.addressLocality"):
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
                if company_rating_count := nested_get(company_data, query="ratingsModel.count"):
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
