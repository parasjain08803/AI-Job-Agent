import asyncio
from services.Adzuna_job import fetch_adzuna
from services.Jsearch_job import fetch_jsearch


async def fetch_jobs_async(
    query,
    location="india",
    experience=None,
    remote=False,
    min_salary=None
):
    tasks = []

    tasks.append(fetch_adzuna(query, location))

    tasks.append(fetch_jsearch(query, location, page=1))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_jobs = []

    for res in results:
        if isinstance(res, list):
            all_jobs.extend(res)
        else:
            print("Error in source:", res)  # debug

    return all_jobs


def fetch_jobs(
    query,
    location="india",
    experience=None,
    remote=False,
    min_salary=None
):
    return asyncio.run(
        fetch_jobs_async(query, location, experience, remote, min_salary)
    )