from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy import Integer, ForeignKey, Text, ForeignKey, Float, DateTime, UniqueConstraint, func
from datetime import datetime

from app.db import Base

#for users in db
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    role: Mapped[str]  # student | teacher | admin

#for topics in db
class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    prerequisite_ids: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, server_default="{}"
    )

#for assignments in db
class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    type: Mapped[str] #essay, mcq, etc
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    rubric: Mapped[dict] = mapped_column(JSONB, nullable=False)

#for MasteryScore model
class MasteryScore(Base):
    __tablename__ = "mastery_scores"
    __table_args__ = (UniqueConstraint("student_id", "topic_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    bucket: Mapped[str] = mapped_column(nullable=False)  # advanced | average | struggling
    trend: Mapped[str] = mapped_column(nullable=False, server_default="flat")  # rising | falling | flat
    updated_at: Mapped[datetime] = mapped_column (
        DateTime, server_default=func.now(), onupdate=func.now()
    )

class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, server_default="pending")
