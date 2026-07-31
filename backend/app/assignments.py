from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Assignment
from app.dependencies import require_roles, get_current_user

router = APIRouter(prefix="/assignments", tags=["assignments"])

class AssignmentIn(BaseModel):
    topic_id: int
    type: str
    prompt: str
    rubric: dict

    @field_validator("rubric") #validation to ensure rubric criterion only + up to 1.0 
    @classmethod
    def validate_rubric(cls, rubric, info):
        if info.data.get("type") == "mcq":
            options = rubric.get("options", [])
            correct_answer = rubric.get("correct_answer")
            if len(options) < 2:
                raise ValueError("Multiple choice questions rubric must include at least 2 options.")
            if correct_answer not in options:
                raise ValueError("Correct answer must be one of the listed options")
        else:
            total = sum(c.get("weight", 0) for c in rubric.get("criteria", []))
            if abs(total-1) > 0.01:
                raise ValueError(f"Rubric weights must sum up to 1, but got {total} instead")
        return rubric
                


class AssignmentOut(BaseModel):
    id: int
    topic_id: int
    type: str
    prompt: str
    rubric: dict

    class Config: 
        from_attributes = True


@router.get("", response_model=list[AssignmentOut], dependencies=[Depends(get_current_user)])
def list_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).all()


@router.post("", response_model=AssignmentOut, dependencies=[Depends(require_roles("teacher", "admin"))])
def create_assignment(body: AssignmentIn, db: Session = Depends(get_db)):
    assignment = Assignment(**body.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/{assignment_id}", response_model=AssignmentOut, dependencies=[Depends(get_current_user)])
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentOut, dependencies=[Depends(require_roles("teacher", "admin"))])
def update_assignment(assignment_id: int, body: AssignmentIn, db: Session = Depends(get_db)):
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    for field, value in body.model_dump().items():
        setattr(assignment, field, value)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=204, dependencies=[Depends(require_roles("teacher", "admin"))])
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    db.delete(assignment)
    db.commit()