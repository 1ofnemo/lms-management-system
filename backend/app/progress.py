from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import MasteryScore, User, Topic
from app.dependencies import require_roles

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("", dependencies=[Depends(require_roles("teacher", "admin"))])
def class_progress(db: Session = Depends(get_db)):
    rows = db.query(MasteryScore).all()
    students = {u.id: u.name for u in db.query(User).filter(User.role == "student")}
    topics = {t.id: t.name for t in db.query(Topic).all()}

    return [
        {
            "student_id": r.student_id,
            "student_name": students.get(r.student_id, "?"),
            "topic_id": r.topic_id,
            "topic_name": topics.get(r.topic_id, "?"),
            "score": r.score,
            "bucket": r.bucket,
        }
        for r in rows
    ]