from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from models.common import CookingSetting, CookingSettingTip
from models.user import User

router = APIRouter()


@router.post("/", response_model=CookingSetting)
def create_cooking_setting(
        *,
        session: Session = Depends(get_session),
        cooking_setting: CookingSetting,
        current_user: User = Depends(get_current_superuser)
):
    session.add(cooking_setting)
    session.commit()
    session.refresh(cooking_setting)
    return cooking_setting


@router.get("/")
def read_cooking_settings_with_tips(
        *,
        session: Session = Depends(get_session),
        ingredient_id: int,
        cooking_tool_id: int,
):
    """
    조리 설정과 관련된 팁을 함께 조회합니다.
    선택적으로 재료, 조리방법, 조리도구, 가열방법으로 필터링할 수 있습니다.
    """
    # 동적으로 where 절 구성
    query = (
        select(CookingSetting)
        .options(
            selectinload(CookingSetting.tips)
        )
        .where(CookingSetting.ingredient_id == ingredient_id)
        .where(CookingSetting.cooking_tool_id == cooking_tool_id)
    )

    setting = session.exec(query).first()

    if not setting:
        raise HTTPException(status_code=404, detail="Cooking setting not found")

    # 응답 포맷 조정
    setting_dict = {
        "id": setting.id,
        "temperature": setting.temperature,
        "cooking_time": setting.cooking_time,
        "color_theme": setting.ingredient.color_theme,
        "tips": [{"tip_type": tip.tip_type, "message": tip.message} for tip in setting.tips] if setting.tips else []
    }

    return setting_dict


@router.patch("/{cooking_setting_id}", response_model=CookingSetting)
def update_cooking_setting(
        *,
        session: Session = Depends(get_session),
        cooking_setting_id: int,
        cooking_setting: CookingSetting,
        current_user: User = Depends(get_current_superuser)
):
    db_setting = session.get(CookingSetting, cooking_setting_id)
    if not db_setting:
        raise HTTPException(status_code=404, detail="Cooking setting not found")

    setting_data = cooking_setting.dict(exclude_unset=True)
    for key, value in setting_data.items():
        setattr(db_setting, key, value)

    session.add(db_setting)
    session.commit()
    session.refresh(db_setting)
    return db_setting


@router.delete("/{cooking_setting_id}")
def delete_cooking_setting(
        *,
        session: Session = Depends(get_session),
        cooking_setting_id: int,
        current_user: User = Depends(get_current_superuser)
):
    setting = session.get(CookingSetting, cooking_setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Cooking setting not found")

    session.delete(setting)
    session.commit()
    return {"ok": True}


@router.post("/{cooking_setting_id}/tips", response_model=CookingSettingTip)
def create_cooking_setting_tip(
        cooking_setting_id: int,
        tip: CookingSettingTip,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_superuser),
):
    cooking_setting = session.get(CookingSetting, cooking_setting_id)
    if not cooking_setting:
        raise HTTPException(status_code=404, detail="Cooking setting not found")

    tip.cooking_setting_id = cooking_setting_id
    session.add(tip)
    session.commit()
    session.refresh(tip)
    return tip


@router.get("/{cooking_setting_id}/tips", response_model=List[CookingSettingTip])
def read_cooking_setting_tips(
        cooking_setting_id: int,
        skip: int = 0,
        limit: int = Query(default=100, le=100),
        session: Session = Depends(get_session),
):
    cooking_setting = session.get(CookingSetting, cooking_setting_id)
    if not cooking_setting:
        raise HTTPException(status_code=404, detail="Cooking setting not found")

    tips = session.exec(
        select(CookingSettingTip)
        .where(CookingSettingTip.cooking_setting_id == cooking_setting_id)
        .offset(skip)
        .limit(limit)
    ).all()
    return tips


@router.get("/{cooking_setting_id}/tips/{tip_id}", response_model=CookingSettingTip)
def read_cooking_setting_tip(
        cooking_setting_id: int, tip_id: int, session: Session = Depends(get_session)
):
    tip = session.exec(
        select(CookingSettingTip).where(
            CookingSettingTip.cooking_setting_id == cooking_setting_id,
            CookingSettingTip.id == tip_id,
        )
    ).first()

    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    return tip


@router.put("/{cooking_setting_id}/tips/{tip_id}", response_model=CookingSettingTip)
def update_cooking_setting_tip(
        cooking_setting_id: int,
        tip_id: int,
        tip_update: CookingSettingTip,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_superuser),
):
    tip = session.exec(
        select(CookingSettingTip).where(
            CookingSettingTip.cooking_setting_id == cooking_setting_id,
            CookingSettingTip.id == tip_id,
        )
    ).first()

    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")

    tip_data = tip_update.dict(exclude_unset=True)
    for key, value in tip_data.items():
        if key != "cooking_setting_id":
            setattr(tip, key, value)

    session.add(tip)
    session.commit()
    session.refresh(tip)
    return tip


@router.delete("/{cooking_setting_id}/tips/{tip_id}")
def delete_cooking_setting_tip(
        cooking_setting_id: int,
        tip_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_superuser),
):
    tip = session.exec(
        select(CookingSettingTip).where(
            CookingSettingTip.cooking_setting_id == cooking_setting_id,
            CookingSettingTip.id == tip_id,
        )
    ).first()

    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")

    session.delete(tip)
    session.commit()
    return {"message": "Tip deleted successfully"}
