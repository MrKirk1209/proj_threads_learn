from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import List
import app.models.models as m
from app.database import get_db
import pyd
from sqlalchemy.ext.asyncio import AsyncSession

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
