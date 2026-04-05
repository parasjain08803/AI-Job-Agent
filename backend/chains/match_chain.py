from llms.prompts import match_prompt
from llms.llm import match_llm
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

match_chain = match_prompt | match_llm | parser