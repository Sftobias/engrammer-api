from typing import List, Union, Generator, Iterator, Dict, Any
import os
import asyncio
import neo4j
from app.core.llm import openai_client
from app.core.vision import ollama_client

# neo4j-graphrag imports
from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.generation import RagTemplate, GraphRAG
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline

from app.services.tenant_manager import TENANTS
from app.services.conversation_store import CONVERSATIONS

class PipelineGuardar:

    id = "pipeline_guardar"
    name = "Engrammer TEST PIPELINE"
    description = "Extracts memory entities/relations into Neo4j and chats to enrich details."

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        tenant = TENANTS.get(tenant_id)
        if not tenant:
            raise ValueError(f"Unknown tenant {tenant_id}")

        # Connect per-tenant
        self.neo4j_driver = TENANTS.get_driver(tenant_id)

        # LLMs / Embeddings
        self.llm = OpenAILLM(
            model_name="gpt-4o-mini",
            model_params={
                "response_format": {"type": "json_object"},
                "temperature": 0.0,
            },
        )
        self.clientOpenAI = openai_client
        self.vision_llm = ollama_client
        self.embedder = OpenAIEmbeddings()

        # Graph schema 
        self.NODES = [
            {"label": "Person", "properties": [
                {"name": "uuid", "type": "STRING"},
                {"name": "name", "type": "STRING"},
                {"name": "birthDate", "type": "DATE"},
                {"name": "gender", "type": "STRING"},
                {"name": "description", "type": "STRING"},
            ]},
            {"label": "Event", "properties": [
                {"name": "name", "type": "STRING"},
                {"name": "type", "type": "STRING"},
                {"name": "generalEvent", "type": "BOOLEAN"},
                {"name": "description", "type": "STRING"},
                {"name": "fromDate", "type": "DATE"},
                {"name": "toDate", "type": "DATE"},
            ]},
            {"label": "Place", "properties": [
                {"name": "name", "type": "STRING"},
                {"name": "location", "type": "STRING"},
                {"name": "description", "type": "STRING"},
            ]},
            {"label": "Object", "properties": [
                {"name": "name", "type": "STRING"},
                {"name": "type", "type": "STRING"},
                {"name": "brand", "type": "STRING"},
                {"name": "description", "type": "STRING"},
                {"name": "acquisitionDate", "type": "DATE"},
            ]},
            {"label": "Emotion", "properties": [{"name": "name", "type": "STRING"}]},
            {"label": "Smell", "properties": [{"name": "name", "type": "STRING"}]},
            {"label": "Taste", "properties": [{"name": "name", "type": "STRING"}]},
            {"label": "File", "properties": [
                {"name": "name", "type": "STRING"},
                {"name": "type", "type": "STRING"},
                {"name": "url", "type": "STRING"},
            ]},
        ]

        self.RELATIONS = [
            {"label": "KNOWS", "properties": [
                {"name": "relationship", "type": "STRING"},
                {"name": "fromDate", "type": "DATE"},
                {"name": "toDate", "type": "DATE"},
            ]},
            {"label": "LIVES_IN", "properties": [
                {"name": "fromDate", "type": "DATE"},
                {"name": "toDate", "type": "DATE"},
            ]},
            {"label": "OWNS", "properties": [
                {"name": "fromDate", "type": "DATE"},
                {"name": "toDate", "type": "DATE"},
            ]},
            {"label": "FEATURES_IN", "properties": [
                {"name": "role", "type": "STRING"},
            ]},
            {"label": "TAKES_PLACE_IN", "properties": []},
            {"label": "FEELS", "properties": []},
            {"label": "ASSOCIATED_WITH", "properties": []},
            {"label": "RELATED_TO", "properties": []},
        ]

        self.prompt_template = '''
        You are an assistant that has to extract the elements of a memory and structure them correctly in a property graph to enable users to query past memories.

        Extract the entities (nodes) and specify their type from the following Input text.
        Also extract the relationships between these nodes. the relationship direction goes from the start node to the end node.


        Return result as JSON using the following format:
        {{"nodes": [ {{"id": "0", "label": "the type of entity", "properties": {{"name": "name of entity" }} }}],
        "relationships": [{{"type": "TYPE_OF_RELATIONSHIP", "start_node_id": "0", "end_node_id": "1", "properties": {{"details": "Description of the relationship"}} }}] }}

        ...

        Use only fhe following nodes and relationships:
        {schema}

        Assign a unique ID (string) to each node, and reuse it to define relationships.
        Do respect the source and target node types for relationship and the relationship direction.

        Do not return any additional information other than the JSON in it. Make sure the structure is correct, and that you just use the node tags and relationships i have just described.

        Do not add line jumps with slash n.

        Examples:
        {examples}

        Input text:

        {text}
        '''

        self.kg_builder = SimpleKGPipeline(
            llm=self.llm,
            driver=self.neo4j_driver,
            text_splitter=FixedSizeSplitter(chunk_size=5000, chunk_overlap=1000),
            embedder=self.embedder,
            entities=self.NODES,
            relations=self.RELATIONS,
            prompt_template=self.prompt_template,
            from_pdf=False,
        )

    def _developer_preamble(self) -> dict:
        return {
            "role": "developer",
            "content": '''
                Eres un asistente que almacena recuerdos del usuario, si detectas que falta información relevante dile al usuario que datos consideras interesantes y especifícale que puede darte más información. 
                Es posible que el usuario haya proporcionado imagenes para complementar el recuerdo, si es así, debes seguir las siguientes normas: 
                MUY IMPORTANTE: No des por hecho lo que se pasa como descripción de la imagen, dile al usuario lo que aparece en la imagen desde la duda, de modo que el lo tenga que confirmar. 
                Utiliza la descripción de las imágenes para complementar el recuerdo. 
                No hagas una enumeración literal de lo que aparece en la imagen, sino que intenta describir y preguntar lo que ves de forma natural y fluida, como si fuese una conversación. 
                Dentro de la conversación intenta preguntar al usuario por las personas que aparecen en la imagen para que las identifique y las puedas añadir al recuerdo, pero no te centres solo en ello y no asumas quien de las personas que puedan aparecer en la imagen es el usuario ni las relaciones que pueden tener entre si (madre, padre, amigo, primo, etc), pregunta al usuario. 
                Si no hay imágenes, simplemente pregunta al usuario por los datos que consideres relevantes. 
                Separa claramente lo que dice el usuario (literal) de lo que pone en la descripción de la imagen (no literal, no lo dice el usuario, se ha extraido de una imagen pero puede contener errores). 
                Por ejemplo, si el usuario te dice que ha ido a un concierto, pregúntale por el nombre del artista, la fecha del concierto, si fue con alguien, si le gustó, etc. 
                Si además aparece la descripcion de una imagen que coincide, di cosas como: parece que en la imagen que has adjuntado aparece un concierto, ¿es correcto? Veo que aparecen varias personas en la imagen, ¿podrías decirme quiénes son? ¿Es alguna de ellas tú? ¿Qué relación tienes con las personas que aparecen en la imagen? También veo que estais tomando algo de beber, ¿qué es? ¿lo comprasteis en el concierto? etc.
            '''
        }

    def _ensure_preamble(self, tenant_id: str, session_id: str):
        history = CONVERSATIONS.get(tenant_id, session_id)
        if not history or history[0].get("role") != "developer":
            CONVERSATIONS.append(tenant_id, session_id, **self._developer_preamble())

    def comprobar_fin_conversacion(self, text: str) -> bool:
        resp = self.clientOpenAI.responses.create(
            model="gpt-4o-mini",
            instructions='''
                Eres un asistente que esta escuchando una conversación con un usuario en el que el usuario está describiendo un recuerdo suyo. T
                Tu tarea es identificar si el usuario quiere finalizar la conversación y guardar el recuerdo. El usuario tiene que expresar de forma explicita que quiere finalizar la conversación y guardar el recuerdo, por ejemplo, diciendo "finalizar conversación" o "guardar recuerdo".
                El usuario también puede exxpresarlo diciendo que el recuerdo ya está completo o que no quiere añadir más información.
                Devuelve True si el usuario quiere finalizar la conversación y guardar el recuerdo, y False en caso contrario.
                Responde exclusivamente True o False. 
                
                Ejemplo de mensaje del usuario: "Eso es todo". Respuesta: True
                Ejemplo de mensaje del usuario: "No tengo nada más que añadir". Respuesta: True
                Ejemplo de mensaje del usuario: "Estuve con mis familiares en un concierto y lo pasamos genial". Respuesta: False
            ''',
            input=text,
        ).output_text.strip().upper()
        return resp == "TRUE" or text.strip().upper() == "END_MEMORY"

    def finalizar_conversacion(self, tenant_id: str, session_id: str) -> str:
        history = CONVERSATIONS.get(tenant_id, session_id)
        full_conversation = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in history if m["role"] != "developer")
        resumen = self.clientOpenAI.responses.create(
            model="gpt-4o-mini",
            instructions='''
                Eres un asistente que tiene que resumir una conversación con un usuario.
                En la conversación verás que el usuario ha ido describiendo un recuerdo suyo mientras que un asistente le ha ido preguntando por detalles relevantes.
                Tu tarea es resumir el recuerdo de forma clara. Describe el recuerdo, no la interacción con el asistente. (Por ejemplo, no digas "el asistente le preguntó al usuario por el nombre del artista", sino "el usuario fue a un concierto de [nombre del artista]").
                No añadas información que no haya sido proporcionada por el usuario. No inventes información que no haya sido proporcionada por el usuario.
                El resumen tiene que contener todos los detalles del recuerdo que se describen en la conversación.
                Además es posible que el recuerdo incluya descripciones de imágenes, si es así, debes incluir la información relevante de las imágenes en el resumen.
                ''',
            input=full_conversation,
        ).output_text

        # Persist into Neo4j
        asyncio.run(self.kg_builder.run_async(text=resumen))

        # Reset conversation to fresh preamble
        CONVERSATIONS.clear(tenant_id, session_id)
        CONVERSATIONS.append(tenant_id, session_id, **self._developer_preamble())
        return f"Conversación finalizada. Resumen guardado: {resumen}"

    def invoke(self, tenant_id: str, session_id: str, user_message: str, messages: List[dict]) -> str:
        self._ensure_preamble(tenant_id, session_id)

        last_user_message = None
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_message = m
                break

        has_image = False
        image_list = []
        if last_user_message:
            content = last_user_message.get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "image_url":
                        has_image = True
                        img_data = part["image_url"]["url"]
                        if img_data.startswith("data:image"):
                            img_data = img_data.split(",", 1)[1]
                        image_list.append(img_data)

        if has_image and self.vision_llm:
            image_messages = [{
                "role": "user",
                "content": "Describe la imagen de forma detallada, incluyendo los objetos, personas, lugares y cualquier otro elemento relevante que aparezca en la imagen. Si aparecen personas no asumas las relaciones entre ellas. Responde solo con la descripción de la imagen.",
                "images": image_list,
            }]
            try:
                image_description = self.vision_llm.chat(model="gemma3:4b", messages=image_messages).message.content
                user_message = f"{user_message}. Además de este recuerdo, el usuario ha adjuntado una imagen. Esta es su descripción: {image_description}".strip()
            except Exception:
                pass
        
        if self.comprobar_fin_conversacion(user_message):
            return self.finalizar_conversacion(tenant_id, session_id)
        
        # Store and chat
        CONVERSATIONS.append(tenant_id, session_id, role="user", content=user_message)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=CONVERSATIONS.get(tenant_id, session_id),
        ).choices[0].message.content

        CONVERSATIONS.append(tenant_id, session_id, role="assistant", content=response)

        return response

def pipeline_guardar_factory():
    def _builder(tenant_id: str) -> PipelineGuardar:
        return PipelineGuardar(tenant_id)
    return _builder
