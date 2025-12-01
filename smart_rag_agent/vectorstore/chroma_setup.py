# vectorstore/chroma_setup.py
import chromadb
from chromadb.utils import embedding_functions
from config.settings import (
    API_KEY,
    EMBEDDING_MODEL,
    CHROMA_PATH,
    COLLECTION_NAME,
    MAX_CHUNK_CHARS
)
import streamlit as st
from datetime import datetime


@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
            api_key=API_KEY
        )
    )


def store_in_chroma(url: str, content: str, collection):
    # Import here to avoid circular imports
    from .chunking import get_text_splitter

    if len(content) < 200:
        return "Not enough content to index."

    text_splitter = get_text_splitter()
    raw_chunks = text_splitter.split_text(content)

    final_chunks = []
    for chunk in raw_chunks:
        if len(chunk) <= MAX_CHUNK_CHARS:
            final_chunks.append(chunk)
        else:
            # Hard split oversized chunks
            for i in range(0, len(chunk), MAX_CHUNK_CHARS):
                final_chunks.append(chunk[i:i + MAX_CHUNK_CHARS])

    # Generate unique IDs
    base_id = url.replace("https://", "").replace("http://", "").replace("/", "_")
    ids = [f"{base_id}_{i}" for i in range(len(final_chunks))]

    metadatas = [
        {"source": url, "added": datetime.now().isoformat()}
        for _ in final_chunks
    ]

    collection.add(
        documents=final_chunks,
        ids=ids,
        metadatas=metadatas
    )

    return f"Indexed {len(final_chunks)} chunks from {url}"