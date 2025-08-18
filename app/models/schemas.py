from pydantic import BaseModel, Field, HttpUrl
from typing import Any, Dict, List, Optional

# --- Tenant models ---
class TenantCreate(BaseModel):
    tenant_id: str = Field(..., description="Unique tenant/user id")
    tenant_name: str = Field(..., description="Name of the tenant/user")
    tenant_email: str = Field(..., description="Email of the tenant/user")
    neo4j_uri: str = Field(..., example="bolt://localhost:7687")
    neo4j_user: str = Field(...)
    neo4j_password: str = Field(...)

class TenantInfo(BaseModel):
    tenant_id: str

# --- Pipeline invocation ---
class ChatMessage(BaseModel):
    role: str
    content: Any  # string or list of {type: text|image_url}

class InvokeRequest(BaseModel):
    tenant_id: str
    pipeline_id: str
    user_message: str
    messages: List[ChatMessage] = Field(default_factory=list)
    session_id: Optional[str] = Field(default="default", description="Conversation id within tenant")

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