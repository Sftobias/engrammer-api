from pydantic import BaseModel, Field, HttpUrl
from typing import Any, Dict, List, Optional
from app.models.db_models import ActivityQuestion

# --- Tenant models ---
class TenantCreate(BaseModel):
    tenant_id: str = Field(..., description="Unique tenant/user id")
    tenant_name: Optional[str] = Field(None, description="Name of the tenant/user")
    tenant_email: Optional[str] = Field(None, description="Email of the tenant/user")
    neo4j_uri: Optional[str] = Field(None, example="bolt://localhost:7687")
    neo4j_user: Optional[str] = Field(None)
    neo4j_password: Optional[str] = Field(None)

class TenantInfo(BaseModel):
    tenant_id: str

# --- Pipeline invocation ---
class ChatMessage(BaseModel):
    role: str
    content: Any  # string or list of {type: text|image_url}

class MemoryInvokeRequest(BaseModel):
    pipeline_id: str
    user_message: str
    messages: List[ChatMessage] = Field(default_factory=list)
    session_id: Optional[str] = Field(default="default", description="Conversation id within tenant")
    
class HistoryInvokeRequest(BaseModel):
    pipeline_id: str
    user_message: str
    messages: List[ChatMessage] = Field(default_factory=list)
    session_id: str = Field(description="Conversation id within tenant")
    activity_index: int = Field(..., description="Index of the activity user is referring to")

class InvokeResponse(BaseModel):
    output: str

class PipelineInfo(BaseModel):
    id: str
    name: str
    description: str

class PipelinesList(BaseModel):
    data: List[PipelineInfo]

class EndConversationRequest(BaseModel):
    tenant_id: str
    pipeline_id: str
    session_id: Optional[str] = "default"

class EndConversationResponse(BaseModel):
    message: str
    
# --- Activities and Questions ---
class ActivityInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    
class QuestionDetail(BaseModel):
    id: str
    activity_id: str
    contexto: Optional[str] = None
    pregunta: str
    respuesta_correcta: str

class ActivityDetail(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    questions: List[QuestionDetail]

