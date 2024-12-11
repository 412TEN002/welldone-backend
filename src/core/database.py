from sqlalchemy import QueuePool, create_engine, Engine
from sqlmodel import Session, select

from core.config import settings
from core.enums import UserRole
from models.common import Category, Ingredient, CookingSettingTip, CookingSetting, CookingMethod, CookingTool, \
    HeatingMethod, Timer, Feedback, NutritionTag, IngredientNutritionLink
from models.user import User

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
    User.metadata.create_all(engine)

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

    # Check if superuser exists
    superuser = session.exec(
        select(User).where(User.role == UserRole.SUPERUSER)
    ).first()

    if not superuser:
        # Create default superuser
        default_superuser = User(
            email="admin@example.com",
            username="admin",
            hashed_password=User.get_password_hash("admin123"),
            role=UserRole.SUPERUSER,
            is_active=True
        )
        session.add(default_superuser)

        try:
            session.commit()
            print("Default superuser created successfully!")
            print("Email: admin@example.com")
            print("Password: admin123")
            print("Please change these credentials immediately after first login!")
        except Exception as e:
            session.rollback()
            print(f"Error creating superuser: {e}")
            raise
