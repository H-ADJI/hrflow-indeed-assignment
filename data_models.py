from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    pass


@dataclass
class Section:
    pass


@dataclass
class Skill:
    pass


@dataclass
class DateRange:
    pass


@dataclass
class FloatRange:
    pass


@dataclass
class Tag:
    pass


@dataclass
class RawJob:
    """
    The format / model of the job when scraped from indeed.
    """

    # number of hires
    # salary
    # job description

    # //script[contains(text(), 'window._initialData')] select json that contains alot of stuff
    # //script[@type="application/ld+json"] json that contains job main data

    in_platform_id: str  # regex from url or others ...
    title: str  # .//table//td[@class='resultContent']//a[@id]/span/@title from job feed
    url: str  # .//table//td[@class='resultContent']//a[@id]/@href from job feed
    company: Optional[Company] = None
    location: Optional[str] = None
    salary: Optional[Salary] = None
    job_type: Optional[
        list
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Job type']] from job feed (use getall for parsing)
    shift: Optional[
        list
    ] = None  # //div[@class='metadata']/div[svg[@aria-label='Shift']]  from feed OR //div[contains(preceding-sibling::*,'Shift')]//text() from job page

    def platform_id(self):
        return self.url


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
    skills: list[Skill] = None
    ranges_float: list[FloatRange]
    ranges_date: list[DateRange]
    tags: list[Tag]
