import requests
from config.settings import PUSHOVER_API_TOKEN, PUSHOVER_USER_KEY

def send_pushover(title: str, message: str):
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        return
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={"token": PUSHOVER_API_TOKEN, "user": PUSHOVER_USER_KEY, "title": title, "message": message},
            timeout=10
        )
    except Exception as e:
        print(f"Pushover error: {e}")