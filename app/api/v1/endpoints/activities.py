from fastapi import APIRouter, HTTPException
from typing import List
from app.services.activity_manager import ACTIVITIES
from app.models.schemas import ActivityInfo, ActivityDetail, QuestionDetail

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
