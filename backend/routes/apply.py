from fastapi import APIRouter
from backend.services.application_agent import generate_application

router = APIRouter(prefix="/apply")

@router.post("/")
def apply_job(data: dict):
    resume = data["resume"]
    job = data["job"]

    result = generate_application(resume, job)

    return result