from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from models.common import HeatingMethod
from models.user import User

router = APIRouter()


@router.post("/", response_model=HeatingMethod)
def create_heating_method(*, session: Session = Depends(get_session), heating_method: HeatingMethod,
                          current_user: User = Depends(get_current_superuser)):
    session.add(heating_method)
    session.commit()
    session.refresh(heating_method)
    return heating_method


@router.get("/", response_model=List[HeatingMethod])
def read_heating_methods(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    methods = session.exec(select(HeatingMethod).offset(offset).limit(limit)).all()
    return methods


@router.get("/{method_id}", response_model=HeatingMethod)
def read_heating_method(*, session: Session = Depends(get_session), method_id: int):
    method = session.get(HeatingMethod, method_id)
    if not method:
        raise HTTPException(status_code=404, detail="Heating method not found")
    return method


@router.patch("/{method_id}", response_model=HeatingMethod)
def update_heating_method(
        *, session: Session = Depends(get_session), method_id: int, heating_method: HeatingMethod,
        current_user: User = Depends(get_current_superuser)
):
    db_method = session.get(HeatingMethod, method_id)
    if not db_method:
        raise HTTPException(status_code=404, detail="Heating method not found")

    method_data = heating_method.dict(exclude_unset=True)
    for key, value in method_data.items():
        setattr(db_method, key, value)

    session.add(db_method)
    session.commit()
    session.refresh(db_method)
    return db_method


@router.delete("/{method_id}")
def delete_heating_method(*, session: Session = Depends(get_session), method_id: int,
                          current_user: User = Depends(get_current_superuser)):
    method = session.get(HeatingMethod, method_id)
    if not method:
        raise HTTPException(status_code=404, detail="Heating method not found")

    session.delete(method)
    session.commit()
    return {"ok": True}
