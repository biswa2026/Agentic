from dotenv import load_dotenv
load_dotenv()
import os


API_KEY = os.getenv("openai_api_key")
MODEL = "gpt-4o-mini"
INPUT_CSV = "cust_utterance_dec25.xlsx"
OUTPUT_CSV = "output_classified.csv"
RATE_LIMIT_DELAY = 0.3  # seconds between calls