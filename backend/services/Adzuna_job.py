import httpx
import os

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


def normalize_job(job):
    return {
        "title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "description": job.get("description"),
        "url": job.get("redirect_url"),
        "salary": job.get("salary_min"),
        "source": "adzuna"
    }


async def fetch_adzuna(query, location="india", job_type=None, remote=False):
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"


    search_query = query

    if job_type == "Fresher":
        search_query += " fresher"
    elif job_type == "Internship":
        search_query += " internship"
    elif job_type == "Senior":
        search_query += " senior"

    if remote:
        search_query += " remote"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": search_query,
        "where": location,
        "results_per_page": 20
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(url, params=params)

    if res.status_code != 200:
        print("Adzuna Error:", res.text)
        return []

    data = res.json()
    jobs = data.get("results", [])

    return [normalize_job(job) for job in jobs]