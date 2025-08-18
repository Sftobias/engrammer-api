from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class TenantRow(SQLModel, table=True):

    tenant_id: str = Field(primary_key=True, index=True)

    name: Optional[str] = None
    email: Optional[str] = None

    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)