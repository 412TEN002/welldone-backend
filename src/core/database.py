from sqlalchemy import QueuePool, create_engine

from core.config import settings

if settings.ENVIRONMENT == "test":
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
