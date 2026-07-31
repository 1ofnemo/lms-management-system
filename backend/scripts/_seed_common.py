"""Shared helpers for the one-off seed/backfill scripts in this directory (not part of the running app)."""
from datetime import datetime, timedelta, timezone

from app.mastery import ADVANCED_THRESHOLD, MASTERY_THRESHOLD
from app.models import Assignment, Submission

ESSAY_RUBRIC = {
    "criteria": [
        {"criterion": "Correct answer", "weight": 0.4},
        {"criterion": "Shows work", "weight": 0.4},
        {"criterion": "Explanation clarity", "weight": 0.2},
    ]
}

STRONG_FEEDBACK = {
    "strengths": ["Shows clear step-by-step work", "Correct final answer", "Explanation is easy to follow"],
    "gaps": [],
    "next_step": "Try a slightly harder problem in this topic.",
}
MIXED_FEEDBACK = {
    "strengths": ["Correct final answer"],
    "gaps": ["Work could be shown more explicitly"],
    "next_step": "Practice writing out each algebra step before solving.",
}
WEAK_FEEDBACK = {
    "strengths": [],
    "gaps": ["Final answer is incorrect", "Reasoning steps are unclear"],
    "next_step": "Review the worked examples for this topic before trying again.",
}


def feedback_for_essay_score(score: float) -> dict:
    if score >= ADVANCED_THRESHOLD:
        return STRONG_FEEDBACK
    if score >= MASTERY_THRESHOLD:
        return MIXED_FEEDBACK
    return WEAK_FEEDBACK


def build_submission(db, student_id: int, topic_id: int, assignment_id: int, assignment_type: str, score: float, days_ago: int) -> Submission:
    if assignment_type == "mcq":
        rubric = db.get(Assignment, assignment_id).rubric
        answer = rubric["correct_answer"] if score == 1 else "wrong answer"
        feedback = {
            "criterion_scores": [{"criterion": "Correct answer", "score": score}],
            "total": score,
            "strengths": ["Correct answer selected"] if score else [],
            "gaps": [] if score else [f"Correct answer was: {rubric['correct_answer']}"],
            "next_step": "" if score else "Review this topic and try again.",
        }
    else:
        answer = f"[backfilled essay response for topic {topic_id}]"
        feedback = feedback_for_essay_score(score)

    return Submission(
        student_id=student_id,
        assignment_id=assignment_id,
        answer=answer,
        score=score,
        feedback=feedback,
        graded_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
        status="graded",
    )