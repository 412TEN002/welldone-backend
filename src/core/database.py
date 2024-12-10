from sqlalchemy import QueuePool, create_engine, Engine
from sqlmodel import Session

from core.config import settings
from models.common import Category, Ingredient, CookingSettingTip, CookingSetting, CookingMethod, CookingTool, \
    HeatingMethod, Timer, Feedback, NutritionTag, IngredientNutritionLink

if settings.ENVIRONMENT == "local":
    engine = create_engine(
        "sqlite:///test.db", connect_args={"check_same_thread": False}
    )
else:
    dbschema = "db,public"

    engine = create_engine(
        "postgresql://",
        poolclass=QueuePool,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        connect_args={"options": f"-c search_path={dbschema}"},
    )


async def init_db(session: Session, engine: Engine) -> None:
    Category.metadata.create_all(engine)
    CookingMethod.metadata.create_all(engine)
    CookingSetting.metadata.create_all(engine)
    CookingSettingTip.metadata.create_all(engine)
    CookingTool.metadata.create_all(engine)
    Feedback.metadata.create_all(engine)
    HeatingMethod.metadata.create_all(engine)
    IngredientNutritionLink.metadata.create_all(engine)
    NutritionTag.metadata.create_all(engine)
    Ingredient.metadata.create_all(engine)
    Timer.metadata.create_all(engine)
