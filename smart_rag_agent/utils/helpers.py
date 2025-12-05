# utils/helpers.py
import asyncio
import nest_asyncio

def apply_nest_asyncio():
    """Call this once at the start of your app if you need nested event loops."""
    loop = asyncio.get_event_loop_policy().get_event_loop()
    if loop.is_running():
        nest_asyncio.apply()

# Optional: auto-apply the very first time the module is imported in a running loop
try:
    apply_nest_asyncio()
except RuntimeError:  # no running loop yet → fine, we'll apply later
    pass
