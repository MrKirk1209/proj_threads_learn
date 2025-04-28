from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import List
import app.models.models as m
from app.database import get_db
import pyd
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.security import get_password_hash
# контролер пользователя
user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@user_router.get("/all", response_model=List[pyd.UserSchema])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    # Явно загружаем связанные данные
    stmt = (
        select(m.User)
        .options(
            selectinload(m.User.role),
            selectinload(m.User.posts),
            selectinload(m.User.threads),
        )
        .order_by(m.User.id)
        .limit(100)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    return users





@user_router.post("/create", response_model=pyd.CreateUser,status_code=status.HTTP_201_CREATED)
async def create_user(user_data: pyd.CreateUser, db: AsyncSession = Depends(get_db)):
    # print(user_data.user_password)
    hashed_password = get_password_hash(user_data.user_password)

    stmt = (
        select(m.Role)
        .where(m.Role.role_name == "admin")
    )
    result = await db.execute(stmt)
    role = result.scalars().first()
    new_user = m.User(
        email=user_data.email,
        user_name=user_data.user_name,
        user_password=hashed_password,
        role_id=role.id
    )
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email или имя пользователя уже существует"
        )
    
    return new_user