from typing import Optional, List

from pydantic import BaseModel


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
    category: Optional[CategoryResponse] = None
    cooking_settings: List[CookingSettingResponse] = []
    nutrition_tags: List[NutritionTagResponse] = []
