from config import OUTPUT_CSV
from genai_classifier import process_batch,INPUT_XLSX

# -------- MAIN --------
if __name__ == "__main__":
    process_batch(INPUT_XLSX, OUTPUT_CSV)
    print(f"Processing complete. Output saved to {OUTPUT_CSV}")