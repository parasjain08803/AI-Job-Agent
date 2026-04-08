import httpx
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


def normalize_job(job):
    return {
        "title": job.get("title"),
        "company": job.get("company", {}).get("display_name"),
        "location": job.get("location", {}).get("display_name"),
        "description": job.get("description"),
        "url": job.get("redirect_url"),
        "source": "adzuna"
    }


async def fetch_adzuna(query, location="india", page=1):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": 20
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        data = res.json()

    jobs = data.get("results", [])

    return [normalize_job(job) for job in jobs]