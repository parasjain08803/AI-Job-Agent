from loaders.resume_loader import load_resume
from chains.resume_chain import resume_chain
import time

def split_text(text, chunk_size=3000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def safe_invoke(chain, input_data, retries=3):
    for i in range(retries):
        try:
            return chain.invoke(input_data)
        except Exception as e:
            print(f"Retry {i+1} failed:", e)
            time.sleep(2 ** i)
    return {"skills": [], "projects": []}


def process_resume(file_bytes):
    documents = load_resume(file_bytes)


    if isinstance(documents, list):
        text = " ".join([doc.page_content for doc in documents])
    else:
        text = str(documents)

    chunks = split_text(text)

    all_skills = set()
    all_projects = []

    for chunk in chunks:
        result = safe_invoke(resume_chain, {"context": chunk})

        all_skills.update(result.get("skills", []))
        all_projects.extend(result.get("projects", []))

        time.sleep(1)  

    return {
        "skills": list(all_skills),
        "projects": all_projects
    }