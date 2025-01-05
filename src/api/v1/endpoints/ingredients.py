from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from sqlalchemy import func
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from core.s3 import object_storage
from models.common import Ingredient, IngredientNutritionLink, NutritionTag, CookingTool, CookingSetting
from models.response import IngredientResponse, IngredientSearchResponse, CookingToolResponse, IngredientListResponse
from models.user import User
from utils.utils import is_chosung

router = APIRouter()


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


@router.get("/search", response_model=List[IngredientSearchResponse])
def search_ingredients(
        *,
        session: Session = Depends(get_session),
        keyword: str = Query(..., min_length=1),
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = Query(default=100, lte=100),
):
    query = select(Ingredient)

    if keyword:
        if is_chosung(keyword):
            query = query.where(Ingredient.chosung.contains(keyword))
        else:
            query = query.where(Ingredient.name.contains(keyword))

    if category_id is not None:
        query = query.where(Ingredient.category_id == category_id)

    query = query.offset(skip).limit(limit)
    ingredients = session.exec(query).all()

    # DB에 저장된 URL들을 그대로 사용
    return [IngredientSearchResponse.model_validate(ingredient) for ingredient in ingredients]


@router.get("/", response_model=List[IngredientListResponse])
def read_ingredients(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
        is_random: bool = Query(default=False),
):
    if is_random:
        query = select(Ingredient).order_by(func.random()).limit(limit)
    else:
        query = select(Ingredient).offset(offset).limit(limit)

    ingredients = session.exec(query).all()
    return [IngredientResponse.model_validate(ingredient) for ingredient in ingredients]


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def read_ingredient(*, session: Session = Depends(get_session), ingredient_id: int):
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    cooking_tools = session.exec(
        select(CookingTool)
        .join(CookingSetting, CookingTool.id == CookingSetting.cooking_tool_id)
        .where(CookingSetting.ingredient_id == ingredient_id)
        .distinct()
        .order_by(CookingTool.id)  # id 기준 오름차순 정렬
    ).all()

    response = IngredientResponse.model_validate(ingredient)
    response.available_cooking_tools = [CookingToolResponse.model_validate(tool) for tool in cooking_tools]

    return response


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


@router.post("/{ingredient_id}/icon")
async def upload_ingredient_icon(
        *,
        session: Session = Depends(get_session),
        ingredient_id: int,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_superuser),
):
    """일반 아이콘 SVG 업로드"""
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # 기존 일반 이미지가 있다면 삭제
    if ingredient.icon_url:
        key = ingredient.icon_url.split('/')[-1]
        object_storage.delete_image(key)

    # 새 이미지 업로드
    result = await object_storage.upload_image(file, folder="ingredients")
    if not result:
        raise HTTPException(status_code=400, detail="Failed to upload image")

    # DB 업데이트
    ingredient.icon_url = result["url"]
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return {"icon_url": ingredient.icon_url}


@router.post("/{ingredient_id}/home-icon")
async def upload_ingredient_home_icon(
        *,
        session: Session = Depends(get_session),
        ingredient_id: int,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_superuser),
):
    """홈화면용 아이콘 SVG 업로드"""
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if not ingredient.icon_url:
        raise HTTPException(status_code=400, detail="Regular icon must be uploaded first")

    # 기존 홈화면 이미지가 있다면 삭제
    if ingredient.home_icon_url:
        key = ingredient.home_icon_url.split('/')[-1]
        object_storage.delete_image(key)

    # 새 이미지 업로드
    result = await object_storage.upload_image(
        file,
        folder="ingredients",
        is_home=True
    )

    if not result:
        raise HTTPException(status_code=400, detail="Failed to upload image")

    # DB 업데이트
    ingredient.home_icon_url = result["url"]
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return {"home_icon_url": ingredient.home_icon_url}


@router.delete("/{ingredient_id}/icon")
async def delete_ingredient_icon(
        *,
        session: Session = Depends(get_session),
        ingredient_id: int,
        current_user: User = Depends(get_current_superuser),
):
    """일반 아이콘 삭제"""
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if not ingredient.icon_url:
        raise HTTPException(status_code=404, detail="Icon not found")

    # Object Storage에서 이미지 삭제
    key = ingredient.icon_url.split('/')[-1]
    if object_storage.delete_image(key):
        ingredient.icon_url = None
        session.add(ingredient)
        session.commit()
        return {"message": "Icon deleted successfully"}

    raise HTTPException(status_code=500, detail="Failed to delete icon")


@router.delete("/{ingredient_id}/home-icon")
async def delete_ingredient_home_icon(
        *,
        session: Session = Depends(get_session),
        ingredient_id: int,
        current_user: User = Depends(get_current_superuser),
):
    """홈화면용 아이콘 삭제"""
    ingredient = session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if not ingredient.home_icon_url:
        raise HTTPException(status_code=404, detail="Home icon not found")

    # Object Storage에서 이미지 삭제
    key = ingredient.home_icon_url.split('/')[-1]
    if object_storage.delete_image(key):
        ingredient.home_icon_url = None
        session.add(ingredient)
        session.commit()
        return {"message": "Home icon deleted successfully"}

    raise HTTPException(status_code=500, detail="Failed to delete home icon")
