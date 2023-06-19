import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from hrflow import Hrflow
from loguru import logger

from src.constants import INDEED_BASE_URL
from src.utils import nested_get


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
    value_min: datetime = None
    value_max: datetime = None


@dataclass
class FloatRange:
    name: str
    value_min: float = None
    value_max: float = None
    unit: str = None


@dataclass
class Tag:
    name: str
    value: str


@dataclass
class Language:
    name: str
    value: str


@dataclass
class Task:
    name: str
    value: str


@dataclass
class Certification:
    name: str
    value: str


@dataclass
class Course:
    name: str
    value: str


@dataclass
class Metadata:
    name: str
    value: str


@dataclass
class HrflowJob:
    """
    The Hrflow job model, this is the format used to index jobs into hrflow
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
    tasks: list[Task] = None
    languages: list[Language] = None
    certifications: list[Certification] = None
    courses: list[Course] = None
    ranges_float: list[FloatRange] = None
    ranges_date: list[DateRange] = None
    metadata: list[Metadata] = None

    @staticmethod
    def __parse_skills(parsed_data: dict) -> list[Skill] | None:
        pass

    @staticmethod
    def __parse_tasks(parsed_data: dict) -> list[Task] | None:
        pass

    @staticmethod
    def __parse_languages(parsed_data: dict) -> list[Language] | None:
        pass

    @staticmethod
    def __parse_certifications(parsed_data: dict) -> list[Certification] | None:
        pass

    @staticmethod
    def __parse_courses(parsed_data: dict) -> list[Course] | None:
        pass

    def add_hrflowAI_generated_field(self, job_text: str, client: Hrflow):
        response_data: dict = client.document.parsing.post(text=job_text)
        if data := nested_get(dictionary=response_data, query="data.parsing"):
            self.tasks = self.__parse_tasks(parsed_data=data)
            self.skills = self.__parse_skills(parsed_data=data)
            self.courses = self.__parse_courses(parsed_data=data)
            self.languages = self.__parse_languages(parsed_data=data)
            self.certifications = self.__parse_certifications(parsed_data=data)
            return
        logger.warning("Could not parse job text")


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
    job_location: Optional[str] = None
    raw_salary: Optional[str] = None
    salary_details: Optional[dict] = None
    date_posted: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    job_type: Optional[list[str]] = None
    job_benefits: Optional[list[str]] = None
    shift: Optional[str] = None

    @property
    def clean_description(self) -> str | None:
        if self.description:
            return re.sub(
                r"\n\s*\n",
                "\n\n",
                self.description.strip(),
            )

    @property
    def full_description(self) -> str | None:
        if clean_description := self.clean_description:
            return self.title + "\n" + clean_description

    @property
    def work_modes(self) -> list[str]:
        work_modes = []
        if job_location := self.job_location:
            if "remote" in job_location.lower():
                work_modes.append("remote")

        if company_location := self.company_location:
            if "remote" in company_location.lower():
                work_modes.append("remote")

            if "hybrid" in company_location.lower():
                work_modes.append("hybrid")

        return work_modes

    @property
    def location(self) -> str:
        from_company_location = None
        from_job_location = None
        compiled_regex = re.compile(r"((remote|hybrid)(\sin)?)")

        if job_loc := self.job_location:
            from_job_location = compiled_regex.sub("", job_loc.lower()).strip()

        if company_loc := self.company_location:
            from_company_location = compiled_regex.sub("", company_loc.lower()).strip()

        return from_company_location or from_job_location or None

    @property
    def full_url(self) -> str:
        return INDEED_BASE_URL + self.url.encode().decode()

    def update_data(self, job_details: dict = None, job_metadata: dict = None):
        if job_details:
            if raw_description := job_details.get("description"):
                self.description = re.sub("<[^>]*>", "", raw_description)
            if location := nested_get(job_details, query="jobLocation.address.addressLocality"):
                self.job_location = location
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

    def __location_adapter(self) -> Location:
        return Location(text=self.location)

    def __tags_adapter(self) -> list[Tag]:
        tags = []
        for benefit in self.job_benefits or []:
            tags.append[Tag(name="job benefit", value=benefit)]
        for job_type in self.job_type:
            tags.append(Tag(name="job type", value=job_type))
        for work_mode in self.work_modes:
            tags.append(Tag(name="work mode", value=work_mode))
        if shift := self.shift:
            tags.append(Tag(name="shift", value=shift))
        if salary := self.raw_salary:
            tags.append(Tag(name="raw salary", value=salary))
        return tags or None

    def __section_adapter(self) -> list[Section]:
        return [
            Section(
                name="description", title="job description text", description=self.clean_description
            )
        ]

    def __float_ranges_adapter(self) -> list[FloatRange]:
        ranges = []
        if salary_details := self.salary_details:
            salary_max = salary_details.get("maxValue")
            salary_min = salary_details.get("minValue")
            timeframe = salary_details.get("unitText")
            currency = salary_details.get("currency")
            if salary_min and salary_max and currency and timeframe:
                ranges.append(
                    FloatRange(
                        name="salary",
                        value_max=salary_max,
                        value_min=salary_min,
                        unit=f"{currency}/{timeframe}",
                    )
                )
        return ranges or None

    def __date_ranges_adapter(self) -> list[DateRange]:
        return [
            DateRange(name="job validity", value_min=self.date_posted, value_max=self.valid_until)
        ]

    def __metadata_adapter(self) -> list[Metadata]:
        metadatas = []
        if company_name := self.company_name:
            metadatas.append(Metadata(name="company name", value=company_name))

        if company_rating := self.company_rating:
            metadatas.append(Metadata(name="company rating", value=company_rating))

        if company_description := self.company_description:
            metadatas.append(Metadata(name="company description", value=company_description))

        if company_indeed_profile := self.company_indeed_profile:
            metadatas.append(Metadata(name="company indeed profile", value=company_indeed_profile))

        if company_rating_count := self.company_rating_count:
            metadatas.append(Metadata(name="company rating count", value=company_rating_count))

        if company_review_page := self.company_review_page:
            metadatas.append(Metadata(name="company review page", value=company_review_page))

        if company_logo := self.company_logo:
            metadatas.append(Metadata(name="company logo", value=company_logo))

        return metadatas or None

    def api_format(self, client: Hrflow) -> HrflowJob:
        hrflow_job = HrflowJob(
            reference=self.in_platform_id,
            name=self.title,
            location=self.__location_adapter(),
            sections=self.__section_adapter(),
            url=self.full_url,
            created_at=self.date_posted,
            tags=self.__tags_adapter(),
            ranges_float=self.__float_ranges_adapter(),
            ranges_date=self.__date_ranges_adapter(),
            metadata=self.__metadata_adapter(),
        )
        # include NLP/AI generated fields
        # hrflow_job.add_hrflowAI_generated_field(job_text=self.full_description, client=client)

        return hrflow_job
