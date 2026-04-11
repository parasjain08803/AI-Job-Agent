from fastapi import APIRouter
from services.analys_single_job import analyze_single_job


router = APIRouter(prefix="/jobs")

@router.post("/analyze")
async def analyze_job(data: dict):
    resume_data = data.get("resume")
    job = data.get("job")

    result = await analyze_single_job(resume_data, job)

    return result