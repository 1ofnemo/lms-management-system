from sqlalchemy.orm import Session

from app.models import Assignment, MasteryScore, Submission

RECENT_SCORES_LIMIT = 5
TREND_THRESHOLD = 0.05
ADVANCED_THRESHOLD = 0.85
MASTERY_THRESHOLD = 0.6  # "good enough to move on" — also used by roadmap.py to decide what's unlocked


def bucker_for_score(score: float) -> str:
    if score >= ADVANCED_THRESHOLD:
        return "advanced"
    if score >= MASTERY_THRESHOLD:
        return "average"
    return "struggling"

def trend_for_recent(scores: list[float]) -> str:
    if len(scores) < 2:
        return "flat"
    recent = scores[:3]
    delta = recent[0] - recent[-1]
    if delta > TREND_THRESHOLD:
        return "rising"
    if delta < -TREND_THRESHOLD:
        return "falling"
    return "flat"

def recompute_mastery (db: Session, student_id: int, topic_id: int) -> None:
    recent = (
        db.query(Submission)
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .filter(
            Assignment.topic_id == topic_id,
            Submission.student_id == student_id,
            Submission.score.isnot(None),
        )
        .order_by(Submission.graded_at.desc())
        .limit(RECENT_SCORES_LIMIT)
        .all()
    )
    if not recent:
        return

    weights = list(range(len(recent), 0, -1))
    weighted_score = sum((s.score or 0) * w for s, w in zip(recent, weights)) / sum(weights)
    bucket = bucker_for_score(weighted_score)
    trend = trend_for_recent([s.score for s in recent if s.score is not None])
    mastery = (
        db.query(MasteryScore)
        .filter(
            MasteryScore.student_id == student_id,
            MasteryScore.topic_id == topic_id,
        )
        .first()
    )
    if mastery:
        mastery.score = weighted_score
        mastery.bucket = bucket
        mastery.trend = trend
    else:
        mastery = MasteryScore(
            student_id=student_id,
            topic_id=topic_id,
            score=weighted_score,
            bucket=bucket,
            trend=trend,
        )
        db.add(mastery)

    db.commit()