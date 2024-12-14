from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from core.enums import TipType, TimerFeedbackType, ColorTheme
from utils.utils import get_chosung


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Relationships
    ingredients: List["Ingredient"] = Relationship(back_populates="category")


class IngredientNutritionLink(SQLModel, table=True):
    __tablename__ = "ingredient_nutrition_links"

    ingredient_id: Optional[int] = Field(
        default=None, foreign_key="ingredients.id", primary_key=True
    )
    nutrition_tag_id: Optional[int] = Field(
        default=None, foreign_key="nutrition_tags.id", primary_key=True
    )


class NutritionTag(SQLModel, table=True):
    __tablename__ = "nutrition_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None

    # Relationships
    ingredients: List["Ingredient"] = Relationship(
        back_populates="nutrition_tags", link_model=IngredientNutritionLink
    )


class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    chosung: str = Field(index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    color_theme: ColorTheme = Field(default=ColorTheme.BLACK)
    icon_url: Optional[str] = None
    home_icon_url: Optional[str] = None

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="ingredients")
    cooking_settings: List["CookingSetting"] = Relationship(back_populates="ingredient")
    nutrition_tags: List[NutritionTag] = Relationship(
        back_populates="ingredients", link_model=IngredientNutritionLink
    )

    def __init__(self, **data):
        if "name" in data and "chosung" not in data:
            data["chosung"] = get_chosung(data["name"])
        super().__init__(**data)


class CookingMethod(SQLModel, table=True):
    __tablename__ = "cooking_methods"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Relationships
    # cooking_settings: List["CookingSetting"] = Relationship(
    #     back_populates="cooking_method"
    # )


class CookingTool(SQLModel, table=True):
    __tablename__ = "cooking_tools"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Relationships
    cooking_settings: List["CookingSetting"] = Relationship(
        back_populates="cooking_tool"
    )


class HeatingMethod(SQLModel, table=True):
    __tablename__ = "heating_methods"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Relationships
    # cooking_settings: List["CookingSetting"] = Relationship(
    #     back_populates="heating_method"
    # )


class CookingSetting(SQLModel, table=True):
    __tablename__ = "cooking_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredients.id")
    # cooking_method_id: int = Field(foreign_key="cooking_methods.id")
    cooking_tool_id: int = Field(foreign_key="cooking_tools.id")
    # heating_method_id: int = Field(foreign_key="heatingmethod.id")
    temperature: int = Field(ge=0, default=0)
    cooking_time: int = Field(gt=0)

    # Relationships
    ingredient: Ingredient = Relationship(back_populates="cooking_settings")
    # cooking_method: CookingMethod = Relationship(back_populates="cooking_settings")
    cooking_tool: CookingTool = Relationship(back_populates="cooking_settings")
    # heating_method: HeatingMethod = Relationship(back_populates="cooking_settings")
    tips: List["CookingSettingTip"] = Relationship(back_populates="cooking_setting")
    timers: List["Timer"] = Relationship(back_populates="cooking_setting")


class CookingSettingTip(SQLModel, table=True):
    __tablename__ = "cooking_setting_tips"

    id: Optional[int] = Field(default=None, primary_key=True)
    cooking_setting_id: int = Field(foreign_key="cooking_settings.id")
    tip_type: TipType = Field(index=True)
    message: str

    # Relationships
    cooking_setting: CookingSetting = Relationship(back_populates="tips")


class Timer(SQLModel, table=True):
    __tablename__ = "timers"

    id: Optional[int] = Field(default=None, primary_key=True)
    cooking_setting_id: int = Field(foreign_key="cooking_settings.id")

    # Relationships
    cooking_setting: CookingSetting = Relationship(back_populates="timers")
    feedbacks: List["TimerFeedback"] = Relationship(back_populates="timer")


class TimerFeedback(SQLModel, table=True):
    __tablename__ = "timer_feedbacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    timer_id: int = Field(foreign_key="timers.id")
    timer_feedback_type: TimerFeedbackType = Field(index=True)
    comment: Optional[str] = None
    # star_rating: Optional[int] = Field(default=None, ge=1, le=5)

    # Relationships
    timer: Timer = Relationship(back_populates="feedbacks")


class IngredientRequestFeedback(SQLModel, table=True):
    __tablename__ = "ingredient_request_feedbacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    comment: Optional[str] = None
