from typing import List

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from core.s3 import object_storage
from models.common import Category
from models.response import CategoryResponse
from models.user import User

router = APIRouter()


@router.post("/", response_model=Category)
def create_category(
        *,
        session: Session = Depends(get_session),
        category: Category,
        current_user: User = Depends(get_current_superuser),
):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/", response_model=List[CategoryResponse])
def read_categories(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    categories = session.exec(select(Category).offset(offset).limit(limit)).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(*, session: Session = Depends(get_session), category_id: int):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=Category)
def update_category(
        *,
        session: Session = Depends(get_session),
        category_id: int,
        category: Category,
        current_user: User = Depends(get_current_superuser),
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
def delete_category(
        *,
        session: Session = Depends(get_session),
        category_id: int,
        current_user: User = Depends(get_current_superuser),
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"ok": True}


@router.post("/{category_id}/icon")
async def upload_category_icon(
        *,
        session: Session = Depends(get_session),
        category_id: int,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_superuser),
):
    """카테고리 아이콘 SVG 업로드"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # 기존 이미지가 있다면 삭제
    if category.icon_url:
        key = category.icon_url.split('/')[-1]
        object_storage.delete_image(key)

    # 새 이미지 업로드
    result = await object_storage.upload_image(file, folder="categories")
    if not result:
        raise HTTPException(status_code=400, detail="Failed to upload image")

    # DB 업데이트
    category.icon_url = result["url"]
    session.add(category)
    session.commit()
    session.refresh(category)

    return {"icon_url": category.icon_url}


@router.delete("/{category_id}/icon")
async def delete_category_icon(
        *,
        session: Session = Depends(get_session),
        category_id: int,
        current_user: User = Depends(get_current_superuser),
):
    """카테고리 아이콘 삭제"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if not category.icon_url:
        raise HTTPException(status_code=404, detail="Icon not found")

    # Object Storage에서 이미지 삭제
    key = category.icon_url.split('/')[-1]
    if object_storage.delete_image(key):
        category.icon_url = None
        session.add(category)
        session.commit()
        return {"message": "Icon deleted successfully"}

    raise HTTPException(status_code=500, detail="Failed to delete icon")
