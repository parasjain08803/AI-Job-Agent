from llms.prompts import query_prompt
from llms.llm import query_llm
from langchain_core.output_parsers import JsonOutputParser

query_parser = JsonOutputParser()

query_chain = query_prompt | query_llm | query_parser