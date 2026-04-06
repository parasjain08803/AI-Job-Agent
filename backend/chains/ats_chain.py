from llms.prompts import ats_prompt
from llms.llm import parser_llm
from langchain_core.output_parsers import JsonOutputParser

ats_chain = ats_prompt | parser_llm | JsonOutputParser()