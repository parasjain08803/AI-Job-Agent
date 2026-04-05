from fastapi import APIRouter, UploadFile, File
from loaders.resume_loader import load_resume
from llms.prompts import classifier_prompt,parser_prompt
from llms.llm import classifier_llm,parser_llm
from services.resume_service import process_resume
from langchain_core.output_parsers import StrOutputParser

router = APIRouter(prefix="/resume")

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    
    file_bytes = await file.read()

    documents = load_resume(file_bytes)

    if not documents:
        return {"error": "Empty document"}

    first_page_text = documents[0].page_content

    classification_parser=StrOutputParser()

    classification_chain = classifier_prompt | classifier_llm | classification_parser
    classification = classification_chain.invoke({"text": first_page_text})

    result = classification.strip().lower()

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

    return {
        "is_resume": True,
        "data": final_output
    }


