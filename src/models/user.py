from datetime import datetime
from typing import Optional

from passlib.context import CryptContext
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from core.enums import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.NORMAL)
    created_datetime: datetime = Field(default_factory=datetime.utcnow)
    updated_datetime: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
