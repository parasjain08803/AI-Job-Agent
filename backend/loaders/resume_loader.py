from langchain_community.document_loaders import PyPDFLoader
import tempfile

def load_resume(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        path = tmp.name

    loader = PyPDFLoader(path)
    return loader.load()