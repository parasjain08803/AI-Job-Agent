from fastapi import APIRouter, UploadFile, File
from loaders.resume_loader import load_resume
from services.resume_service import process_resume
from chains.ats_chain import ats_chain
from langchain_core.output_parsers import StrOutputParser
import re

router = APIRouter(prefix="/resume")

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    
    file_bytes = await file.read()

    documents = load_resume(file_bytes)

    if not documents:
        return {"error": "Empty document"}

    resume_text = " ".join(document.page_content for document in documents)

    def fix_text(text):
        text = text.lower()

    # FIX: "p r o j e c t s" → "projects"
        text = re.sub(r'(\b[a-z])\s+(?=[a-z]\b)', r'\1', text)

    # FIX: multiple spaces
        text = re.sub(r'\s+', ' ', text)

        return text
    
    fixed_resume_text=fix_text(resume_text)

    keywords = [
        "skills", "technical skills",
        "projects", "project",
        "experience", "work experience",
        "education", "summary",
        "professional summary"
    ]

    if any(keyword in fixed_resume_text for keyword in keywords):
        result="resume"
    else:
        result="not_resume"
        

    if result == "not_resume":
        return {
            "is_resume": False,
            "message": "This is not a resume. Please upload a valid resume."
        }

    final_output=process_resume(documents)

    if not final_output.get("skills",[]):
        return {
            "is_resume": False,
            "message": "This is not a resume. Please upload a valid resume."
        }
    

    ats_result = ats_chain.invoke({
    "resume_text": resume_text,
    "skills": final_output.get("skills", []),
    "projects": final_output.get("projects", []),
    "experience": final_output.get("experience", [])
})

    return {
        "is_resume": True,
        "data": final_output,
        "ats":ats_result
    }


