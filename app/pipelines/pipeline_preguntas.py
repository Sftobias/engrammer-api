from typing import List, Union, Generator, Iterator
from app.core.llm import openai_client
from app.services.tenant_manager import TENANTS
from app.services.conversation_store import CONVERSATIONS
from app.services.memory_store import MEMORIES

# neo4j / graphrag
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.retrievers import VectorRetriever, VectorCypherRetriever
from neo4j_graphrag.generation import RagTemplate, GraphRAG


class PipelinePreguntas:

    id = "pipeline_preguntas"
    name = "Engrammer Preguntas"
    description = "Hace preguntas guiadas sobre recuerdos del usuario empleando RAG sobre Neo4j."

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        tenant = TENANTS.get(tenant_id)
        if not tenant:
            raise ValueError(f"Unknown tenant {tenant_id}")

        # Connect per-tenant
        self.neo4j_driver = TENANTS.get_driver(tenant_id)

        # LLMs / Embeddings
        self.embedder = OpenAIEmbeddings()
        self.llm = OpenAILLM(
            model_name="gpt-4o-mini",
            model_params={"temperature": 0.0},
        )

        try:
            create_vector_index(
                self.neo4j_driver,
                name="text_embeddings",
                label="Chunk",
                embedding_property="embedding",
                dimensions=1536,
                similarity_fn="cosine",
            )
        except Exception:
            pass

        # --- Retrievers ---
        self.vector_retriever = VectorRetriever(
            self.neo4j_driver,
            index_name="text_embeddings",
            embedder=self.embedder,
            return_properties=["text"],
        )

        self.graph_retriever = VectorCypherRetriever(
            self.neo4j_driver,
            index_name="text_embeddings",
            embedder=self.embedder,
            retrieval_query="""
                //1) Go out 2-3 hops in the entity graph and get relationships
                WITH node AS chunk
                MATCH (chunk)<-[:FROM_CHUNK]-(entity)-[relList:!FROM_CHUNK]-{1,2}(nb)
                UNWIND relList AS rel

                //2) collect relationships and text chunks
                WITH collect(DISTINCT chunk) AS chunks, collect(DISTINCT rel) AS rels

                //3) format and return context
                RETURN apoc.text.join([c in chunks | c.text], '\n') +
                apoc.text.join([r in rels |
                startNode(r).name+' - '+type(r)+' '+coalesce(r.details, '')+' -> '+endNode(r).name],
                '\n') AS info
             """
        )

        # --- Prompt template para RAG ---
        self.rag_template = RagTemplate(
            template="""
            You are a memory assistant, you have to help people to remember their memories.
            Answer the Question using the following Context. Only respond with information mentioned in the Context.
            Do not inject any speculative information not mentioned. Give detailed answers.

            # Question:
            {query_text}

            # Context:
            {context}

            # Answer:
            """,
            expected_inputs=["query_text", "context"],
        )

        self.vector_rag = GraphRAG(
            llm=self.llm, retriever=self.vector_retriever, prompt_template=self.rag_template
        )
        self.graph_rag = GraphRAG(
            llm=self.llm, retriever=self.graph_retriever, prompt_template=self.rag_template
        )

        self.clientOpenAI = openai_client

    def _get_recuerdo(self, session_id: str) -> str:
        return MEMORIES.get(self.tenant_id, session_id)

    def _set_recuerdo(self, session_id: str, value: str) -> None:
        MEMORIES.set(self.tenant_id, session_id, value)


    def invoke(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        messages: List[dict],
    ) -> Union[str, Generator, Iterator]:

        CONVERSATIONS.append(tenant_id, session_id, role="user", content=user_message)

        current_recuerdo = self._get_recuerdo(session_id)

        prompt_gate = f"""
        Eres un asistente que está manteniendo una conversación con un usuario sobre sus propios recuerdos.

        Este es el contexto, la conversación y el recuerdo.

        Conversación: {CONVERSATIONS.get(tenant_id, session_id)}
        
        Recuerdo: {current_recuerdo}
        
        Tu tarea es identificar si el usuario quiere seguir hablando del mismo recuerdo o si quiere hablar de un recuerdo diferente.
        
        También tienes que identificar si en el recuerdo se encuentra el contenido del que quiere hablar el usuario. 
        
        Si el usuario quiere cambiar de recuerdo, o el tema del que quiere hablar no se encuentra en el recuerdo, devuelve False.
        
        Si el usuario quiere continuar hablando del mismo recuerdo y la conversación esta relacionada con el recuerdo, devuelve True.
        
        Responde True solo si claramente el usuario quiere hablar del mismo recuerdo, si el usuario da cualquier señal de querer hablar de otra cosa responde False.
        
        Devuelve exclusivamente True o False.
        """
        gate = self.clientOpenAI.responses.create(
            model="gpt-4o-mini",
            input=prompt_gate,
            temperature=0,
        ).output_text.strip()

        if gate != "True" or not current_recuerdo:
            topic = self.clientOpenAI.responses.create(
                model="gpt-4o-mini",
                input=f"Estas manteniendo una conversación con un usuario sobre sus recuerdos, esta ha sido la conversación {CONVERSATIONS.get(tenant_id, session_id)}. Identifica la temática del recuerdo del que quiere hablar el usuario ahora. Únicamente responde con la temática, ningún texto adicional. Por ejemplo si el usuario dice 'Preguntame sobre mi viaje a Paris' responde con 'viaje a Paris'",
                temperature=0,
            ).output_text.strip()

            try:
                result = self.graph_rag.search(
                    f"Hablame sobre {topic}", retriever_config={"top_k": 5}
                )
                nuevo_recuerdo = (result.answer or "").strip()
            except Exception:
                nuevo_recuerdo = ""

            if not nuevo_recuerdo:
                try:
                    result = self.vector_rag.search(
                        f"Hablame sobre {topic}", retriever_config={"top_k": 5}
                    )
                    nuevo_recuerdo = (result.answer or "").strip()
                except Exception:
                    nuevo_recuerdo = ""

            if not nuevo_recuerdo:
                assistant_msg = (
                    "No he podido encontrar detalles de ese recuerdo aún. "
                )
                CONVERSATIONS.append(
                    tenant_id, session_id, role="assistant", content=assistant_msg
                )
                return assistant_msg

            self._set_recuerdo(session_id, nuevo_recuerdo)
            current_recuerdo = nuevo_recuerdo
            
            CONVERSATIONS.append(tenant_id, session_id, role="user", content=user_message)


        prompt_quiz = f"""
        
        Eres un asistente que tiene que jugar a un juego con un usuario. 
        
        Tienes un recuerdo del usuario y vas a tener que hacerle preguntas al usuario sobre dicho recuerdo para que el trate de recordar la respuesta.
        
        Tienen que ser preguntas sobre datos concretos que aparezcan en el recuerdo, como que se hizo, quienes estaban, etc.
        
        Es importante que hagas preguntas sobre cosas que tengan una respuesta concreta.
        
        La respuesta tiene que aparecer en el recuerdo, no puedes hacer preguntas sobre cosas que no estén en el recuerdo.
        
        Ten cuidado de solo dar la respuesta en las pregunta si usuario te la pide, y procura que la respuesta a nuevas preguntas no haya aparecido o sea deducible del historico de mensajes con el usuario.
        
        Si la respuesta que te da es correcta felicítale, y pregúntale si quiere que le des más detalles sobre ese recuerdo. En caso afirmativo dale más detalles sobre lo ocurrido (solo puedes dar información presente en el recuerdo, no añadas nada que no esté ya ahi)
        
        Si la respuesta es erronea, corrígele de manera amigable pero solo sobre el detalle concreto de la pregunta.
                
        Haz preguntas de una en una, no añadas varias preguntas por mensaje.
        
        Si no quedan posibles preguntas sobre ese recuerdo concreto, hazselo saber al usuario y preguntale si quiere jugar con otro recuerdo diferente.
        
        Ten un tono cercano y familiar. A menos que la respuesta se numérica no seas excesivamente estricto, si el usuario responde mas o menos acertadamente da la respuesta por correcta.
        
        Este es el recuerdo sobre el que tienes que preguntar: {current_recuerdo}
        
        Esta es la conversación con el usuario: {CONVERSATIONS.get(tenant_id, session_id)}
        
        """

        response = self.clientOpenAI.responses.create(
            model="gpt-4o-mini",
            instructions=prompt_quiz,
            input=user_message,
            temperature=0,
        ).output_text

        CONVERSATIONS.append(tenant_id, session_id, role="assistant", content=response)
        return response


def pipeline_preguntas_factory():
    def _builder(tenant_id: str) -> PipelinePreguntas:
        return PipelinePreguntas(tenant_id)
    return _builder
