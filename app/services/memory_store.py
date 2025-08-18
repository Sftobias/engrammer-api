from collections import defaultdict
from typing import Dict

class MemoryStore:

    def __init__(self):
        self._data: Dict[str, Dict[str, str]] = defaultdict(lambda: defaultdict(str))

    def set(self, tenant_id: str, session_id: str, content: str):
        self._data[tenant_id][session_id] = content

    def get(self, tenant_id: str, session_id: str) -> str:
        return self._data[tenant_id][session_id]

    def clear(self, tenant_id: str, session_id: str):
        self._data[tenant_id].pop(session_id, None)

MEMORIES = MemoryStore()