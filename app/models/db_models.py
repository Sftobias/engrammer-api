from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class TenantRow(SQLModel, table=True):
    tenant_id: str = Field(primary_key=True, index=True)
    name: Optional[str] = None
    email: Optional[str] = None

    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Activity(SQLModel, table=True):
    # __allow_unmapped__ = True 

    activity_id: str = Field(primary_key=True, index=True)
    name: str
    description: Optional[str] = None

class ActivityQuestion(SQLModel, table=True):
    # __allow_unmapped__ = True

    activity_id: str = Field(foreign_key="activity.activity_id", primary_key=True)
    question_id: str = Field(primary_key=True)

    contexto: Optional[str] = None
    pregunta: str
    respuesta_correcta: str
