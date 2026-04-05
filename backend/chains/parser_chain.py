from llms.llm import parser_llm
from llms.prompts import parser_prompt
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

parser_chain = parser_prompt | parser_llm | parser