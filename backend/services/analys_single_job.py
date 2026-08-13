from chains.match_chain import match_chain
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import numpy as np
from services.internshala_job_scrapping import fetch_description

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



def cosine_similarity(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return np.dot(a, b) / denom

analysis_cache = {}


async def analyze_single_job(resume_data, job):

    key = job.get("url")

    if key in analysis_cache:
        return analysis_cache[key]

    if "data" in resume_data:
        resume_structured = resume_data.get("data", {})
    else:
        resume_structured = resume_data

    resume_text = prepare_resume_text(resume_structured)

    description=job.get("description")

    if not description:
        if job.get("source") == "internshala":
            description = await fetch_description(key)

    if not description:
        return {
            "error": "Description not found"
        }        
      

    # embeddings similarity
    resume_vec = embeddings.embed_query(resume_text)
    job_vec = embeddings.embed_query(description)

    similarity_score = cosine_similarity(resume_vec, job_vec)

    # LLM analysis
    try:
        from llms.llm import match_llm
        if match_llm is None:
            # Fallback mock analysis when LLM is not available
            result = {
                "score": min(85, int(similarity_score * 100)),
                "reason": f"Based on similarity analysis, your resume matches {int(similarity_score * 100)}% with this job requirement.",
                "missing_skills": ["API integration", "Cloud deployment"],  # Mock missing skills
                "suggestion": "Consider gaining experience with cloud platforms and API development to strengthen your application.",
                "similarity": float(similarity_score)
            }
        else:
            response = match_chain.invoke({
                "resume": resume_text,
                "title": job["title"],
                "description": description
            })

            result = {
                "score": response.get("score", 0),
                "reason": response.get("reason", ""),
                "missing_skills": response.get("missing_skills", []),
                "suggestion": response.get("suggestion", ""),
                "similarity": float(similarity_score)
            }
    except Exception as e:
        # Fallback if LLM analysis fails
        result = {
            "score": min(75, int(similarity_score * 100)),
            "reason": f"Analysis based on resume-job similarity ({int(similarity_score * 100)}%). LLM analysis unavailable.",
            "missing_skills": [],
            "suggestion": "Ensure your resume highlights relevant skills mentioned in the job description.",
            "similarity": float(similarity_score)
        }
    analysis_cache[key] = result
    return result