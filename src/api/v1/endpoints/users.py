from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from api.v1.deps import get_session, create_access_token, get_current_superuser, get_current_user
from models.response import UserResponse, UserCreate, UserUpdate
from models.user import User

router = APIRouter()


@router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)
) -> dict:
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=UserResponse)
async def create_user(
        *,
        session: Session = Depends(get_session),
        user_in: UserCreate,
        current_user: User = Depends(get_current_superuser)
) -> User:
    # Check if email already exists
    db_user = session.exec(
        select(User).where(User.email == user_in.email)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    db_user = session.exec(
        select(User).where(User.username == user_in.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=User.get_password_hash(user_in.password),
        role=user_in.role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse)
async def read_current_user(
        current_user: User = Depends(get_current_user)
) -> User:
    return current_user


@router.get("/", response_model=List[UserResponse])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_superuser),
        session: Session = Depends(get_session)
) -> List[UserResponse]:
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
        user_id: int,
        current_user: User = Depends(get_current_superuser),
        session: Session = Depends(get_session)
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_in: UserUpdate,
        current_user: User = Depends(get_current_superuser),
        session: Session = Depends(get_session)
) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_data = user_in.dict(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = User.get_password_hash(user_data.pop("password"))

    for field, value in user_data.items():
        setattr(db_user, field, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_superuser),
        session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    session.delete(user)
    session.commit()
    return {"ok": True}
