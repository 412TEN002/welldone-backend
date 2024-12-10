from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None

    # Relationships
    ingredients: List["Ingredient"] = Relationship(back_populates="category")


class IngredientNutritionLink(SQLModel, table=True):
    __tablename__ = "ingredient_nutrition_link"

    ingredient_id: Optional[int] = Field(
        default=None,
        foreign_key="ingredient.id",
        primary_key=True
    )
    nutrition_tag_id: Optional[int] = Field(
        default=None,
        foreign_key="nutritiontag.id",
        primary_key=True
    )


class NutritionTag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None

    # Relationships
    ingredients: List["Ingredient"] = Relationship(
        back_populates="nutrition_tags",
        link_model=IngredientNutritionLink
    )


class Ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="ingredients")
    cooking_settings: List["CookingSetting"] = Relationship(back_populates="ingredient")
    nutrition_tags: List[NutritionTag] = Relationship(
        back_populates="ingredients",
        link_model=IngredientNutritionLink
    )


class CookingMethod(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Relationships
    cooking_settings: List["CookingSetting"] = Relationship(back_populates="cooking_method")


class CookingTool(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Relationships
    cooking_settings: List["CookingSetting"] = Relationship(back_populates="cooking_tool")


class HeatingMethod(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: Optional[str] = None
    icon_url: Optional[str] = None

    # Relationships
    cooking_settings: List["CookingSetting"] = Relationship(back_populates="heating_method")


class CookingSetting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredient.id")
    cooking_method_id: int = Field(foreign_key="cookingmethod.id")
    cooking_tool_id: int = Field(foreign_key="cookingtool.id")
    heating_method_id: int = Field(foreign_key="heatingmethod.id")
    temperature: Optional[float] = None
    cooking_time: Optional[int] = None  # in seconds

    # Relationships
    ingredient: Ingredient = Relationship(back_populates="cooking_settings")
    cooking_method: CookingMethod = Relationship(back_populates="cooking_settings")
    cooking_tool: CookingTool = Relationship(back_populates="cooking_settings")
    heating_method: HeatingMethod = Relationship(back_populates="cooking_settings")
    tips: List["CookingSettingTip"] = Relationship(back_populates="cooking_setting")
    timers: List["Timer"] = Relationship(back_populates="cooking_setting")


class CookingSettingTip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cooking_setting_id: int = Field(foreign_key="cookingsetting.id")
    message: str

    # Relationships
    cooking_setting: CookingSetting = Relationship(back_populates="tips")


class Timer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cooking_setting_id: int = Field(foreign_key="cookingsetting.id")

    # Relationships
    cooking_setting: CookingSetting = Relationship(back_populates="timers")
    feedbacks: List["Feedback"] = Relationship(back_populates="timer")


class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timer_id: int = Field(foreign_key="timer.id")
    comment: Optional[str] = None
    star_rating: Optional[int] = Field(default=None, ge=1, le=5)

    # Relationships
    timer: Timer = Relationship(back_populates="feedbacks")
