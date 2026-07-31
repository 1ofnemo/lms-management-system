from typing import NamedTuple

from sqlalchemy.orm import Session

from app.mastery import MASTERY_THRESHOLD
from app.models import MasteryScore, Topic


class Recommendation(NamedTuple):
    topic: Topic | None
    reason: str
    context_topic: Topic | None  # the other topic named in the reason text, if any


REASON_MESSAGES = {
    "on_track": "This is the next topic in your learning path.",
    "complete": "You've mastered every topic in the curriculum — great work!",
    "stuck": "There's nothing available to recommend right now — check with your teacher.",
}


def next_unlocked_topic(topics: list[Topic], mastered_topic_ids: set[int]) -> Topic | None:
    for topic in sorted(topics, key=lambda t: t.id):  # ties between simultaneously-unlocked topics go to the lowest id
        if topic.id in mastered_topic_ids:
            continue
        if all(prereq_id in mastered_topic_ids for prereq_id in topic.prerequisite_ids):
            return topic
    return None


def adjust_for_bucket(
    next_topic: Topic | None,
    trigger: MasteryScore | None,
    topics: list[Topic],
    mastered_topic_ids: set[int],
    mastery_scores: list[MasteryScore],
) -> Recommendation:
    if next_topic is None:
        if len(mastered_topic_ids) == len(topics):
            return Recommendation(None, "complete", None)
        return Recommendation(None, "stuck", None)  # e.g. a broken prerequisite chain locked everything

    if trigger is None:
        return Recommendation(next_topic, "on_track", None)

    if trigger.bucket == "advanced":
        next_topic_score = next((m for m in mastery_scores if m.topic_id == next_topic.id), None)
        next_topic_is_struggling = next_topic_score is not None and next_topic_score.bucket == "struggling"
        if not next_topic_is_struggling:
            # pretend next_topic is already mastered too, and see what that would unlock
            skip_target = next_unlocked_topic(topics, mastered_topic_ids | {next_topic.id})
            if skip_target:
                trigger_topic = next(t for t in topics if t.id == trigger.topic_id)
                return Recommendation(skip_target, "skip_ahead", trigger_topic)
        return Recommendation(next_topic, "on_track", None)

    if trigger.bucket == "struggling":
        struggling_scores = [m for m in mastery_scores if m.bucket == "struggling"]
        if struggling_scores:
            weakest = min(struggling_scores, key=lambda m: m.score)
            if weakest.topic_id != next_topic.id:  # only redirect if somewhere else is worse
                remedial_topic = next(t for t in topics if t.id == weakest.topic_id)
                return Recommendation(remedial_topic, "remedial", next_topic)
        return Recommendation(next_topic, "on_track", None)

    return Recommendation(next_topic, "on_track", None)  # average bucket: no adjustment


def reason_message(recommendation: Recommendation) -> str:
    reason, context_topic = recommendation.reason, recommendation.context_topic
    if reason == "skip_ahead":
        return f"Since you scored well on {context_topic.name}, we've skipped ahead to this topic."
    if reason == "remedial":
        return f"This is a weaker area for you, so we recommend reinforcing it before moving on to {context_topic.name}."
    return REASON_MESSAGES[reason]


def recommend_next_topic(db: Session, student_id: int) -> Recommendation:
    mastery_scores = db.query(MasteryScore).filter(MasteryScore.student_id == student_id).all()
    mastered_topic_ids = {m.topic_id for m in mastery_scores if m.score >= MASTERY_THRESHOLD}
    topics = db.query(Topic).all()

    next_topic = next_unlocked_topic(topics, mastered_topic_ids)
    if mastery_scores:
        trigger = max(mastery_scores, key=lambda m: m.updated_at)
    else:
        trigger = None

    return adjust_for_bucket(next_topic, trigger, topics, mastered_topic_ids, mastery_scores)