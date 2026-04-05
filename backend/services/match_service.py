from chains.match_chain import match_chain
from chains.query_chain import query_chain
from llms.prompts import match_prompt,query_prompt
from services.job_service import fetch_jobs
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import numpy as np

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def prepare_resume_text(data):
    skills = data.get("skills", [])
    projects = data.get("projects", [])

    skill_text = " ".join(skills)

    project_text_list = []
    for p in projects:
        desc = p.get("description", "")

        if isinstance(desc, list):
            desc = " ".join(desc)   
        elif not isinstance(desc, str):
            desc = ""

        project_text_list.append(desc)

    project_text = " ".join(project_text_list)

    return f"Skills: {skill_text}\nProjects: {project_text}"


def _derive_query_from_resume_llm(resume_structured: dict) -> str:
    result = query_chain.invoke({"resume_json": resume_structured})
    if not isinstance(result, dict):
        raise ValueError("LLM did not return a JSON object")

    query = result.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Missing/invalid query from LLM")

    return query.strip()



def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def match_jobs(resume_text, jobs):

    resume_vec = embeddings.embed_query(resume_text)

    scored_jobs = []

    for job in jobs:
        job_vec = embeddings.embed_query(job["description"])
        score = cosine_similarity(resume_vec, job_vec)
        scored_jobs.append((job, score))

    top_jobs = sorted(scored_jobs, key=lambda x: x[1], reverse=True)[:10]

    results = []

    for job, _ in top_jobs:
        response = match_chain.invoke({
            "resume": resume_text,
            "title": job["title"],
            "description": job["description"]
        })

        results.append({
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "description": job["description"],
            "url": job["url"],
            "score": response.get("score", 0),
            "reason": response.get("reason", ""),
            "missing_skills": response.get("missing_skills", []),
            "suggestion": response.get("suggestion", "")
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results


def get_matching_jobs(resume_data):

    if "data" in resume_data:
        resume_structured = resume_data.get("data",{})
    else:
        resume_structured = resume_data
    resume_text = prepare_resume_text(resume_structured)

    query = None
    if isinstance(resume_data, dict):
        query = resume_data.get("query") or resume_data.get("job_query")

    query = query.strip() if isinstance(query, str) else ""
    if not query:
        query = _derive_query_from_resume_llm(resume_structured)

    jobs = fetch_jobs(query=query, location="India")

    matches = match_jobs(resume_text, jobs)

    return matches