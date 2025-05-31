from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import List
import app.models.models as m
from app.database import get_db
from app.routers.thread import build_thread_tree, get_threads_by_post_id
import pyd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc
from app.security import get_current_user


category_router = APIRouter(
    prefix="/category",
    tags=["category"],
)


@category_router.get("", response_model=List[pyd.CategorySchema])
async def get_all_category(db: AsyncSession = Depends(get_db)):
    stmt = select(m.Category).order_by(m.Category.id).limit(100)

    result = await db.execute(stmt)
    post = result.scalars().all()

    return post


@category_router.post("/", response_model=pyd.CategorySchema, status_code=201)
async def create_post(
    category_data: pyd.CreateCategory,
    current_user: m.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    # Создаём новый пост
    new_category = m.Category(
        name=category_data.name,
        # description=category_data.description,
    )

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    new_category = pyd.CategorySchema(
        **new_category.__dict__,
    )

    return new_category
