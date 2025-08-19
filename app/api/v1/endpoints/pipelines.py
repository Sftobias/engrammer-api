from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import InvokeRequest, InvokeResponse, PipelinesList, PipelineInfo, EndConversationRequest, EndConversationResponse
from app.services.pipeline_registry import PIPELINES, RegisteredPipeline
from app.pipelines.pipeline_guardar import pipeline_guardar_factory, PipelineGuardar
from app.pipelines.pipeline_preguntas import PipelinePreguntas, pipeline_preguntas_factory
from app.pipelines.pipeline_recuperar import PipelineRecuperar, pipeline_recuperar_factory
from app.api.v1.deps import get_current_tenant_id

# Register pipelines on import
PIPELINES.register(RegisteredPipeline(
    id=PipelinePreguntas.id,
    name=PipelinePreguntas.name,
    description=PipelinePreguntas.description,
    factory=pipeline_preguntas_factory(),
))

PIPELINES.register(RegisteredPipeline(
    id=PipelineGuardar.id,
    name=PipelineGuardar.name,
    description=PipelineGuardar.description,
    factory=pipeline_guardar_factory(),
))

PIPELINES.register(RegisteredPipeline(
    id=PipelineRecuperar.id,
    name=PipelineRecuperar.name,
    description=PipelineRecuperar.description,
    factory=pipeline_recuperar_factory(),
))

router = APIRouter()

@router.get("/pipelines", response_model=PipelinesList)
def list_pipelines():
    data = [PipelineInfo(id=p.id, name=p.name, description=p.description) for p in PIPELINES.list()]
    return {"data": data}

@router.post("/pipelines/invoke", response_model=InvokeResponse)
def invoke_pipeline(
    req: InvokeRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):
    
    try:
        reg = PIPELINES.get(req.pipeline_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    pipeline_builder = reg.factory
    pipeline = pipeline_builder(tenant_id)
    output = pipeline.invoke(tenant_id, req.session_id or "default", req.user_message, [m.model_dump() for m in req.messages])
    return InvokeResponse(output=output)

@router.post("/pipelines/end", response_model=EndConversationResponse)
def end_conversation(
    req: EndConversationRequest,
    tenant_id: str = Depends(get_current_tenant_id)
):

    try:
        reg = PIPELINES.get(req.pipeline_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    pipeline_builder = reg.factory
    pipeline = pipeline_builder(tenant_id)
    message = pipeline.finalizar_conversacion(tenant_id, req.session_id or "default")
    return EndConversationResponse(message=message)