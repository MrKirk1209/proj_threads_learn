from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import List
import app.models.models as m
from app.database import get_db
import pyd
from sqlalchemy.ext.asyncio import AsyncSession


role_router = APIRouter(
    prefix="/role",
    tags=["role"],
)

@role_router.get("/all", response_model=List[pyd.RoleSchema])
async def get_all_role(db: AsyncSession = Depends(get_db)):
    # Явно загружаем связанные данные
    stmt = (
        select(m.Role)
        .order_by(m.Role.id)
        .limit(100)
    )

    result = await db.execute(stmt)
    role = result.scalars().all()

    return role
