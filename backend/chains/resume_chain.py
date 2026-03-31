from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

json_parser = JsonOutputParser()
str_output_parser=StrOutputParser()

prompt = ChatPromptTemplate.from_template("""
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

resume_chain = prompt | llm | str_output_parser | json_parser