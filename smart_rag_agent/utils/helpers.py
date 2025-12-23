def apply_nest_asyncio():
    """
    Safely apply nest_asyncio only if an event loop is already running.
    Prevents RuntimeError and Streamlit Cloud issues.
    """
    try:
        import asyncio
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return  # No running loop → do nothing

    try:
        import nest_asyncio
        nest_asyncio.apply()
    except Exception:
        pass
