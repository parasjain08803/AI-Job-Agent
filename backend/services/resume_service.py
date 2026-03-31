from backend.loaders.resume_loader import load_resume
from backend.chains.resume_chain import resume_chain

def process_resume(file_bytes):
    documents = load_resume(file_bytes)

    response = resume_chain.invoke({
        "context": documents
    })

    return response