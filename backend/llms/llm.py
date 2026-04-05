from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()


classifier_llm = query_llm = ChatGroq(model="llama-3.1-8b-instant")
structured_data_llm = match_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
application_llm=ChatGroq(model="openai/gpt-oss-120b")
parser_llm = ChatGroq(model="llama-3.3-70b-versatile")