from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends, UploadFile, File
from sqlmodel import select, Session

from api.v1.deps import get_session, get_current_superuser
from core.s3 import object_storage
from models.common import CookingTool
from models.response import CookingToolResponse
from models.user import User

router = APIRouter()


@router.post("/", response_model=CookingTool)
def create_cooking_tool(
        *,
        session: Session = Depends(get_session),
        cooking_tool: CookingTool,
        current_user: User = Depends(get_current_superuser),
):
    session.add(cooking_tool)
    session.commit()
    session.refresh(cooking_tool)
    return cooking_tool


@router.get("/", response_model=List[CookingToolResponse])
def read_cooking_tools(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    tools = session.exec(select(CookingTool).offset(offset).limit(limit)).all()
    return tools


@router.get("/{tool_id}", response_model=CookingToolResponse)
def read_cooking_tool(*, session: Session = Depends(get_session), tool_id: int):
    tool = session.get(CookingTool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Cooking tool not found")
    return tool


@router.patch("/{tool_id}", response_model=CookingTool)
def update_cooking_tool(
        *,
        session: Session = Depends(get_session),
        tool_id: int,
        cooking_tool: CookingTool,
        current_user: User = Depends(get_current_superuser),
):
    db_tool = session.get(CookingTool, tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Cooking tool not found")

    tool_data = cooking_tool.dict(exclude_unset=True)
    for key, value in tool_data.items():
        setattr(db_tool, key, value)

    session.add(db_tool)
    session.commit()
    session.refresh(db_tool)
    return db_tool


@router.delete("/{tool_id}")
def delete_cooking_tool(
        *,
        session: Session = Depends(get_session),
        tool_id: int,
        current_user: User = Depends(get_current_superuser),
):
    tool = session.get(CookingTool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Cooking tool not found")

    session.delete(tool)
    session.commit()
    return {"ok": True}


@router.post("/{tool_id}/icon")
async def upload_cooking_tool_icon(
        *,
        session: Session = Depends(get_session),
        tool_id: int,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_superuser),
):
    """요리 도구 아이콘 SVG 업로드"""
    tool = session.get(CookingTool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Cooking tool not found")

    # 기존 이미지가 있다면 삭제
    if tool.icon_url:
        key = tool.icon_url.split('/')[-1]
        object_storage.delete_image(key)

    # 새 이미지 업로드
    result = await object_storage.upload_image(file, folder="cooking_tools")
    if not result:
        raise HTTPException(status_code=400, detail="Failed to upload image")

    # DB 업데이트
    tool.icon_url = result["url"]
    session.add(tool)
    session.commit()
    session.refresh(tool)

    return {"icon_url": tool.icon_url}


@router.delete("/{tool_id}/icon")
async def delete_cooking_tool_icon(
        *,
        session: Session = Depends(get_session),
        tool_id: int,
        current_user: User = Depends(get_current_superuser),
):
    """요리 도구 아이콘 삭제"""
    tool = session.get(CookingTool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Cooking tool not found")

    if not tool.icon_url:
        raise HTTPException(status_code=404, detail="Icon not found")

    # Object Storage에서 이미지 삭제
    key = tool.icon_url.split('/')[-1]
    if object_storage.delete_image(key):
        tool.icon_url = None
        session.add(tool)
        session.commit()
        return {"message": "Icon deleted successfully"}

    raise HTTPException(status_code=500, detail="Failed to delete icon")
