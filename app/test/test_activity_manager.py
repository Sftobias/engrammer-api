import pytest
from sqlmodel import SQLModel, create_engine, Session
from app.models.db_models import Activity, ActivityQuestion
from app.services.activity_manager import ActivityManager


@pytest.fixture
def engine():
    # BBDD temporal en memoria
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def manager(engine):
    return ActivityManager(engine=engine)


@pytest.fixture
def sample_data(session):
    """Insertamos datos de ejemplo"""
    act1 = Activity(activity_id="A1", name="Actividad 1", description="Desc 1")
    act2 = Activity(activity_id="A2", name="Actividad 2")
    q1 = ActivityQuestion(question_id="Q1", activity_id="A1", pregunta="¿Pregunta 1?", respuesta_correcta="Sí")
    q2 = ActivityQuestion(question_id="Q2", activity_id="A1", pregunta="¿Pregunta 2?", respuesta_correcta="No")
    session.add_all([act1, act2, q1, q2])
    session.commit()


# ---------- TESTS ----------
def test_list_activities(manager, session, sample_data):
    acts = manager.list_activities()
    assert len(acts) == 2
    assert acts[0].id == "A1"
    assert acts[1].name == "Actividad 2"


def test_get_activity_with_questions(manager, session, sample_data):
    act = manager.get_activity("A1")
    assert act is not None
    assert act.id == "A1"
    assert len(act.questions) == 2
    assert act.questions[0].pregunta == "¿Pregunta 1?"


def test_get_questions_for_activity(manager, session, sample_data):
    qs = manager.get_questions_for_activity("A1")
    assert len(qs) == 2
    assert qs[1].respuesta_correcta == "No"


def test_get_question(manager, session, sample_data):
    q = manager.get_question("A1", "Q2")
    assert q is not None
    assert q.id == "Q2"
    assert q.pregunta == "¿Pregunta 2?"
