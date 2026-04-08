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

    for attempt in range(3): 
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.get(BASE_URL, headers=headers, params=params)

            print("STATUS:", res.status_code)

            if res.status_code != 200:
                raise Exception(res.text)

            data = res.json()
            jobs = data.get("data", [])

            return [normalize_job(job) for job in jobs]

        except Exception as e:
            print(f"Retry {attempt+1} failed:", str(e))

    return []