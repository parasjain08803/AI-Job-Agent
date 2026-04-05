from langchain_text_splitters import RecursiveCharacterTextSplitter
from chains.parser_chain import parser_chain

def process_resume(documents):

    full_text = "\n".join([doc.page_content for doc in documents])

    final_output = parser_chain.invoke({"text": full_text})

    return final_output