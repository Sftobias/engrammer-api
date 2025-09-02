from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints.tenants import router as tenants_router
from app.api.v1.endpoints.pipelines import router as pipelines_router
from app.api.v1.endpoints.historia import router as historia_router
from app.api.v1.endpoints.recuerdos import router as recuerdos_router
from app.utils.logging import configure_logging
from app.core.db import create_db_and_tables

configure_logging()
create_db_and_tables()

import sys
print(sys.path)

app = FastAPI(
    title="GraphRAG Pipelines API",
    version="1.0.0",
    description="Multi-tenant FastAPI service exposing GraphRAG pipelines as models"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenants_router, prefix="/v1", tags=["users"]) 
app.include_router(pipelines_router, prefix="/v1", tags=["pipelines"]) 
app.include_router(historia_router, prefix="/v1", tags=["historia"])
app.include_router(recuerdos_router, prefix="/v1", tags=["recuerdos"])

@app.get("/health", tags=["health"]) 
def health(): 
    return {"status": "ok"}

