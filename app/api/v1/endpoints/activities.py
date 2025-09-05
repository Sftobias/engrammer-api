from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.v1.deps import get_current_tenant_id
from app.services.activity_manager import ACTIVITIES
from app.models.schemas import ActivityInfo, ActivityDetail, ActivityInvokeRequest, InvokeResponse, QuestionDetail
from app.services.pipeline_registry import PIPELINES

router = APIRouter()

@router.get("/activities", response_model=List[ActivityInfo])
def list_activities():
    activities = ACTIVITIES.list_activities()
    return activities

@router.get("/activities/{activity_id}", response_model=ActivityDetail)
def get_activity(activity_id: str):
    activity = ACTIVITIES.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return activity

@router.get("/activities/{activity_id}/questions/{question_id}", response_model=QuestionDetail)
def get_question(activity_id: str, question_id: str):
    question = ACTIVITIES.get_question(activity_id, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return question

@router.post("/activities/{activity_id}/questions/{question_id}/invoke", response_model=InvokeResponse)
def invoke_pipeline(activity_id: str, question_id: str, req: ActivityInvokeRequest, tenant_id: str = Depends(get_current_tenant_id)):
    
    try:
        reg = PIPELINES.get("pipeline_historia")
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    session_id = activity_id + "__" + question_id

    pipeline_builder = reg.factory
    pipeline = pipeline_builder(tenant_id)
    output = pipeline.invoke(tenant_id, session_id, req.user_message, [m.model_dump() for m in req.messages])
    return InvokeResponse(output=output)
