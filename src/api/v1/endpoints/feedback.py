from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from models.common import Feedback
from models.user import User

router = APIRouter()


@router.post("/", response_model=Feedback)
def create_feedback(feedback: Feedback, session: Session = Depends(get_session)):
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


@router.get("/", response_model=List[Feedback])
def read_feedbacks(
        session: Session = Depends(get_session),
        skip: int = 0,
        limit: int = Query(default=100, le=100),
        current_user: User = Depends(get_current_superuser)
):
    feedbacks = session.exec(select(Feedback).offset(skip).limit(limit)).all()
    return feedbacks


@router.get("/{feedback_id}", response_model=Feedback)
def read_feedback(feedback_id: int, session: Session = Depends(get_session),
                  current_user: User = Depends(get_current_superuser)):
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.put("/{feedback_id}", response_model=Feedback)
def update_feedback(
        feedback_id: int,
        feedback_update: Feedback,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_superuser)
):
    db_feedback = session.get(Feedback, feedback_id)
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    feedback_data = feedback_update.dict(exclude_unset=True)
    for key, value in feedback_data.items():
        setattr(db_feedback, key, value)

    session.add(db_feedback)
    session.commit()
    session.refresh(db_feedback)
    return db_feedback


@router.delete("/{feedback_id}")
def delete_feedback(feedback_id: int, session: Session = Depends(get_session),
                    current_user: User = Depends(get_current_superuser)):
    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    session.delete(feedback)
    session.commit()
    return {"message": "Feedback deleted successfully"}
