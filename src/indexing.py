from dataclasses import asdict

from hrflow import Hrflow
from loguru import logger

from src.data_models import HrflowJob, RawJob
from src.utils import env_settings


def index_job(client: Hrflow, extracted_job: RawJob) -> None:
    job_already_indexed = client.job.indexing.get(
        board_key=env_settings.BOARD_KEY, reference=extracted_job.in_platform_id
    ).get("data")

    if not job_already_indexed:
        logger.info(f"job {extracted_job.in_platform_id} indexing ")
        job: HrflowJob = extracted_job.api_format(client=client)
        client.job.indexing.add_json(board_key=env_settings.BOARD_KEY, job_json=asdict(job))
        return

    logger.info(
        f"job {extracted_job.in_platform_id} already indexed, url : {extracted_job.full_url}"
    )
