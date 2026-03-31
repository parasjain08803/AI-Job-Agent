from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(model="openai/gpt-oss-120b")

prompt = ChatPromptTemplate.from_template("""
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

application_chain = prompt | llm