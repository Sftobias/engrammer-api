from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import InvokeRequest, InvokeResponse, PipelinesList, PipelineInfo, EndConversationRequest, EndConversationResponse
from app.services.pipeline_registry import PIPELINES, RegisteredPipeline
from app.pipelines.pipeline_guardar import pipeline_guardar_factory, PipelineGuardar
from app.pipelines.pipeline_preguntas import PipelinePreguntas, pipeline_preguntas_factory
from app.pipelines.pipeline_recuperar import PipelineRecuperar, pipeline_recuperar_factory
from app.api.v1.deps import get_current_tenant_id

router = APIRouter()

@router.post("/memories/invoke", response_model=InvokeResponse)
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

@router.post("/memories/end", response_model=EndConversationResponse)
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