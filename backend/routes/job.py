from fastapi import APIRouter
from services.find_job import find_jobs
from services.internshala_job_scrapping import get_browser

router = APIRouter(prefix="/jobs")

@router.post("/find")
async def match_jobs_api(resume_data: dict):
    await get_browser()
    results = await find_jobs(resume_data)
    return {"matches": results}





