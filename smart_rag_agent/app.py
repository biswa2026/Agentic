import os
import streamlit as st
from dotenv import load_dotenv

# =============================================================================
# 🔐 SECRETS LOADER — SAFE FOR .env + STREAMLIT CLOUD
# =============================================================================

# Load .env locally (ignored on Streamlit Cloud)
load_dotenv()

def load_secret(key: str, default: str = ""):
    # 1️⃣ OS env (includes python-dotenv)
    if os.getenv(key):
        return os.getenv(key)

    # 2️⃣ Streamlit secrets (ONLY if they exist)
    try:
        return st.secrets[key]
    except Exception:
        return default

os.environ["OPENAI_API_KEY"] = load_secret("openai_api_key")
os.environ["PUSHOVER_API_TOKEN"] = load_secret("PUSHOVER_API_TOKEN")
os.environ["PUSHOVER_USER_KEY"] = load_secret("PUSHOVER_USER_KEY")
os.environ["TARGET_URL"] = load_secret("TARGET_URL")

if not os.environ["OPENAI_API_KEY"]:
    st.error("❌ OPENAI_API_KEY not found. Check .env or Streamlit Secrets.")
    st.stop()

# =============================================================================
# 🌐 TARGET DOMAIN
# =============================================================================

TARGET_URL = os.getenv("TARGET_URL", "").strip()

domain_name = (
    TARGET_URL.replace("https://", "")
              .replace("http://", "")
              .replace("www.", "")
              .split("/")[0]
              .split(":")[0]
              .title() or "Knowledge Base"
)

# =============================================================================
# 🧠 SAFE ASYNC PATCH (ONLY WHEN EVENT LOOP EXISTS)
# =============================================================================

from utils.helpers import apply_nest_asyncio
apply_nest_asyncio()

# =============================================================================
# 📦 APP IMPORTS
# =============================================================================

from scraper.web_scraper import scrape_url
from vectorstore.chroma_setup import get_collection, store_in_chroma
from agents.router import supervisor, contains_email
from agents import Runner, SQLiteSession
from tools.notifications import send_pushover

# =============================================================================
# 🎛️ STREAMLIT CONFIG
# =============================================================================

st.set_page_config(
    page_title="Smart RAG Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("Smart RAG Assistant")
st.caption(f"Ask anything — Knowledge sourced from **{domain_name}**")

st.success(
    f"Ready! API key loaded ({len(os.environ['openai_api_key'])} chars)"
)

# =============================================================================
# 🧾 SESSION STATE
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "db_ready" not in st.session_state:
    st.session_state.db_ready = False

# =============================================================================
# 🧠 VECTOR DB SETUP (ONE-TIME ONLY)
# =============================================================================

collection = get_collection()

def auto_index():
    if st.session_state.db_ready or not TARGET_URL:
        return

    existing = collection.get(where={"source": TARGET_URL}, limit=1)
    if existing and existing.get("ids"):
        st.session_state.db_ready = True
        return

    with st.status("Indexing knowledge base (one-time only)..."):
        content = scrape_url(TARGET_URL)
        if content.startswith("Error"):
            st.error("Failed to scrape target URL.")
            return
        store_in_chroma(TARGET_URL, content, collection)

    st.session_state.db_ready = True
    st.success("Knowledge base ready!")

# First-time setup (guarded)
if not os.path.exists("chroma_db"):
    with st.spinner("First-time setup: building vector DB (one-time)..."):
        auto_index()
    st.rerun()
elif not st.session_state.db_ready:
    auto_index()
    st.rerun()

# =============================================================================
# 💬 CHAT HISTORY (LIMITED)
# =============================================================================

for msg in st.session_state.messages[-10:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# =============================================================================
# 🧑‍💻 USER INPUT
# =============================================================================

prompt = st.chat_input("Ask something about the documentation...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # --------------------------------------------------
    # 📧 Email detection
    # --------------------------------------------------
    if contains_email(prompt):
        email = contains_email(prompt)
        send_pushover(
            "New Email Lead",
            f"Email: {email}\nQuestion: {prompt}"
        )
        reply = f"Thanks! I’ll contact **{email}** shortly."

    # --------------------------------------------------
    # 🤖 Agent execution (USER-TRIGGERED ONLY)
    # --------------------------------------------------
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                session = SQLiteSession("sessions/rag_session.db")
                result = Runner.run_sync(
                    supervisor,
                    prompt,
                    session=session,
                    max_turns=3
                )

                reply = result.final_output.strip()

                if "NO_CONTEXT_FOUND" in reply.upper():
                    send_pushover("Out-of-scope Question", prompt)
                    reply = (
                        "I don’t have information about that yet. "
                        "Try asking about the supported documentation."
                    )

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.markdown(reply, unsafe_allow_html=True)
