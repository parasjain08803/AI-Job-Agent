from llms.llm import application_llm
from llms.prompts import application_prompt

application_chain = application_prompt | application_llm