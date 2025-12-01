# vectorstore/chunking.py
from langchain_text_splitters import CharacterTextSplitter

def get_text_splitter():
    return CharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separator="\n\n",
        length_function=len
    )