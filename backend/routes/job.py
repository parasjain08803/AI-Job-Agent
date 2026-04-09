from fastapi import APIRouter
from services.match_service import get_matching_jobs

router = APIRouter(prefix="/jobs")

@router.post("/match")
def match_jobs_api(resume_data: dict):
    results = get_matching_jobs(resume_data)
    return {"matches": results}





