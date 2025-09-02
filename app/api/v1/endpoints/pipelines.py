from fastapi import APIRouter
from app.models.schemas import PipelinesList, PipelineInfo
from app.services.pipeline_registry import PIPELINES, RegisteredPipeline
from app.pipelines.pipeline_guardar import pipeline_guardar_factory, PipelineGuardar
from app.pipelines.pipeline_preguntas import PipelinePreguntas, pipeline_preguntas_factory
from app.pipelines.pipeline_recuperar import PipelineRecuperar, pipeline_recuperar_factory

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