from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv()

# Check if Groq API key is available
groq_api_key = os.getenv("GROQ_API_KEY")

if groq_api_key:
    classifier_llm = query_llm = ChatGroq(model="llama-3.1-8b-instant")
    structured_data_llm = match_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
    application_llm = ChatGroq(model="openai/gpt-oss-120b")
    parser_llm = ChatGroq(model="llama-3.3-70b-versatile")
else:
    # Fallback mock responses when API key is not available
    print("WARNING: Groq API key not found. Using mock responses.")
    classifier_llm = query_llm = None
    structured_data_llm = match_llm = None
    application_llm = None
    parser_llm = None