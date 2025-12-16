from openai import OpenAI
import pandas as pd
import json
import time
from config import API_KEY, MODEL, OUTPUT_CSV, RATE_LIMIT_DELAY

# -------- INPUT FILE (EXCEL) --------
INPUT_XLSX = "/workspaces/Agentic/genai_oneshot_prompt/cust_utterance_dec25.xlsx"

# -------- OPENAI CLIENT --------
client = OpenAI(api_key=API_KEY)

# -------- SYSTEM PROMPT --------
SYSTEM_PROMPT = """
You are a service desk analytics assistant.

Task:
Analyze customer service desk utterances and return EXACTLY 3 fields in JSON:
1. conversation_summary
2. driver
3. sub_driver

Driver MUST be one of:
- Network
- Billing
- Experience
- Financial Hardship
- Competitor Offer

Rules:
- Choose the single most dominant driver
- Be concise and business-ready
- Sub-driver must be specific
- Return VALID JSON ONLY
"""

# -------- ONE-SHOT EXAMPLE --------
ONE_SHOT_EXAMPLE = """
Example Input:
"I keep losing internet every evening and support has not fixed it yet."

Example Output:
{
  "conversation_summary": "Customer reports recurring evening internet outages with unresolved support issues",
  "driver": "Network",
  "sub_driver": "Intermittent connectivity"
}
"""

# -------- GENAI CLASSIFIER --------
def classify_utterance(utterance: str) -> dict:
    prompt = f"""
{ONE_SHOT_EXAMPLE}

Now analyze the following customer utterance:

"{utterance}"

Return JSON only.
"""

    response = client.responses.create(
        model=MODEL,
        temperature=0.2,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
    )

    output_text = response.output_text.strip()
    return json.loads(output_text)

# -------- BATCH PROCESSOR --------
def process_batch(input_xlsx: str, output_csv: str):
    # READ EXCEL FILE
    df = pd.read_excel(input_xlsx)

    results = []

    for idx, row in df.iterrows():
        cust_id = row["cust_id"]
        account_num = row["account_num"]
        event_dt = row["event_dt"]
        utterance = str(row["utterance"])

        try:
            classification = classify_utterance(utterance)

            results.append({
                "cust_id": cust_id,
                "account_num": account_num,
                "event_dt": event_dt,
                "conversation_summary": classification["conversation_summary"],
                "driver": classification["driver"],
                "sub_driver": classification["sub_driver"]
            })

        except Exception as e:
            # LOG ERROR FOR VISIBILITY
            print(f"[ERROR] Row {idx} failed: {e}")

            results.append({
                "cust_id": cust_id,
                "account_num": account_num,
                "event_dt": event_dt,
                "conversation_summary": "Classification error",
                "driver": "Experience",
                "sub_driver": "Model failure"
            })

        time.sleep(RATE_LIMIT_DELAY)

    output_df = pd.DataFrame(
        results,
        columns=[
            "cust_id",
            "account_num",
            "event_dt",
            "conversation_summary",
            "driver",
            "sub_driver"
        ]
    )

    output_df.to_csv(output_csv, index=False)


