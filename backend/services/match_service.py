from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from backend.services.job_service import fetch_jobs
from dotenv import load_dotenv

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_template("""
You are an expert AI recruiter.

Evaluate how well this resume matches the job.

Resume:
{resume}

Job Title: {title}
Job Description: {description}

Return JSON:
{{
  "score": number (0-100),
  "reason": "short explanation",
  "missing_skills": ["list of important missing skills"],
  "suggestion": "how candidate can improve for this role"                                        
                                          
}}
""")

chain = prompt | llm | parser


def prepare_resume_text(data):
    skills = data.get("skills", [])
    projects = data.get("projects", [])

    skill_text = " ".join(skills)

    project_text = " ".join(
        [p.get("description", "") for p in projects]
    )

    return skill_text + " " + project_text


def create_job_vectorstore(jobs):
    texts = [job["description"] for job in jobs]
    metadatas = jobs

    return FAISS.from_texts(texts, embeddings, metadatas=metadatas)


def match_jobs(resume_text, vectorstore):

    # Step 1: FAISS shortlist
    docs = vectorstore.similarity_search(resume_text, k=10)

    results = []

    # Step 2: LLM via LCEL
    for doc in docs:
        job = doc.metadata

        response = chain.invoke({
            "resume": resume_text,
            "title": job["title"],
            "description": job["description"]
        })

        results.append({
            "title": job["title"],
            "company":job["company"],
            "location":job["location"],
            "description": job["description"],
            "url":job["url"],
            "score": response.get("score", 0),
            "reason": response.get("reason", ""),
            "missing_skills":response.get("missing_skills",[]),
            "suggestion":response.get("suggestion","")
        })


    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results


def get_matching_jobs(resume_data):

    resume_text = prepare_resume_text(resume_data.get("data", {}))

    jobs = fetch_jobs(query="AI Engineer")

    vectorstore = create_job_vectorstore(jobs)

    matches = match_jobs(resume_text, vectorstore)

    return matches