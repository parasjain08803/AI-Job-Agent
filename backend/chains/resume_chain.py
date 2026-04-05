from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from llms.llm import structured_data_llm
from llms.prompts import structured_data_prompt
from dotenv import load_dotenv

load_dotenv()

json_parser = JsonOutputParser()
str_output_parser=StrOutputParser()

resume_chain = structured_data_prompt | structured_data_llm | str_output_parser | json_parser