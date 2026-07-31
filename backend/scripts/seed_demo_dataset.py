"""Generates the full submission/mastery dataset for every demo student.

This is the final step in the seed chain (after seed_base, seed_submissions, and
seed_hardening) and the single authoritative source for grade history: it wipes and
rebuilds ALL submissions and mastery_scores, so re-running it always produces the same
clean result rather than layering more data on top of whatever's already there.

Why a wipe-and-rebuild instead of an additive script like the others: earlier ad-hoc
live testing (re-submitting the same MCQ nine times to demonstrate mastery recompute)
left several students with multiple submissions against the *same* assignment, which
doesn't reflect a real "submit once, get graded" flow. Cleaning that up by hand and
keeping every future re-seed clean means always starting from zero for these two
tables specifically.

Adds 13 more students on top of the ones seed_base/seed_hardening already created, for
24 total (8 per bucket), then gives every student exactly ONE submission per assignment
across however many topics their profile is meant to reach -- no student ever submits
to the same assignment twice. Does not call the Claude API; every score and feedback
string is directly authored, same convention as the other seed scripts.

Run once, after the other three seed scripts: python -m scripts.seed_demo_dataset
"""
import random

from app.db import SessionLocal
from app.mastery import recompute_mastery
from app.models import Assignment, MasteryScore, Submission, Topic, User
from app.security import hash_password
from scripts._seed_common import build_submission

random.seed(42)  # deterministic -- re-running produces the same dataset

NEW_STUDENTS = [
    ("Isabella Cruz", "isabella.cruz@test.com", "advanced"),
    ("Ryan Foster", "ryan.foster@test.com", "advanced"),
    ("Maya Singh", "maya.singh@test.com", "advanced"),
    ("Jordan Lee", "jordan.lee@test.com", "advanced"),
    ("Chloe Adams", "chloe.adams@test.com", "advanced"),
    ("Diego Ramirez", "diego.ramirez@test.com", "average"),
    ("Hannah Wright", "hannah.wright@test.com", "average"),
    ("Lucas Ferreira", "lucas.ferreira@test.com", "average"),
    ("Aiden Clarke", "aiden.clarke@test.com", "struggling"),
    ("Olivia Turner", "olivia.turner@test.com", "struggling"),
    ("Nathan Reed", "nathan.reed@test.com", "struggling"),
    ("Emma Collins", "emma.collins@test.com", "struggling"),
    ("Tyler Morgan", "tyler.morgan@test.com", "struggling"),
]

# Every student created by seed_base/seed_hardening gets a clean single-bucket profile
# here too -- e.g. Test Student and Liam Chen had mixed profiles from earlier ad-hoc
# testing, which wasn't a deliberate demo design, just another thing this cleans up.
EXISTING_STUDENT_BUCKETS = {
    "ava.martinez@test.com": "advanced",
    "zoe.bennett@test.com": "advanced",
    "marcus.webb@test.com": "advanced",
    "liam.chen@test.com": "average",
    "noah.patel@test.com": "average",
    "priya.sharma@test.com": "average",
    "ethan.brooks@test.com": "average",
    "student@test.com": "average",
    "sophia.kim@test.com": "struggling",
    "mason.rivera@test.com": "struggling",
    "grace.nguyen@test.com": "struggling",
}

# How many topics (counting from the root) each bucket's students progress through.
TOPIC_DEPTH_FOR_BUCKET = {"advanced": 5, "average": 3, "struggling": 2}
ESSAY_SCORE_RANGE = {"advanced": (0.85, 0.93), "average": (0.62, 0.74), "struggling": (0.20, 0.35)}
MCQ_CORRECT_FOR_BUCKET = {"advanced": True, "average": True, "struggling": False}


def main() -> None:
    db = SessionLocal()

    db.query(Submission).delete()
    db.query(MasteryScore).delete()
    db.commit()

    for name, email, _bucket in NEW_STUDENTS:
        if not db.query(User).filter(User.email == email).first():
            db.add(User(name=name, email=email, role="student", password_hash=hash_password("pass1234")))
    db.commit()

    all_students = dict(EXISTING_STUDENT_BUCKETS)
    all_students.update({email: bucket for _, email, bucket in NEW_STUDENTS})

    topics = db.query(Topic).order_by(Topic.id).all()
    assignments_for_topic = {}
    for a in db.query(Assignment).all():
        assignments_for_topic.setdefault(a.topic_id, []).append(a)

    touched_pairs = set()
    for email, bucket in all_students.items():
        student = db.query(User).filter(User.email == email).first()
        if student is None:
            continue  # a bucket entry with no matching account -- shouldn't happen, but don't crash the whole run
        depth = TOPIC_DEPTH_FOR_BUCKET[bucket]
        essay_lo, essay_hi = ESSAY_SCORE_RANGE[bucket]
        mcq_score = 1 if MCQ_CORRECT_FOR_BUCKET[bucket] else 0

        days_ago = 8 * depth
        for topic in topics[:depth]:  # topics ordered by id -- a valid prefix walk of the DAG
            # mcq first (older, smaller recency weight) so the tier-representative essay
            # score -- not a binary mcq=1 -- dominates recompute_mastery's weighted average
            ordered = sorted(assignments_for_topic.get(topic.id, []), key=lambda a: a.type != "mcq")
            for assignment in ordered:
                score = mcq_score if assignment.type == "mcq" else round(random.uniform(essay_lo, essay_hi), 2)
                db.add(build_submission(db, student.id, topic.id, assignment.id, assignment.type, score, days_ago))
                touched_pairs.add((student.id, topic.id))
                days_ago -= 2
            days_ago -= 4
    db.commit()

    for student_id, topic_id in touched_pairs:
        recompute_mastery(db, student_id, topic_id)

    print(f"Reset complete: {len(all_students)} students, {len(touched_pairs)} student/topic pairs recomputed.")


if __name__ == "__main__":
    main()