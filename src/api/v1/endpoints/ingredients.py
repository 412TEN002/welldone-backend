from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from models.common import Ingredient, IngredientNutritionLink, NutritionTag
from models.response import IngredientResponse
from models.user import User
from utils.utils import is_chosung

router = APIRouter()


@router.get("/search", response_model=List[IngredientResponse])
def search_ingredients(
    *,
    session: Session = Depends(get_session),
    keyword: str = Query(..., min_length=1),
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(default=100, lte=100),
):
    """
    재료를 검색합니다.
    - 일반 검색과 초성 검색을 모두 지원합니다.
    - 카테고리로 필터링할 수 있습니다.
    """
    query = select(Ingredient)

    # 검색어 처리
    if keyword:
        if is_chosung(keyword):
            # DB에 저장된 초성 정보를 이용해 검색
            query = query.where(Ingredient.chosung.contains(keyword))
        else:
            # 일반 검색어는 이름으로 검색
            query = query.where(Ingredient.name.contains(keyword))

    # 카테고리 필터링
    if category_id is not None:
        query = query.where(Ingredient.category_id == category_id)

    # 페이지네이션 적용
    query = query.offset(skip).limit(limit)

    return session.exec(query).all()


@router.post("/", response_model=Ingredient)
def create_ingredient(
    *,
    session: Session = Depends(get_session),
    ingredient: Ingredient,
    current_user: User = Depends(get_current_superuser),
):
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)
    return ingredient


@router.get("/", response_model=List[IngredientResponse])
def read_ingredients(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    ingredients = session.exec(select(Ingredient).offset(offset).limit(limit)).all()
    return ingredients


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def read_ingredient(*, session: Session = Depends(get_session), ingredient_id: int):
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.patch("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    *,
    session: Session = Depends(get_session),
    ingredient_id: int,
    ingredient: Ingredient,
    current_user: User = Depends(get_current_superuser),
):
    db_ingredient = session.get(Ingredient, ingredient_id)
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    ingredient_data = ingredient.dict(exclude_unset=True)
    for key, value in ingredient_data.items():
        setattr(db_ingredient, key, value)

    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient


@router.delete("/{ingredient_id}")
def delete_ingredient(
    *,
    session: Session = Depends(get_session),
    ingredient_id: int,
    current_user: User = Depends(get_current_superuser),
):
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    session.delete(ingredient)
    session.commit()
    return {"ok": True}


@router.post("/{ingredient_id}/tags/{tag_id}")
def add_nutrition_tag(
    *,
    session: Session = Depends(get_session),
    ingredient_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_superuser),
):
    # 재료 확인
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # 태그 확인
    tag = session.get(NutritionTag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Nutrition tag not found")

    # 현재 태그 수 확인
    current_tags = session.exec(
        select(IngredientNutritionLink).where(
            IngredientNutritionLink.ingredient_id == ingredient_id
        )
    ).all()

    if len(current_tags) >= 3:
        raise HTTPException(
            status_code=400, detail="Maximum number of nutrition tags (3) reached"
        )

    # 이미 존재하는 태그인지 확인
    existing_link = session.exec(
        select(IngredientNutritionLink).where(
            IngredientNutritionLink.ingredient_id == ingredient_id,
            IngredientNutritionLink.nutrition_tag_id == tag_id,
        )
    ).first()

    if existing_link:
        raise HTTPException(
            status_code=400,
            detail="This nutrition tag is already added to the ingredient",
        )

    # 새 태그 연결 추가
    link = IngredientNutritionLink(ingredient_id=ingredient_id, nutrition_tag_id=tag_id)
    session.add(link)
    session.commit()

    return {"ok": True}


@router.delete("/{ingredient_id}/tags/{tag_id}")
def remove_nutrition_tag(
    *,
    session: Session = Depends(get_session),
    ingredient_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_superuser),
):
    # 연결 확인
    link = session.exec(
        select(IngredientNutritionLink).where(
            IngredientNutritionLink.ingredient_id == ingredient_id,
            IngredientNutritionLink.nutrition_tag_id == tag_id,
        )
    ).first()

    if not link:
        raise HTTPException(
            status_code=404, detail="Nutrition tag not found for this ingredient"
        )

    # 연결 삭제
    session.delete(link)
    session.commit()

    return {"ok": True}


@router.get("/{ingredient_id}/tags", response_model=List[NutritionTag])
def read_ingredient_nutrition_tags(
    *, session: Session = Depends(get_session), ingredient_id: int
):
    # 재료 확인
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # 연결된 태그 조회
    return ingredient.nutrition_tags
