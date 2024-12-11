from typing import List

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select, Session

from api.v1.deps import get_session
from models.common import CookingTool

router = APIRouter()


@router.post("/", response_model=CookingTool)
def create_cooking_tool(*, session: Session = Depends(get_session), cooking_tool: CookingTool):
    session.add(cooking_tool)
    session.commit()
    session.refresh(cooking_tool)
    return cooking_tool


@router.get("/", response_model=List[CookingTool])
def read_cooking_tools(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    tools = session.exec(select(CookingTool).offset(offset).limit(limit)).all()
    return tools


@router.get("/{tool_id}", response_model=CookingTool)
def read_cooking_tool(*, session: Session = Depends(get_session), tool_id: int):
    tool = session.get(CookingTool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Cooking tool not found")
    return tool


@router.patch("/{tool_id}", response_model=CookingTool)
def update_cooking_tool(
        *, session: Session = Depends(get_session), tool_id: int, cooking_tool: CookingTool
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
def delete_cooking_tool(*, session: Session = Depends(get_session), tool_id: int):
    tool = session.get(CookingTool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Cooking tool not found")

    session.delete(tool)
    session.commit()
    return {"ok": True}
