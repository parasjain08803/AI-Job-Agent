from langchain_core.prompts import ChatPromptTemplate

classifier_prompt = ChatPromptTemplate.from_template("""
You are a strict classifier.

Check if the following text is a RESUME.

A resume MUST contain at least one of:
- skills
- experience
- education
- projects

If it's a book, notes, random text → return "not_resume"

Return ONLY:
resume OR not_resume

Text:
{text}
""")

parser_prompt = ChatPromptTemplate.from_template("""
You are a strict resume parser.

Extract structured information from the resume text.

Return ONLY valid JSON in the exact format below:

{{
  "skills": [string],
  "experience": [
    {
      "role": string,
      "company": string,
      "description": string
    }
  ],
  "projects": [
    {
      "name": string,
      "description": string,
      "technologies": [string]
    }
  ],
  "education": [
    {
      "degree": string,
      "institution": string
    }
  ]
}}

STRICT RULES:
- Skills = technologies, tools, programming languages
- Experience = jobs, internships, work roles (NOT projects)
- Projects = personal/academic projects (NOT jobs)
- Education = degrees, college, school

- NEVER mix projects into experience
- NEVER put project inside experience
- If a section is missing, return []
- Do NOT add extra keys
- Do NOT return text, ONLY JSON

Resume:
{text}
""")

match_prompt = ChatPromptTemplate.from_template("""
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

query_prompt = ChatPromptTemplate.from_template("""
You are an expert career coach and job search assistant.

Given this resume data (already parsed to JSON), propose the best job search query to use in a job API.

Rules:
- Output MUST be valid JSON only.
- Keep "query" short (2-6 words), like a real job-search keyword.
- Prefer a role title over listing many skills.

Resume JSON:
{resume_json}

Return JSON:
{{
  "query": "string"
}}
""")

structured_data_prompt = ChatPromptTemplate.from_template("""
You are an AI resume parser.

Extract structured data from the resume.

Return ONLY valid JSON.
Do NOT include:
- explanations
- thinking
- markdown
- code blocks

Format:
{{
  "skills": [],
  "experience": [],
  "projects": [],
  "education": []
}}

Resume:
{context}
""")

application_prompt = ChatPromptTemplate.from_template("""
You are an AI job application assistant.

STRICT RULES:
- Use ONLY information from the resume
- DO NOT add new skills
- DO NOT hallucinate
- Output MUST be valid JSON only (no extra text)

Return JSON in this format:

{{
  "cover_letter": "string",
  "why_fit": "string",
  "strengths": ["string", "string", "string"]
}}

Resume:
{resume}

Job:
{job}
""")
