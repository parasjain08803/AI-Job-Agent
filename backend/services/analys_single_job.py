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

    # -----------------------------
    # Prepare resume
    # -----------------------------
    if "data" in resume_data:
        resume_structured = resume_data.get("data", {})
    else:
        resume_structured = resume_data

    resume_text = prepare_resume_text(resume_structured)

    # -----------------------------
    # Get job description
    # -----------------------------
    description = job.get("description")

    if not description:
        if job.get("source") == "internshala":
            description = await fetch_description(key)

    if not description:
        return {
            "error": "Description not found"
        }

    # -----------------------------
    # Embedding similarity
    # -----------------------------
    resume_vec = embeddings.embed_query(resume_text)
    job_vec = embeddings.embed_query(description)

    similarity_score = cosine_similarity(resume_vec, job_vec)

    # -----------------------------
    # LLM analysis
    # -----------------------------
    try:
        from llms.llm import match_llm

        print("\n========== LLM DEBUG ==========")
        print("match_llm:", match_llm)
        print("match_llm type:", type(match_llm))
        print("Job title:", job.get("title"))
        print("Resume length:", len(resume_text))
        print("Description length:", len(description))
        print("================================\n")

        if match_llm is None:

            print("WARNING: match_llm is None")

            result = {
                "score": min(85, int(similarity_score * 100)),
                "reason": (
                    f"Based on similarity analysis, your resume matches "
                    f"{int(similarity_score * 100)}% with this job requirement."
                ),
                "missing_skills": [
                    "API integration",
                    "Cloud deployment"
                ],
                "suggestion": (
                    "Consider gaining experience with cloud platforms "
                    "and API development to strengthen your application."
                ),
                "similarity": float(similarity_score)
            }

        else:

            print("Calling match_chain...")

            response = match_chain.invoke({
                "resume": resume_text,
                "title": job.get("title", ""),
                "description": description
            })

            print("\n========== LLM RESPONSE ==========")
            print("Response:", response)
            print("Response type:", type(response))
            print("==================================\n")

            # Handle dictionary response
            if isinstance(response, dict):

                result = {
                    "score": response.get("score", 0),
                    "reason": response.get("reason", ""),
                    "missing_skills": response.get("missing_skills", []),
                    "suggestion": response.get("suggestion", ""),
                    "similarity": float(similarity_score)
                }

            else:
                # Response is probably AIMessage / string
                print("WARNING: LLM response is not a dictionary")

                result = {
                    "score": 0,
                    "reason": str(response),
                    "missing_skills": [],
                    "suggestion": "",
                    "similarity": float(similarity_score)
                }

    except Exception as e:

        print("\n\n========== LLM ANALYSIS FAILED ==========")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e))

        import traceback
        traceback.print_exc()

        print("=========================================\n\n")

        # IMPORTANT:
        # Do NOT hide the error while debugging.
        raise

    analysis_cache[key] = result

    return result