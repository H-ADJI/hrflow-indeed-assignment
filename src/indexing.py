from dataclasses import asdict

from hrflow import Hrflow

from src.data_models import HrflowJob, RawJob
from src.utils import env_settings

hrflow_client = Hrflow(api_secret=env_settings.API_KEY, api_user=env_settings.USER_EMAIL)


def index_job(client: Hrflow, raw_job: RawJob) -> None:
    job_already_indexed = client.job.indexing.get(
        board_key=env_settings.BOARD_KEY, reference=raw_job.in_platform_id
    ).get("data")

    if not job_already_indexed:
        job: HrflowJob = raw_job.api_format(client=client)
        client.job.indexing.add_json(board_key=env_settings.BOARD_KEY, job_json=asdict(job))
