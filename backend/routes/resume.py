from fastapi import APIRouter, UploadFile, File
from backend.services.resume_service import process_resume

router = APIRouter(prefix="/resume")

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    result = process_resume(content)
    return {"data": result}