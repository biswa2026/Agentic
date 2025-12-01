from agents import function_tool
from vectorstore.chroma_setup import get_collection

@function_tool
def retrieve_context(query: str) -> str:
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=2)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    
    if not docs:
        return "NO_CONTEXT_FOUND"
    
    text = "\n\n".join(
        f"[Source: {m.get('source')}] {d.strip()}"
        for d, m in zip(docs, metas)
    )
    return text[:6000]