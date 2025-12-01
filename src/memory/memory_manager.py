# src/memory/memory_manager.py
import time
from typing import Dict, Any, List


class MemoryManager:
    """
    Simple long-term memory storage for users.
    Stores knowledge as { user_id: { memory_key: [entries...] } }
    """

    def __init__(self):
        # Example structure:
        # memories = {
        #   "user123": {
        #       "submitted_ticket": [ {...}, {...} ]
        #   }
        # }
        self.memories: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    def create_memory(self, user_id: str, memory_key: str, data: Dict[str, Any]):
        if user_id not in self.memories:
            self.memories[user_id] = {}

        if memory_key not in self.memories[user_id]:
            self.memories[user_id][memory_key] = []

        entry = {
            "timestamp": time.time(),
            "data": data
        }
        self.memories[user_id][memory_key].append(entry)
        return entry

    def query_memory(self, user_id: str, memory_key: str) -> List[Dict[str, Any]]:
        return self.memories.get(user_id, {}).get(memory_key, [])

    def list_users(self):
        return list(self.memories.keys())