from collections import defaultdict
from typing import Dict, List

class ConversationStore:

    def __init__(self):
        self._data: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))

    def append(self, tenant_id: str, session_id: str, role: str, content: str):
        self._data[tenant_id][session_id].append({"role": role, "content": content})

    def get(self, tenant_id: str, session_id: str) -> List[dict]:
        return list(self._data[tenant_id][session_id])

    def set(self, tenant_id: str, session_id: str, history: List[dict]):
        self._data[tenant_id][session_id] = list(history)

    def clear(self, tenant_id: str, session_id: str):
        self._data[tenant_id].pop(session_id, None)

CONVERSATIONS = ConversationStore()