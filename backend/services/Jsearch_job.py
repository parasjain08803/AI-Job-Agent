# backend/services/jsearch.py

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

BASE_URL = "https://jsearch.p.rapidapi.com/search"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}


def normalize_job(job):
    return {
        "title": job.get("job_title"),
        "company": job.get("employer_name"),
        "location": job.get("job_city"),
        "description": job.get("job_description"),
        "url": job.get("job_apply_link"),
        "source": "jsearch"
    }


async def fetch_jsearch(query, location="india", page=1):
    params = {
        "query": f"{query} in {location}",
        "page": page,
        "num_pages": 1
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(BASE_URL, headers=headers, params=params)
        data = res.json()

    jobs = data.get("data", [])

    return [normalize_job(job) for job in jobs]