from typing import List, Union, Generator, Iterator
from app.services.tenant_manager import TENANTS
from app.services.conversation_store import CONVERSATIONS
from app.core.llm import openai_client



class PipelineRecuperar:

    id = "pipeline_recuperar"
    name = "Engrammer – Recuperar Recuerdo"
    description = "Responde preguntas sobre recuerdos con RAG"

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        tenant = TENANTS.get(tenant_id)
        if not tenant:
            raise ValueError(f"Unknown tenant {tenant_id}")
        
    def _system_preamble(self) -> dict:
        return {
            "role": "system",
            "content": '''

            '''
        }

    def _ensure_preamble(self, tenant_id: str, session_id: str):
        history = CONVERSATIONS.get(tenant_id, session_id)
        if not history or history[0].get("role") != "system":
            CONVERSATIONS.append(tenant_id, session_id, **self._system_preamble())

    def invoke(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        messages: List[dict],
    ) -> Union[str, Generator, Iterator]:
        
        self._ensure_preamble(tenant_id, session_id)

        CONVERSATIONS.append(tenant_id, session_id, role="user", content=user_message)

        answer = openai_client

        if not answer:
            answer = (
                "No he encontrado suficiente contexto aún. "
                "¿Puedes darme algún detalle más (personas, lugar, fecha aproximada) para afinar la búsqueda?"
            )

        CONVERSATIONS.append(tenant_id, session_id, role="assistant", content=answer)
        return answer

def pipeline_recuperar_factory():
    def _builder(tenant_id: str) -> PipelineRecuperar:
        return PipelineRecuperar(tenant_id)
    return _builder
