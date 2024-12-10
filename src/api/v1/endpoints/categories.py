from typing import List

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from api.v1.deps import SessionDep
from models.common import Category

router = APIRouter()


@router.post("/", response_model=Category)
def create_category(*, session: SessionDep, category: Category):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/", response_model=List[Category])
def read_categories(
        *,
        session: SessionDep,
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    categories = session.exec(select(Category).offset(offset).limit(limit)).all()
    return categories


@router.get("/{category_id}", response_model=Category)
def read_category(*, session: SessionDep, category_id: int):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=Category)
def update_category(
        *, session: SessionDep, category_id: int, category: Category
):
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = category.dict(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)

    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.delete("/{category_id}")
def delete_category(*, session: SessionDep, category_id: int):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"ok": True}
