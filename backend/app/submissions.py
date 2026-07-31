from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Assignment, Submission, User
from app.dependencies import require_roles
from app.grading import grade_submission_with_retry
from app.extraction import extract_text
from app.mastery import recompute_mastery

router = APIRouter(prefix="/submissions", tags=["submissions"])

class SubmissionOut(BaseModel):
    id: int
    student_id: int
    assignment_id: int
    answer: str
    score: float | None
    feedback: dict | None
    graded_at: datetime | None
    status: str

    class Config:
        from_attributes = True

class SubmissionListOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    assignment_id: int
    assignment_prompt: str
    answer: str
    score: float | None
    feedback: dict | None
    graded_at: datetime | None
    status: str

class SubmissionOverride(BaseModel):
    score: float
    feedback: dict


@router.post("", response_model=SubmissionOut)
def create_submission(
    assignment_id: int = Form(...),
    answer: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles("student")),
):
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    if not answer and not file: 
        raise HTTPException(400, "Please provide either an answer or a file")
    if answer and file:
        raise HTTPException(400, "Provide either an answer or a file, not both")
    if assignment.type =="mcq" and file:
        raise HTTPException(400, "MCQ assignments don't accept file uploads")
    if file:
        answer = extract_text(file)

    submission = Submission(student_id=user["id"], assignment_id=assignment_id, answer=answer)

    assert answer is not None
    if assignment.type == "mcq":
        correct = assignment.rubric.get("correct_answer")
        is_correct = answer.strip() == str(correct).strip()
        submission.score = 1.0 if is_correct else 0.0
        submission.feedback = {
            "criterion_scores": [{"criterion": "Correct answer", "score": submission.score}],
            "total": submission.score,
            "strengths": ["Correct answer selected"] if is_correct else [],
            "gaps": [] if is_correct else [f"Correct answer was: {correct}"],
            "next_step": "" if is_correct else "Review this topic and try again.",
        }
        submission.graded_at = datetime.now(timezone.utc)
        submission.status = "graded"
    else:
        result = grade_submission_with_retry(assignment.prompt, assignment.rubric, answer)
        if result is None:
            submission.status = "needs_manual_review"
        else:
            submission.score = result["total"]
            submission.feedback = result
            submission.graded_at = datetime.now(timezone.utc)
            submission.status = "graded"
    db.add(submission)
    db.commit()
    db.refresh(submission)
    if submission.status == "graded":
        recompute_mastery(db, submission.student_id, assignment.topic_id)
    return submission

@router.get(
    "", 
    response_model=list[SubmissionListOut],
    dependencies=[Depends(require_roles("teacher", "admin"))],
)
def list_submissions(db: Session = Depends(get_db)):
    submissions = db.query(Submission).all()
    students = {u.id: u.name for u in db.query(User).filter(User.role =="student")}
    assignments = {a.id: a.prompt for a in db.query(Assignment).all()}

    return [
        {
            "id": s.id,
            "student_id": s.student_id,
            "student_name": students.get(s.student_id, "?"),
            "assignment_id": s.assignment_id,
            "assignment_prompt": assignments.get(s.assignment_id, "?"),
            "answer": s.answer,
            "score": s.score,
            "feedback": s.feedback,
            "graded_at": s.graded_at,
            "status": s.status,
        }
        for s in submissions
    ]

@router.patch(
    "/{submission_id}",
    response_model=SubmissionOut,
    dependencies=[Depends(require_roles("teacher", "admin"))]
)
def override_submission(
    submission_id: int, body: SubmissionOverride, db: Session = Depends(get_db)
):
    submission = db.get(Submission, submission_id)
    if not submission: 
        raise HTTPException(404, "Submission not found")

    assignment = db.get(Assignment, submission.assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")

    submission.score = body.score
    submission.feedback = body.feedback
    submission.graded_at = datetime.now(timezone.utc)
    submission.status = "graded"

    db.commit()
    db.refresh(submission)
    recompute_mastery(db, submission.student_id, assignment.topic_id)
    return submission