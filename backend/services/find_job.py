from services.query_service import generate_query_llm,generate_query_manually
from services.job_service import fetch_jobs_async
from dotenv import load_dotenv
import numpy as np

load_dotenv()


async def find_jobs(resume_data):

    if "data" in resume_data:
        resume_structured = resume_data.get("data",{})
    else:
        resume_structured = resume_data

    location = resume_data.get("location", "India")
    job_type = resume_data.get("jobtype")
    remote = resume_data.get("remote", False)

    query = resume_data.get("query", "").strip()

    if not query:
        query = generate_query_manually(resume_structured)
        if query == "can not find":
            query = generate_query_llm(resume_structured)

    jobs = await fetch_jobs_async(query=query, location=location, job_type=job_type, remote=remote)

    return jobs