from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from models.common import CookingMethod
from models.user import User

router = APIRouter()


@router.post("/", response_model=CookingMethod)
def create_cooking_method(*, session: Session = Depends(get_session), cooking_method: CookingMethod,
                          current_user: User = Depends(get_current_superuser)):
    session.add(cooking_method)
    session.commit()
    session.refresh(cooking_method)
    return cooking_method


@router.get("/", response_model=List[CookingMethod])
def read_cooking_methods(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    methods = session.exec(select(CookingMethod).offset(offset).limit(limit)).all()
    return methods


@router.get("/{method_id}", response_model=CookingMethod)
def read_cooking_method(*, session: Session = Depends(get_session), method_id: int):
    method = session.get(CookingMethod, method_id)
    if not method:
        raise HTTPException(status_code=404, detail="Cooking method not found")
    return method


@router.patch("/{method_id}", response_model=CookingMethod)
def update_cooking_method(
        *, session: Session = Depends(get_session), method_id: int, cooking_method: CookingMethod,
        current_user: User = Depends(get_current_superuser)
):
    db_method = session.get(CookingMethod, method_id)
    if not db_method:
        raise HTTPException(status_code=404, detail="Cooking method not found")

    method_data = cooking_method.dict(exclude_unset=True)
    for key, value in method_data.items():
        setattr(db_method, key, value)

    session.add(db_method)
    session.commit()
    session.refresh(db_method)
    return db_method


@router.delete("/{method_id}")
def delete_cooking_method(*, session: Session = Depends(get_session), method_id: int,
                          current_user: User = Depends(get_current_superuser)):
    method = session.get(CookingMethod, method_id)
    if not method:
        raise HTTPException(status_code=404, detail="Cooking method not found")

    session.delete(method)
    session.commit()
    return {"ok": True}
