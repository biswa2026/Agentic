import os
import streamlit as st

# ===================== FINAL SECRETS LOADER – WORKS 100% ON STREAMLIT CLOUD =====================
# GitHub Actions secrets (added in Settings → Secrets and variables → Actions) are auto-injected
# This fallback only runs locally
if not os.getenv("OPENAI_API_KEY") or len(os.getenv("OPENAI_API_KEY", "")) < 100:
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        os.environ["PUSHOVER_API_TOKEN"] = st.secrets["PUSHOVER_API_TOKEN"]
        os.environ["PUSHOVER_USER_KEY"] = st.secrets["PUSHOVER_USER_KEY"]
        os.environ["TARGET_URL"] = st.secrets["TARGET_URL"]
    except:
        pass  # Expected on Streamlit Cloud – secrets already in os.environ

# Extract domain name safely
TARGET_URL = os.getenv("TARGET_URL", "").strip()
domain_name = (
    TARGET_URL.replace("https://", "")
              .replace("http://", "")
              .replace("www.", "")
              .split("/")[0]
              .split(":")[0]
              .title() or "Link Router Docs"
)

# Final status
st.success(f"Ready! Key length: {len(os.getenv('OPENAI_API_KEY', ''))} | Source: {domain_name}")

# =========================================================================================

from scraper.web_scraper import scrape_url
from vectorstore.chroma_setup import get_collection, store_in_chroma
from agents.router import supervisor, contains_email
from agents import Runner, SQLiteSession
from tools.notifications import send_pushover
from utils.helpers import *  # applies nest_asyncio

st.set_page_config(page_title="Smart RAG Assistant", page_icon="🤖", layout="centered")
st.title("Smart RAG Assistant")
st.caption(f"Ask anything — Knowledge sourced from **{domain_name}**")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db_ready" not in st.session_state:
    st.session_state.db_ready = False

collection = get_collection()

def auto_index():
    if st.session_state.db_ready or not TARGET_URL:
        return
    existing = collection.get(where={"source": TARGET_URL}, limit=1)
    if existing["ids"]:
        st.session_state.db_ready = True
        return
    with st.status("Indexing knowledge base (one-time only)..."):
        content = scrape_url(TARGET_URL)
        if content.startswith("Error"):
            st.error("Failed to load page content.")
            return
        store_in_chroma(TARGET_URL, content, collection)
    st.session_state.db_ready = True
    st.success("Knowledge base ready!")

# First-time indexing (only runs once)
if not os.path.exists("chroma_db"):
    with st.spinner("First time setup: Building vector database (4–7 min one-time)..."):
        auto_index()
    st.rerun()
elif not st.session_state.db_ready:
    auto_index()
    st.rerun()

# Chat history
for msg in st.session_state.messages[-10:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# User input
if prompt := st.chat_input("Ask something about TP-Link routers..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if contains_email(prompt):
        email = contains_email(prompt)
        send_pushover("New Email Lead", f"Email: {email}\nQuestion: {prompt}")
        reply = f"Thanks! I’ll contact **{email}** shortly."
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                session = SQLiteSession("sessions/rag_session.db")
                result = Runner.run_sync(supervisor, prompt, session=session, max_turns=3)
                reply = result.final_output.strip()
                if "NO_CONTEXT_FOUND" in reply.upper():
                    send_pushover("Out-of-scope Question", prompt)
                    reply = "I don’t have information about that yet. Try asking about TP-Link routers, Wi-Fi setup, features, troubleshooting, etc."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply, unsafe_allow_html=True)
