from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Topic
from app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/topics", tags=["topics"])

class TopicIn(BaseModel):
    name: str
    prerequisite_ids: list[int] = []

class TopicOut(BaseModel):
    id: int
    name: str
    prerequisite_ids: list[int]

    class Config:
        from_attributes = True


@router.get("", response_model=list[TopicOut], dependencies=[Depends(get_current_user)])
def list_topics(db: Session = Depends(get_db)):
    return db.query(Topic).all()


@router.post("", response_model=TopicOut, dependencies=[Depends(require_roles("teacher", "admin"))])
def create_topic(body: TopicIn, db: Session = Depends(get_db)):
    topic = Topic(**body.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/{topic_id}", response_model=TopicOut, dependencies=[Depends(get_current_user)])
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found!")
    return topic


@router.put("/{topic_id}", response_model=TopicOut, dependencies=[Depends(require_roles("teacher", "admin"))])
def update_topic(topic_id: int, body: TopicIn, db: Session = Depends(get_db)):
    topic = db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found!")
    topic.name = body.name
    topic.prerequisite_ids = body.prerequisite_ids
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/{topic_id}", status_code=204, dependencies=[Depends(require_roles("teacher", "admin"))])
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found!")
    db.delete(topic)
    db.commit()