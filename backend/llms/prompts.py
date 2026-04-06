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
    {{
      "role": string,
      "company": string,
      "description": string
    }}
  ],
  "projects": [
    {{
      "name": string,
      "description": string,
      "technologies": [string]
    }}
  ],
  "education": [
    {{
      "degree": string,
      "institution": string
    }}
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

ats_prompt = ChatPromptTemplate.from_template("""
You are a strict ATS (Applicant Tracking System).

Analyze the resume and calculate a realistic ATS score.

=====================
RESUME TEXT:
{resume_text}

STRUCTURED DATA:
Skills: {skills}
Projects: {projects}
Experience: {experience}
=====================

SCORING RULES (STRICT):

Skills (0-30):
- Basic tools → 10-15
- Good stack → 15-25
- Advanced + depth → 25-30
- NEVER give 30 unless exceptional depth (real-world usage, specialization)

Projects (0-30):
- Basic projects → 10-15
- Good projects → 15-25
- Production-level / real impact → 25-30
- REDUCE score if:
  - No measurable results (no %, no numbers)
  - No real users
  - No complexity mentioned

Experience (0-20):
- Empty → MUST be 0
- Internship → 5-15
- Full-time → 15-20
- DO NOT assume experience

Formatting (0-20):
- Average → 10-15
- Clean → 15-18
- Excellent → 18-20

IMPORTANT RULES:
- DO NOT give full marks easily
- Be strict and realistic like a real ATS
- If experience is empty but projects are strong → do NOT heavily penalize total score
- Total ATS score = sum of all sections
- Ensure consistency between score and weaknesses

=====================

Return ONLY JSON:

{{
  "ats_score": number,
  "score_breakdown": {{
    "skills": number,
    "projects": number,
    "experience": number,
    "formatting": number
  }},
  "summary": "2-3 line evaluation",
  "strengths": ["point1", "point2"],
  "weaknesses": ["point1", "point2"],
  "missing_sections": ["section1"],
  "improvement_suggestions": ["suggestion1"],
  "keywords_found": ["keyword1"],
  "keywords_missing": ["keyword1"]
}}

=====================

FINAL CHECK BEFORE OUTPUT:
- Experience empty → score MUST be 0
- Do NOT give 30/30 easily
- Total score must match breakdown sum
""")