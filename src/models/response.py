from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr

from models.user import UserRole


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class NutritionTagResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class CookingSettingResponse(BaseModel):
    id: int
    temperature: Optional[float] = None
    cooking_time: Optional[int] = None


class IngredientResponse(BaseModel):
    id: int
    name: str
    icon_url: Optional[str] = None
    category: Optional[CategoryResponse] = None
    cooking_settings: List[CookingSettingResponse] = []
    nutrition_tags: List[NutritionTagResponse] = []


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
