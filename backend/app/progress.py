import anthropic
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analysis import generate_analysis
from app.db import get_db
from app.models import Assignment, MasteryScore, Submission, User, Topic
from app.dependencies import require_roles, get_current_user, ensure_can_view_student
from app.mastery import bucker_for_score
from app.roadmap import recommend_next_topic, reason_message

router = APIRouter(prefix="/progress", tags=["progress"])


def _topic_progress_rows(db: Session, student_id: int) -> list[dict]:
    rows = db.query(MasteryScore).filter(MasteryScore.student_id == student_id).all()
    topics = {t.id: t.name for t in db.query(Topic).all()}
    return [
        {
            "topic_id": r.topic_id,
            "topic_name": topics.get(r.topic_id, "?"),
            "score": r.score,
            "bucket": r.bucket,
            "trend": r.trend,
        }
        for r in rows
    ]


def _submission_rows(db: Session, student_id: int) -> list[dict]:
    submissions = (
        db.query(Submission)
        .filter(Submission.student_id == student_id)
        .order_by(Submission.graded_at)
        .all()
    )
    assignments = {a.id: a for a in db.query(Assignment).all()}
    topics = {t.id: t.name for t in db.query(Topic).all()}

    rows = []
    for s in submissions:
        assignment = assignments[s.assignment_id]
        rows.append({
            "id": s.id,
            "topic_id": assignment.topic_id,
            "topic_name": topics.get(assignment.topic_id, "?"),
            "assignment_id": s.assignment_id,
            "assignment_type": assignment.type,
            "score": s.score,
            "bucket": bucker_for_score(s.score) if s.score is not None else None,
            "feedback": s.feedback,
            "graded_at": s.graded_at,
            "status": s.status,
        })
    return rows

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
            "trend": r.trend,
        }
        for r in rows
    ]

@router.get("/{student_id}")
def student_progress(
    student_id: int, 
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ensure_can_view_student(user, student_id)
    return _topic_progress_rows(db, student_id)

@router.get("/{student_id}/next")
def next_topic_for_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ensure_can_view_student(user, student_id)

    recommendation = recommend_next_topic(db, student_id)
    topic = recommendation.topic

    return {
        "topic": {"id": topic.id, "name": topic.name} if topic else None,
        "reason": reason_message(recommendation),
    }

@router.get("/{student_id}/submissions")
def student_submissions(
    student_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ensure_can_view_student(user, student_id)
    return _submission_rows(db, student_id)

@router.post("/{student_id}/analysis")
def analyze_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ensure_can_view_student(user, student_id)

    student = db.get(User, student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    submissions = _submission_rows(db, student_id)
    if not submissions:
        return {"analysis": "No submissions yet — once this student turns in some work, an analysis will be available here."}

    topic_rows = _topic_progress_rows(db, student_id)
    recommendation_text = reason_message(recommend_next_topic(db, student_id))

    try:
        analysis = generate_analysis(student.name, topic_rows, submissions, recommendation_text)
    except anthropic.APIError:
        raise HTTPException(502, "Couldn't generate an analysis right now — please try again in a moment.")

    return {"analysis": analysis}