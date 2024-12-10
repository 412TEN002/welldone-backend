from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class IngredientBase(BaseModel):
    name: str = Field(..., max_length=100)
    category_id: int
    default_amount: Optional[Decimal] = None
    unit: Optional[str] = Field(None, max_length=20)
    cooking_tip: Optional[str] = None

class Ingredient(IngredientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CookingMethodBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    icon_url: Optional[str] = Field(None, max_length=255)

class CookingMethod(CookingMethodBase):
    id: int

    class Config:
        orm_mode = True

class CookingToolBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    icon_url: Optional[str] = Field(None, max_length=255)

class CookingTool(CookingToolBase):
    id: int

    class Config:
        orm_mode = True

class CookingSettingBase(BaseModel):
    ingredient_id: int
    cooking_method_id: int
    cooking_tool_id: int
    amount: Optional[Decimal] = None
    temperature: Optional[int] = None
    cooking_time: Optional[int] = None
    doneness_level: Optional[str] = Field(None, max_length=20)
    heat_level: Optional[str] = Field(None, max_length=20)

class CookingSetting(CookingSettingBase):
    id: int

    class Config:
        orm_mode = True

class TimerBase(BaseModel):
    user_id: int
    cooking_setting_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pause_time: Optional[datetime] = None
    status: str = Field(..., max_length=20)
    total_duration: int
    remaining_time: int

class Timer(TimerBase):
    id: int

    class Config:
        orm_mode = True

class FeedbackBase(BaseModel):
    user_id: int
    timer_id: int
    timer_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    voice_guide_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CookingHistoryBase(BaseModel):
    user_id: int
    cooking_setting_id: int
    timer_id: int
    feedback_id: Optional[int] = None

class CookingHistory(CookingHistoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Request/Response Models
class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(IngredientBase):
    name: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None

class CookingSettingCreate(CookingSettingBase):
    pass

class TimerCreate(TimerBase):
    pass

class FeedbackCreate(FeedbackBase):
    pass

class CookingHistoryCreate(CookingHistoryBase):
    pass