import httpx
import os

BASE_URL = "https://jsearch.p.rapidapi.com/search"


def normalize_job(job):
    return {
        "title": job.get("job_title"),
        "company": job.get("employer_name"),
        "location": job.get("job_city"),
        "description": job.get("job_description"),
        "url": job.get("job_apply_link"),
        "salary": job.get("job_min_salary"),
        "source": "jsearch"
    }


async def fetch_jsearch(query, location="india", experience=None, remote=False, page=1):
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }


    exp = (experience or "").lower()


    search_query = f"{query} in {location}"

    if exp == "fresher":
        search_query += " fresher"
    elif exp == "intern":
        search_query += " intern"
    elif exp == "junior":
        search_query += " junior"
    elif exp == "senior":
        search_query += " senior"

    if remote:
        search_query += " remote"

    params = {
        "query": search_query,
        "page": page,
        "num_pages": 1
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(BASE_URL, headers=headers, params=params)

        if res.status_code != 200:
            print("JSearch Error:", res.text)
            return []

        data = res.json()
        jobs = data.get("data", [])

        return [normalize_job(job) for job in jobs]

    except Exception as e:
        print("JSearch Exception:", str(e))
        return []