# src/session/session_manager.py
import time
import uuid
from typing import Dict, Any, List


class SessionManager:
    """
    Minimal session manager storing:
      - session history (events)
      - created_at timestamps

    In production this would be external (Redis, Firestore, etc.)
    For capstone, in-memory dictionary is enough.
    """

    def __init__(self):
        # sessions stored as:
        # { session_id: {"user_id": ..., "events": [...], "created_at": ... } }
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def new_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "events": [],
            "created_at": time.time()
        }
        return session_id

    def append_event(self, session_id: str, event: Dict[str, Any]):
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        self.sessions[session_id]["events"].append({
            "timestamp": time.time(),
            "event": event
        })

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self.sessions.get(session_id, {})

    def list_sessions(self):
        return list(self.sessions.keys())