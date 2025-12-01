from agents.core import SQLiteSession

# Wrapper (future expansion)
class SessionStore:
    @staticmethod
    def create(name="rag_session"):
        return SQLiteSession(name)
