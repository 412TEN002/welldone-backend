from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from models.common import TimerFeedback, IngredientRequestFeedback
from models.user import User

router = APIRouter()


@router.post("/timer-feedback", response_model=TimerFeedback)
def create_feedback(
    timer_feedback: TimerFeedback, session: Session = Depends(get_session)
):
    session.add(timer_feedback)
    session.commit()
    session.refresh(timer_feedback)
    return timer_feedback


@router.get("/timer-feedback", response_model=List[TimerFeedback])
def read_feedbacks(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    current_user: User = Depends(get_current_superuser),
):
    feedbacks = session.exec(select(TimerFeedback).offset(skip).limit(limit)).all()
    return feedbacks


@router.get("/timer-feedback/{timer_feedback_id}", response_model=TimerFeedback)
def read_feedback(
    timer_feedback_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_superuser),
):
    feedback = session.get(TimerFeedback, timer_feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.delete("/timer-feedback/{timer_feedback_id}")
def delete_feedback(
    timer_feedback_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_superuser),
):
    feedback = session.get(TimerFeedback, timer_feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    session.delete(feedback)
    session.commit()
    return {"message": "Feedback deleted successfully"}


@router.post("/ingredient-request-feedback", response_model=IngredientRequestFeedback)
def create_ingredient_request_feedback(
    ingredient_request_feedback: IngredientRequestFeedback,
    session: Session = Depends(get_session),
):
    session.add(ingredient_request_feedback)
    session.commit()
    session.refresh(ingredient_request_feedback)
    return ingredient_request_feedback


@router.get(
    "/ingredient-request-feedback", response_model=List[IngredientRequestFeedback]
)
def read_ingredient_request_feedbacks(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    current_user: User = Depends(get_current_superuser),
):
    feedbacks = session.exec(
        select(IngredientRequestFeedback).offset(skip).limit(limit)
    ).all()
    return feedbacks


@router.get(
    "/ingredient-request-feedback/{ingredient_request_feedback_id}",
    response_model=IngredientRequestFeedback,
)
def read_ingredient_request_feedback(
    ingredient_request_feedback_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_superuser),
):
    feedback = session.get(IngredientRequestFeedback, ingredient_request_feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.delete("/ingredient-request-feedback/{ingredient_request_feedback_id}")
def delete_ingredient_request_feedback(
    ingredient_request_feedback_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_superuser),
):
    feedback = session.get(IngredientRequestFeedback, ingredient_request_feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    session.delete(feedback)
    session.commit()
    return {"message": "Feedback deleted successfully"}
