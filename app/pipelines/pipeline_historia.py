from typing import List, Union, Generator, Iterator

from pymilvus import MilvusClient
from app.services.activity_manager import ACTIVITIES
from app.services.tenant_manager import TENANTS
from app.services.conversation_store import CONVERSATIONS
from app.core.llm import openai_client
from app.models.schemas import ActivityQuestion


class PipelineHistoria:

    id = "pipeline_historia"
    name = "Engrammer – Historia"
    description = "Gestiona las preguntas historicas a los alumnos"

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        tenant = TENANTS.get(tenant_id)
        if not tenant:
            raise ValueError(f"Unknown tenant {tenant_id}")
        
        self.milvus_client = MilvusClient(uri="/home/ubuntu/engrammer-api/data/milvus.db")
        self.collection_name="knowledge_base_collection"
        
    def _system_preamble(self, question: ActivityQuestion) -> dict:
        return {
            "role": "system",
            "content": f"""
            Eres un asistente que tiene que hacerle una pregunta a un alumno referente a un temario, siguiendo las sigueintes instrucciones:
            - La pregunta tiene el siguiente contexto: CONTEXTO: "{question.contexto}" FIN DEL CONTEXTO. Esta parte es interna para ti, no se lo tienes que decir al alumno, el ya tiene esta información. 
            - Es decir, no le escribas este texto, pero pueds referenciarselo en la conversación.
            - La pregunta que tienes que hacer es la siguiente: PREGUNTA: "{question.pregunta}" FIN DE LA PREGUNTA, tienes que hacer la pregunta tal cual.
            - La respuesta esperada es: RESPUESTA ESPERADA "{question.respuesta_correcta} FIN DE LA RESPUESTA ESPERADA". A veces no hay una respuesta, si no que es una pregunta abierta. 
            - En caso de que sea una pregunta con respuesta, corrige la respuesta del alumno y explica por qué es correcta o incorrecta de forma amable. 
            - No seas estricto al evaluar las respuestas. Respuestas parcialemnte correctas debes darlas por correctas.
            - Si la pregunta es abierta, simplemente continua por con la conversación.
            """
        }

    def _ensure_preamble(self, tenant_id: str, session_id: str):
        history = CONVERSATIONS.get(tenant_id, session_id)
        if not history or history[0].get("role") != "system":
            
            #Obtain question and activity key
            activity_id, question_id = session_id.split("__")
            question = ACTIVITIES.get_question(activity_id, question_id)
            
            #check not None
            if not question:
                raise ValueError(f"Unknown question {question_id} for activity {activity_id}")
            
            CONVERSATIONS.append(tenant_id, session_id, **self._system_preamble(question))
            
    def emb_text(self, text):
        return (
            openai_client.embeddings.create(input=text, model="text-embedding-3-small")
            .data[0]
            .embedding
        )
        
    def get_rag_context(self, rag_topic: str) -> str:
        search_res = self.milvus_client.search(
            collection_name= self.collection_name,
            data=[
                self.emb_text(rag_topic)
            ],  # Use the `emb_text` function to convert the question to an embedding vector
            limit=3,  # Return top 3 results
            search_params={"metric_type": "IP", "params": {}},  # Inner product distance
            output_fields=["text"],  # Return the text field
        )
        
        retrieved_lines_with_distances = [
            (res["entity"]["text"], res["distance"]) for res in search_res[0]
        ]
        # print(json.dumps(retrieved_lines_with_distances, indent=4))
        
        context = "\n".join(
            [line_with_distance[0] for line_with_distance in retrieved_lines_with_distances]
        )
        
        return context
            

    def invoke(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        messages: List[dict],
    ) -> Union[str, Generator, Iterator]:
 
        self._ensure_preamble(tenant_id, session_id)

        CONVERSATIONS.append(tenant_id, session_id, role="user", content=user_message)
        
        history = CONVERSATIONS.get(tenant_id, session_id)
        full_conversation = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history if m["role"] != "system")

        rag_topic = openai_client.responses.create(
                model="gpt-4o-mini",
                input=f"Identifica la temática de los ultimos mensajes de la conversación encapsulada en <conversacion> para realizar una búsqueda en una base de datos vectorial. Se bastante se preciso al detallar la ultima tematica tratada. Devuelve unicamente el string de búsqueda.  <conversacion>{full_conversation}.</conversacion>",
                temperature=0,
            ).output_text.strip()
        
        rag_context = self.get_rag_context(rag_topic)

        # CONVERSATIONS.append(tenant_id, session_id, role="system", content=f"Usa el siguiente contexto para responder a la pregunta del alumno. Si el contexto no es relevante, simplemente ignóralo y responde a la pregunta. <contexto> {rag_context} </contexto>")
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=CONVERSATIONS.get(tenant_id, session_id),
        ).choices[0].message.content
        
        # response = openai_client.responses.create(
        #         model="gpt-4o-mini",
        #         input=f"Usa el siguiente contexto para responder a la pregunta del alumno. Si el contexto no es relevante, simplemente ignóralo y responde a la pregunta. <conversacion> {full_conversation} </conversacion> <contexto> {rag_context} </contexto>",
        #         temperature=0,
        #     ).output_text.strip()
        
        if not response:
            raise ValueError("No response from LLM")

        CONVERSATIONS.append(tenant_id, session_id, role="assistant", content=response)
        
        return response

def pipeline_historia_factory():
    def _builder(tenant_id: str) -> PipelineHistoria:
        return PipelineHistoria(tenant_id)
    return _builder
