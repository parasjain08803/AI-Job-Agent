import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

def fetch_jobs(query="AI Engineer", location="India"):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": 10
    }

    response = requests.get(url, params=params)
    data = response.json()

    jobs = []

    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title"),
            "description": job.get("description"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "url":job.get("redirect_url")
        })

    return jobs