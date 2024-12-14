from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, EmailStr, ConfigDict, model_validator

from core.enums import ColorTheme
from core.s3 import object_storage
from models.common import CookingSettingTip
from models.user import UserRole


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_key: Optional[str] = None
    icon_urls: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def generate_icon_urls(self):
        if self.icon_key:
            self.icon_urls = object_storage.get_image_urls(self.icon_key)
        return self


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


class IngredientResponse(BaseModel):
    id: Optional[int]
    name: str
    chosung: str
    category_id: Optional[int] = None
    color_theme: ColorTheme
    home_icon_urls: Optional[Dict[str, str]] = None
    icon_urls: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True


class IngredientSearchResponse(BaseModel):
    id: Optional[int]
    name: str
    chosung: str
    category_id: Optional[int] = None
    color_theme: ColorTheme
    icon_urls: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True


class CookingToolResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_key: Optional[str] = None
    icon_urls: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def generate_icon_urls(self):
        if self.icon_key:
            self.icon_urls = object_storage.get_image_urls(self.icon_key)
        return self


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
