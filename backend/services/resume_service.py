from langchain_text_splitters import RecursiveCharacterTextSplitter
from chains.parser_chain import parser_chain

def process_resume(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)

    extracted_data = []

    for chunk in chunks:
        try:
            res = parser_chain.invoke({"text": chunk.page_content})
            extracted_data.append(res)
        except:
            continue

    final_output = {
        "skills": set(),
        "experience": set(),
        "projects": set(),
        "education": set()
    }

    for item in extracted_data:
        for key in final_output:
            if key in item:
                for val in item[key]:
                    if isinstance(val, dict):
                        final_output[key].add(str(val))
                    else:
                        final_output[key].add(val)

    final_output = {k: list(v) for k, v in final_output.items()}

    return final_output