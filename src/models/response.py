from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict

from core.enums import ColorTheme
from models.common import CookingSettingTip, NutritionTag
from models.user import UserRole


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NutritionTagResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class CookingSettingResponse(BaseModel):
    id: int
    ingredient: "IngredientResponse"
    cooking_tool: "CookingToolResponse"
    temperature: int
    cooking_time: int
    color_theme: ColorTheme
    tips: List[CookingSettingTip]


class IngredientListResponse(BaseModel):
    id: Optional[int]
    name: str
    category_id: Optional[int] = None
    color_theme: ColorTheme
    home_icon_url: Optional[str] = None
    icon_url: Optional[str] = None
    nutrition_tags: List[NutritionTag] = []

    model_config = ConfigDict(from_attributes=True)


class IngredientResponse(BaseModel):
    id: Optional[int]
    name: str
    category_id: Optional[int] = None
    color_theme: ColorTheme
    home_icon_url: Optional[str] = None
    icon_url: Optional[str] = None
    nutrition_tags: List[NutritionTag] = []
    available_cooking_tools: List["CookingToolResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class IngredientSearchResponse(BaseModel):
    id: Optional[int]
    name: str
    category_id: Optional[int] = None
    icon_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CookingToolResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.NORMAL


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# Response Models (Output schemas)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    role: UserRole
    created_datetime: datetime
    updated_datetime: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
