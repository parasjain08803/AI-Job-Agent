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

            if isinstance(res, dict):
                extracted_data.append(res)

        except Exception:
            continue

    final_output = {
        "skills": [],
        "experience": [],
        "projects": [],
        "education": []
    }

    for item in extracted_data:
        for key in final_output:

            if key not in item:
                continue

            value = item[key]

            if isinstance(value, list):
                for v in value:

                    if key in ["projects", "experience"]:
                        if isinstance(v, dict):
                            final_output[key].append(v)

                    else:
                        if isinstance(v, (str, int, float)):
                            final_output[key].append(str(v))

    final_output["skills"] = list(set(final_output["skills"]))
    final_output["education"] = list(set(final_output["education"]))

    return final_output