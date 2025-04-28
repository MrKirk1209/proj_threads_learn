from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import List
import app.models.models as m
from app.database import get_db
import pyd
from sqlalchemy.ext.asyncio import AsyncSession


post_router = APIRouter(
    prefix="/post",
    tags=["post"],
)


@post_router.get("/all", response_model=List[pyd.PostSchema])
async def get_all_post(db: AsyncSession = Depends(get_db)):
    # Явно загружаем связанные данные
    stmt = (
        select(m.Post)
        .order_by(m.Post.id)
        .limit(100)
    )

    result = await db.execute(stmt)
    post = result.scalars().all()

    return post
