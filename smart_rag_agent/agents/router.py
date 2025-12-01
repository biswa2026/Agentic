from agents import Agent, ModelSettings
from .qa_agent import qa_agent
import re
from config.settings import EMAIL_REGEX

supervisor = Agent(
    name="Router",
    instructions=(
        "Check if user message contains an email. "
        "If yes, respond politely acknowledging it and do not delegate. "
        "Otherwise, delegate to the Answer Engine.but dont mention email while respond unless user shared mail id."
    ),
    handoffs=[qa_agent],
    model="gpt-4o-mini",
    model_settings=ModelSettings(max_tokens=512)
)

def contains_email(text: str) -> bool:
    return bool(EMAIL_REGEX.search(text))