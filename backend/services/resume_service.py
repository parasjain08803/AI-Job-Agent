from langchain_text_splitters import RecursiveCharacterTextSplitter
from chains.parser_chain import parser_chain

def process_resume(documents):

    final_output=parser_chain.invoke({"text":documents.page_content})

    return final_output