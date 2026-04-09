import asyncio
from services.Adzuna_job import fetch_adzuna
from services.Jsearch_job import fetch_jsearch
from services.internshala_job_scrapping import fetch_internshala

async def fetch_jobs_async(
    query,
    location="india",
    job_type=None,
    remote=False,
):
    tasks = []

    tasks.append(fetch_adzuna(query, location , job_type,remote))

    tasks.append(fetch_jsearch(query, location, page=1,job_type=job_type,remote=remote))

    ##tasks.append(fetch_internshala(query,location,remote,pages=1,job_type=job_type))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_jobs = []

    for res in results:
        if isinstance(res, list):
            all_jobs.extend(res)
        else:
            print("Error in source:", repr(res))  # debug

    return all_jobs


def fetch_jobs(
    query,
    location="india",
    job_type=None,
    remote=False
):
    return asyncio.run(
        fetch_jobs_async(query, location, job_type, remote)
    )