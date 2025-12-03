import os
import streamlit as st

# Load secrets from GitHub Actions (Streamlit Cloud) OR fall back to st.secrets (local)
for key in ["OPENAI_API_KEY", "PUSHOVER_API_TOKEN", "PUSHOVER_USER_KEY", "TARGET_URL"]:
    if key not in os.environ:
        os.environ[key] = st.secrets.get(key, "") if "st.secrets" in globals() else ""

# Optional: quick visual confirmation (remove later if you want)
st.write("All secrets loaded →", 
         len(os.getenv("OPENAI_API_KEY", "")) == 168,  # should be True
         "TARGET_URL →", os.getenv("TARGET_URL"))

if not os.path.exists("chroma_db"):   # ← this folder is created only after first successful indexing
    with st.spinner("First time setup: Indexing TP-Link Router docs into vector DB (4–7 min one-time only)..."):
        auto_index()                      # your existing function
    st.success("Indexing complete! Ready to chat.")
else:
    st.success("Vector DB already exists – instant loading")
    st.success(f"Secrets OK | Key length: {len(os.getenv('OPENAI_API_KEY'))} | URL: {os.getenv('TARGET_URL')}")

import streamlit as st
#from config.settings import TARGET_URL
from scraper.web_scraper import scrape_url
from vectorstore.chroma_setup import get_collection, store_in_chroma
from agents.router import supervisor, contains_email
from agents import Runner, SQLiteSession
from tools.notifications import send_pushover
from utils.helpers import *  # applies nest_asyncio

import os
st.set_page_config(page_title="Smart RAG Assistant", page_icon="🤖", layout="centered")


# OLD (delete this)
# domain_name = (TARGET_URL or "").replace...

# NEW (copy-paste this exact block)
import os
TARGET_URL = os.getenv("TARGET_URL", "").strip()

# Now safe extraction
domain_name = (
    TARGET_URL.replace("https://", "")
              .replace("http://", "")
              .replace("www.", "")
              .split("/")[0]
              .split(":")[0]   # handles ports if any
              .title()
)
if not domain_name:
    domain_name = "Link Router Docs"
st.title("Smart RAG Assistant")
st.caption(f"Ask anything — Knowledge sourced from **{domain_name}**")

# Force redeploy after adding GitHub Actions secrets

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
    content = scrape_url(TARGET_URL)
    if content.startswith("Error"):
        st.error("Failed to load knowledge base.")
        return
    result = store_in_chroma(TARGET_URL, content, collection)
    st.session_state.db_ready = True

if not st.session_state.db_ready:
    with st.status("Loading knowledge base..."):
        auto_index()
    st.rerun()

# Chat history
for msg in st.session_state.messages[-6:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if contains_email(prompt):
        email = contains_email(prompt)
        send_pushover("Email Received", f"Email: {email}\nPrompt: {prompt}")
        reply = f"Thanks! I’ll reach out to **{email}** soon."
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                session = SQLiteSession("sessions/rag_session.db")
                result = Runner.run_sync(supervisor, prompt, session=session, max_turns=3)
                reply = result.final_output.strip()

                if "NO_CONTEXT_FOUND" in reply.upper():
                    send_pushover("Out-of-Box Question", f"Question: {prompt}")
                    reply = "I don’t have information on that yet — try asking something else."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
