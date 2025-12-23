# vectorstore/chroma_setup.py

import os
import chromadb
from chromadb.utils import embedding_functions
import streamlit as st
from datetime import datetime

# =============================================================================
# 🔧 CONFIG — FROM ENV (SAFE FOR LOCAL + STREAMLIT CLOUD)
# =============================================================================

CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "smart_rag_collection")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
API_KEY = os.getenv("OPENAI_API_KEY")
MAX_CHUNK_CHARS = int(os.getenv("MAX_CHUNK_CHARS", "1000"))

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

# =============================================================================
# 🧠 CHROMA COLLECTION (CACHED)
# =============================================================================

@st.cache_resource(show_spinner=False)
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
            api_key=API_KEY
        )
    )

# =============================================================================
# 📥 STORE DOCUMENTS
# =============================================================================

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
            for i in range(0, len(chunk), MAX_CHUNK_CHARS):
                final_chunks.append(chunk[i:i + MAX_CHUNK_CHARS])

    # Stable unique IDs
    base_id = url.replace("https://", "").replace("http://", "").replace("/", "_")
    ids = [f"{base_id}_{i}" for i in range(len(final_chunks))]

    metadatas = [
        {"source": url, "added": datetime.utcnow().isoformat()}
        for _ in final_chunks
    ]

    collection.add(
        documents=final_chunks,
        ids=ids,
        metadatas=metadatas
    )

    return f"Indexed {len(final_chunks)} chunks from {url}"
