from typing import List, Union, Generator, Iterator
from app.services.tenant_manager import TENANTS
from app.services.conversation_store import CONVERSATIONS

from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.retrievers import VectorRetriever, VectorCypherRetriever
from neo4j_graphrag.generation import RagTemplate, GraphRAG


class PipelineRecuperar:

    id = "pipeline_recuperar"
    name = "Engrammer – Recuperar Recuerdo"
    description = "Responde preguntas sobre recuerdos con RAG"

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        tenant = TENANTS.get(tenant_id)
        if not tenant:
            raise ValueError(f"Unknown tenant {tenant_id}")

        self.neo4j_driver = TENANTS.get_driver(tenant_id)

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
            // 1) Go out 1-2 hops in the entity graph and get relationships
            WITH node AS chunk
            MATCH (chunk)<-[:FROM_CHUNK]-(entity)-[relList:!FROM_CHUNK]-{1,2}(nb)
            UNWIND relList AS rel

            // 2) collect relationships and text chunks
            WITH collect(DISTINCT chunk) AS chunks, collect(DISTINCT rel) AS rels

            // 3) format and return context
            RETURN apoc.text.join([c in chunks | c.text], '\n') +
                   apoc.text.join([r in rels |
                     startNode(r).name+' - '+type(r)+' '+coalesce(r.details, '')+' -> '+endNode(r).name],
                     '\n') AS info
            """,
        )

        self.rag_template = RagTemplate(
            template="""
            You are a memory assistant, you have to help people to remember their memories.
            Answer the Question using the following Context. Only respond with information mentioned in the Context.
            Do not inject any speculative information not mentioned. Give detailed answers.
            Give the answer in a friendly and familiar way, but not being too literal with the context.

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

    def invoke(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        messages: List[dict],
    ) -> Union[str, Generator, Iterator]:

        CONVERSATIONS.append(tenant_id, session_id, role="user", content=user_message)

        answer = ""
        try:
            res = self.graph_rag.search(user_message, retriever_config={"top_k": 5})
            answer = (res.answer or "").strip()
        except Exception:
            answer = ""

        if not answer:
            try:
                res = self.vector_rag.search(user_message, retriever_config={"top_k": 5})
                answer = (res.answer or "").strip()
            except Exception:
                answer = ""

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
