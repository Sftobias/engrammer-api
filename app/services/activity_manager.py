from sqlmodel import Session, select
from typing import Optional, List
from app.core.db import engine as default_engine
from app.models.db_models import Activity, ActivityQuestion
from app.models.schemas import ActivityDetail, QuestionDetail, ActivityInfo


class ActivityManager:
    
    def __init__(self, engine=default_engine):
        self.engine = engine
    
    # ---------- Conversores  ----------
    def _row_to_activityInfo(self, row: Activity) -> ActivityInfo:
        return ActivityInfo(
            id=row.activity_id,
            name=row.name,
            description=row.description,
        )
    
    def _row_to_activityDetail(self, row: Activity, questions: List[ActivityQuestion] = None) -> ActivityDetail:
        return ActivityDetail(
            id=row.activity_id,
            name=row.name,
            description=row.description,
            questions=[self._row_to_questionDetail(q) for q in (questions or [])],
        )
        
    def _row_to_questionDetail(self, row: ActivityQuestion) -> QuestionDetail:
        return QuestionDetail(
            id=row.question_id,
            activity_id=row.activity_id,
            contexto=row.contexto,
            pregunta=row.pregunta,
            respuesta_correcta=row.respuesta_correcta,
        )

    # ---------- Métodos públicos ----------
    def list_activities(self) -> List[ActivityInfo]:
        """Devuelve solo info básica de todas las actividades"""
        with Session(self.engine) as session:
            rows = session.exec(select(Activity)).all()
            return [self._row_to_activityInfo(r) for r in rows]

    def get_activity(self, activity_id: str) -> Optional[ActivityDetail]:
        """Devuelve la actividad con todas sus preguntas"""
        with Session(self.engine) as session:
            activity = session.get(Activity, activity_id)
            if not activity:
                return None
            questions = session.exec(
                select(ActivityQuestion).where(ActivityQuestion.activity_id == activity_id)
            ).all()
            return self._row_to_activityDetail(activity, questions)

    def get_questions_for_activity(self, activity_id: str) -> List[QuestionDetail]:
        with Session(self.engine) as session:
            rows = session.exec(
                select(ActivityQuestion).where(ActivityQuestion.activity_id == activity_id)
            ).all()
            return [self._row_to_questionDetail(r) for r in rows]

    def get_question(self, activity_id: str, question_id: str) -> Optional[QuestionDetail]:
        with Session(self.engine) as session:
            row = session.get(ActivityQuestion, (activity_id, question_id))
            return self._row_to_questionDetail(row) if row else None


ACTIVITIES = ActivityManager()
