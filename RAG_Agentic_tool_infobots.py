# app.py
import os
import re
import httpx
import requests
from datetime import datetime
from bs4 import BeautifulSoup

import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from agents import Agent, function_tool, Runner, SQLiteSession,model_settings,ModelSettings
#from agents.tools import tool
#from google.colab import userdata
#from google.colab.userdata import SecretNotFoundError # Corrected import
import os
from dotenv import load_dotenv
load_dotenv()

# Fix asyncio for Streamlit async agent execution
import asyncio
import nest_asyncio



try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

nest_asyncio.apply()

# Agents
from agents import Agent, function_tool, Runner, SQLiteSession, ModelSettings

# Chroma + text splitting
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import CharacterTextSplitter


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart RAG Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ENV CONFIG
# ============================================================


EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAX_HISTORY = 6


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "db_ready" not in st.session_state:
    st.session_state.db_ready = False


# ============================================================
# CHROMA DB
# ============================================================

@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path="chroma_db")
    return client.get_or_create_collection(
        name="docs",
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-3-small",
            api_key=API_KEY
        )
    )

collection = get_collection()

text_splitter = CharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=80,
    separator="\n\n"
)


# ============================================================
# SCRAPER
# ============================================================

def scrape_url(url: str) -> str:
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            r = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())[:250_000]

    except Exception as e:
        return f"Error scraping {url}: {e}"

#PUSHOVER

def send_pushover(title: str, message: str):
    """Send a Pushover notification to the developer."""
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        return  # silently ignore if config missing

    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_API_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "title": title,
                "message": message
            },
            timeout=10
        )
    except Exception as e:
        print(f"Pushover error: {e}")



# ============================================================
# INDEXING
# ============================================================

def store_in_chroma(url: str, content: str) -> str:
    if len(content) < 200:
        return "Not enough content to index."

    raw_chunks = text_splitter.split_text(content)
    MAX_CHARS = 8000
    final_chunks = []

    # enforce strict max chunk size
    for chunk in raw_chunks:
        if len(chunk) <= MAX_CHARS:
            final_chunks.append(chunk)
        else:
            for i in range(0, len(chunk), MAX_CHARS):
                final_chunks.append(chunk[i:i + MAX_CHARS])

    ids = [
        f"{url.replace('https://','').replace('/','_')}_{i}"
        for i in range(len(final_chunks))
    ]
    metas = [{"source": url, "added": datetime.now().isoformat()} for _ in final_chunks]

    collection.add(documents=final_chunks, ids=ids, metadatas=metas)
    return f"Indexed {len(final_chunks)} chunks."


def auto_index():
    """Silent auto index — no UI output."""
    if st.session_state.db_ready or not TARGET_URL:
        return

    exist = collection.get(where={"source": TARGET_URL}, limit=1)
    if exist["ids"]:
        st.session_state.db_ready = True
        return

    content = scrape_url(TARGET_URL)
    if content.startswith("Error"):
        return  # silently fail

    store_in_chroma(TARGET_URL, content)
    st.session_state.db_ready = True


# ============================================================
# RETRIEVAL TOOL
# ============================================================

@function_tool
def retrieve_context(query: str) -> str:
    results = collection.query(query_texts=[query], n_results=2)

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    if not docs:
        return "NO_CONTEXT_FOUND"

    text = "\n\n".join(
        f"[Source: {m.get('source')}] {d.strip()}"
        for d, m in zip(docs, metas)
    )

    return text[:6000]  # token-safe


# ============================================================
# AGENTS
# ============================================================

qa_agent = Agent(
    name="Answer Engine",
    instructions=(
        "Use retrieved context when available. "
        "If context is provided, cite it as (source: URL). "
        "Keep answers short, clear, and accurate."
    ),
    tools=[retrieve_context],
    model="gpt-4o-mini",
    model_settings=ModelSettings(max_tokens=512)
)

supervisor = Agent(
    name="Router",
    instructions=(
        "If user provides an email, acknowledge politely. "
        "Otherwise, delegate to the Answer Engine."
    ),
    handoffs=[qa_agent],
    model="gpt-4o-mini",
    model_settings=ModelSettings(max_tokens=512)
)


# ============================================================
# UI — CLEAN CHAT EXPERIENCE
# ============================================================

domain_name = (TARGET_URL or "").replace("https://","").replace("www.","").split("/")[0].title()

st.title("Smart RAG Assistant")
st.caption(f"Ask anything — Knowledge sourced from **{domain_name}**")

if not st.session_state.db_ready:
    auto_index()
    st.rerun()


# show chat history
for msg in st.session_state.messages[-MAX_HISTORY:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# CHAT INPUT
# ============================================================
if prompt := st.chat_input("Ask something..."):

    # store user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # detect email in user prompt
    emails = EMAIL_REGEX.findall(prompt)

    # ============================================================
    # EMAIL HANDLING + PUSHOVER
    # ============================================================
    if emails:
        email = emails[0]

        # 🔔 Send pushover alert
        send_pushover(
            "Email Shared in Assistant",
            f"User shared email: {email}\nPrompt: {prompt}"
        )

        reply = f"Thanks! I’ll reach out to **{email}** soon."
        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

    # ============================================================
    # NORMAL QUESTION HANDLING
    # ============================================================
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                session = SQLiteSession("rag_session")

                result = Runner.run_sync(
                    supervisor,
                    prompt,
                    session=session,
                    max_turns=3
                )

                answer = result.final_output.strip()

                # Out-of-box detection
                if "NO_CONTEXT_FOUND" in answer.upper():

                    # 🔔 Send pushover alert
                    send_pushover(
                        "Out-of-Box Question Asked",
                        f"User asked something outside indexed context:\n{prompt}"
                    )

                    answer = (
                        "I don’t have info on that yet — try asking something else."
                    )

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
