from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv("openai_api_key"))