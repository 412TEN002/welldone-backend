from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select, Session

from api.v1.deps import get_session
from models.common import Timer

router = APIRouter()


@router.post("/", response_model=Timer)
def create_timer(timer: Timer, session: Session = Depends(get_session)):
    session.add(timer)
    session.commit()
    session.refresh(timer)
    return timer


@router.get("/", response_model=List[Timer])
def read_timers(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
):
    timers = session.exec(select(Timer).offset(skip).limit(limit)).all()
    return timers


@router.get("/{timer_id}", response_model=Timer)
def read_timer(timer_id: int, session: Session = Depends(get_session)):
    timer = session.get(Timer, timer_id)
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")
    return timer


@router.put("/{timer_id}", response_model=Timer)
def update_timer(
    timer_id: int, timer_update: Timer, session: Session = Depends(get_session)
):
    db_timer = session.get(Timer, timer_id)
    if not db_timer:
        raise HTTPException(status_code=404, detail="Timer not found")

    timer_data = timer_update.dict(exclude_unset=True)
    for key, value in timer_data.items():
        setattr(db_timer, key, value)

    session.add(db_timer)
    session.commit()
    session.refresh(db_timer)
    return db_timer


@router.delete("/{timer_id}")
def delete_timer(timer_id: int, session: Session = Depends(get_session)):
    timer = session.get(Timer, timer_id)
    if not timer:
        raise HTTPException(status_code=404, detail="Timer not found")

    session.delete(timer)
    session.commit()
    return {"message": "Timer deleted successfully"}
