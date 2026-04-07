from chains.query_chain import query_chain
def generate_query_manually(data):
    skills = [s.lower() for s in data.get("skills", [])]
    projects = " ".join([p.get("description", "").lower() for p in data.get("projects", [])])

    text = " ".join(skills) + " " + projects

    
    roles = {
        "machine learning engineer": [
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "nlp", "computer vision", "rag", "llm", "ai"
        ],
        "data scientist": [
            "data analysis", "pandas", "numpy", "statistics",
            "data visualization", "matplotlib", "seaborn"
        ],
        "backend developer": [
            "fastapi", "django", "flask", "node", "express",
            "api", "sql", "database", "backend"
        ],
        "frontend developer": [
            "react", "javascript", "html", "css", "frontend",
            "nextjs", "ui", "ux"
        ],
        "full stack developer": [
            "full stack", "mern", "mean", "react", "node", "mongodb"
        ],
        "devops engineer": [
            "docker", "kubernetes", "aws", "ci/cd", "devops"
        ],
        "software engineer": [
            "java", "c++", "python", "dsa", "algorithms"
        ]
    }

    
    role_scores = {}
    for role, keywords in roles.items():
        score = sum(1 for k in keywords if k in text)
        role_scores[role] = score

    
    best_role = max(role_scores, key=role_scores.get)

    
    if role_scores[best_role] == 0:
        return "can not find"

    return best_role

def generate_query_llm(resume_structured: dict) -> str:
    result = query_chain.invoke({"resume_json": resume_structured})
    if not isinstance(result, dict):
        raise ValueError("LLM did not return a JSON object")

    query = result.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Missing/invalid query from LLM")

    return query.strip()