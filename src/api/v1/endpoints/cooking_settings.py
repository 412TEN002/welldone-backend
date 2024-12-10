from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select

from api.v1.deps import SessionDep
from models.common import CookingSetting, CookingSettingTip

router = APIRouter()


@router.post("/", response_model=CookingSetting)
def create_cooking_setting(*, session: SessionDep, cooking_setting: CookingSetting):
    session.add(cooking_setting)
    session.commit()
    session.refresh(cooking_setting)
    return cooking_setting


@router.get("/", response_model=List[CookingSetting])
def read_cooking_settings(
        *,
        session: SessionDep,
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    settings = session.exec(select(CookingSetting).offset(offset).limit(limit)).all()
    return settings


@router.get("/{cooking_setting_id}", response_model=CookingSetting)
def read_cooking_setting(*, session: SessionDep, cooking_setting_id: int):
    setting = session.get(CookingSetting, cooking_setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Cooking setting not found")
    return setting


@router.patch("/{cooking_setting_id}", response_model=CookingSetting)
def update_cooking_setting(
        *, session: SessionDep, cooking_setting_id: int, cooking_setting: CookingSetting
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
def delete_cooking_setting(*, session: SessionDep, cooking_setting_id: int):
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
        session: SessionDep
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
        session: SessionDep,
        cooking_setting_id: int,
        skip: int = 0,
        limit: int = Query(default=100, le=100),
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
        cooking_setting_id: int,
        tip_id: int,
        session: SessionDep
):
    tip = session.exec(
        select(CookingSettingTip)
        .where(
            CookingSettingTip.cooking_setting_id == cooking_setting_id,
            CookingSettingTip.id == tip_id
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
        session: SessionDep
):
    tip = session.exec(
        select(CookingSettingTip)
        .where(
            CookingSettingTip.cooking_setting_id == cooking_setting_id,
            CookingSettingTip.id == tip_id
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
        session: SessionDep
):
    tip = session.exec(
        select(CookingSettingTip)
        .where(
            CookingSettingTip.cooking_setting_id == cooking_setting_id,
            CookingSettingTip.id == tip_id
        )
    ).first()

    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")

    session.delete(tip)
    session.commit()
    return {"message": "Tip deleted successfully"}
