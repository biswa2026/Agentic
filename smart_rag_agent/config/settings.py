import os
import re
from dotenv import load_dotenv

'''load_dotenv()

API_KEY = os.getenv("openai_api_key")
if not API_KEY:
    raise ValueError("Missing openai_api_key in environment variables or .env file")

os.environ["OPENAI_API_KEY"] = API_KEY

TARGET_URL = os.getenv("TARGET_URL")
if not TARGET_URL:
    raise ValueError("TARGET_URL is required in .env")

PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY") '''

import streamlit as st  # Make sure this is imported at the top

# Load API key from Streamlit secrets (this is the secure way)
API_KEY = st.secrets.get("openai_api_key")  # Use .get() to avoid crashes if missing

if not API_KEY:
    st.error("OpenAI API key not found. Check your Secrets settings.")
    st.stop()

# Set for OpenAI SDK
os.environ["OPENAI_API_KEY"] = API_KEY
PUSHOVER_API_TOKEN =st.secrets.get("PUSHOVER_API_TOKEN")
PUSHOVER_USER_KEY = st.secrets.get("PUSHOVER_USER_KEY")
TARGET_URL =st.secrets.get("TARGET_URL")

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAX_HISTORY = 6

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "docs"
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_CHUNK_CHARS = 8000

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80
