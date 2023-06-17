from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


@dataclass
class Company:
    name: str  # //span[@class='companyName'] from job feed
    location: str  # //div[@class='companyLocation'] from job feed
    rating: float  # //span[@class='ratingNumber']/span/text() from job feed


@dataclass
class Salary:
    raw_form: Optional[
        str
    ] = None  # //div[@class='metadata salary-snippet-container']//text() this is from the job feed
    salary_details: Optional[dict] = None


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
class RawJob:
    """
    The format / model of the job when scraped from indeed.
    """

    # //script[contains(text(), 'window._initialData')] select json that contains alot of stuff
    # //script[@type="application/ld+json"] json that contains job main data
    in_platform_id: str  # //table//td[@class='resultContent']//a[@id]/@data-jk from feed
    title: str  # .//table//td[@class='resultContent']//a[@id]/span/@title from job feed
    url: str  # .//table//td[@class='resultContent']//a[@id]/@href from job feed
    location_query_param: str = None
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
    job_type: Optional[
        list[str]
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Job type']] from job feed (use getall for parsing)
    job_benefits: Optional[list[str]] = None
    shift: Optional[
        list[str]
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Shift']]  from feed OR //div[contains(preceding-sibling::*,'Shift')]//text() from job page

    @property
    def work_mode(self) -> list[str]:
        return self.location

    @property
    def full_url(self) -> str:
        return "https://uk.indeed.com" + self.url.encode().decode()


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
