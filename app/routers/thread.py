from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import (
    relationship,
    selectinload,
    subqueryload,
    Session,
    joinedload,
    immediateload,
)
from typing import List
import app.models.models as m
from app.database import get_db
from app.security import get_current_user
import pyd
from sqlalchemy.ext.asyncio import AsyncSession

# контролер пользователя
thread_router = APIRouter(
    prefix="/thread",
    tags=["thread"],
)


@thread_router.get("/posts/{post_id}", response_model=List[pyd.ThreadSchema])
async def get_threads_by_post_id(post_id: int, db: AsyncSession = Depends(get_db)):
    # Явно загружаем связанные данные
    stmt = (
        select(m.Thread)
        .where(m.Thread.post_id == post_id)
        .options(
            selectinload(m.Thread.user).selectinload(m.User.role),
            selectinload(m.Thread.children, recursion_depth=4),
            # selectinload(m.Thread.post),
            subqueryload(m.Thread.parent),
        )
        .limit(100)
    )

    result = await db.execute(stmt)
    threads = list(result.scalars().all())

    return build_thread_tree(threads)


@thread_router.get("/{thread_id}", response_model=List[pyd.ThreadSchema])
async def get_thread_by_id(thread_id: int, db: AsyncSession = Depends(get_db)):
    # Явно загружаем связанные данные
    sql = text(
        """
        WITH RECURSIVE child_threads AS (
            SELECT 
                t.id,
                t.content,
                t.image_url,
                t.creator_id,
                t.post_id,
                t.parent_id,
                1 AS depth
            FROM threads t
            WHERE t.id = :thread_id

            UNION ALL

            SELECT 
                t2.id,
                t2.content,
                t2.image_url,
                t2.creator_id,
                t2.post_id,
                t2.parent_id,
                ct.depth + 1
            FROM threads t2
            JOIN child_threads ct ON t2.parent_id = ct.id
        )
        SELECT 
            ct.*,
            u.user_name
        FROM child_threads ct
        JOIN users u ON ct.creator_id = u.id
        ORDER BY ct.depth, ct.id;
    """
    )

    result = await db.execute(sql, {"thread_id": thread_id})
    rows = result.mappings().all()
    # print(rows)
    threads = []
    for row in rows:
        threads.append(
            pyd.ThreadSchema(
                id=row["id"],
                content=row["content"],
                image_url=row["image_url"],
                creator_id=row["creator_id"],
                parent_id=row["parent_id"],
                post_id=row["post_id"],
                user=pyd.UserThreadSchema(user_name=row["user_name"]),
                children=[],
            )
        )

    return build_thread_tree(threads)


@thread_router.post("/{post_id}", response_model=pyd.ThreadSchema, status_code=201)
async def create_thread(
    post_id: int,
    thread_data: pyd.CreateThread,
    current_user: m.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Создаём новый тред
    new_thread = m.Thread(
        content=thread_data.content,
        image_url=thread_data.image_url,
        creator_id=current_user.id,
        post_id=post_id,
        parent_id=thread_data.parent_id,
    )

    db.add(new_thread)
    await db.commit()
    await db.refresh(new_thread)
    new_thread = pyd.ThreadSchema(
        **new_thread.__dict__,
        user=pyd.UserThreadSchema(
            user_name=current_user.user_name,
        ),
    )

    return new_thread

# @thread_router.post("/{post_id}", response_model=pyd.ThreadSchema, status_code=201)
# async def create_thread(
#     parent_id: int,
#     thread_data: pyd.CreateThread,
#     current_user: m.User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     # Создаём новый тред
#     new_thread = m.Thread(
#         content=thread_data.content,
#         image_url=thread_data.image_url,
#         creator_id=current_user.id,
#         parent_id=parent_id,
#         post_id=parent_id.post_id,
#     )

#     db.add(new_thread)
#     await db.commit()
#     await db.refresh(new_thread)
#     new_thread = pyd.ThreadSchema(
#         **new_thread.__dict__,
#         user=pyd.UserThreadSchema(
#             user_name=current_user.user_name,
#         ),
#     )

#     return new_thread

def build_thread_tree(threads: List[m.Thread]) -> List[pyd.ThreadSchema]:
    thread_dict = {thread.id: thread for thread in threads}
    tree = []
    # print(thread_dict)

    # Чистим возможные дублированные children
    for thread in thread_dict.values():
        thread.children = []

    for thread in threads:
        if thread.parent_id:
            parent = thread_dict.get(thread.parent_id)
            if parent:
                parent.children.append(thread)
        else:
            tree.append(thread)

    def serialize(thread: m.Thread) -> pyd.ThreadSchema:
        return pyd.ThreadSchema(
            id=thread.id,
            content=thread.content,
            image_url=thread.image_url,
            creator_id=thread.creator_id,
            post_id=thread.post_id,
            user=(
                pyd.UserThreadSchema(
                    user_name=thread.user.user_name,
                    role=thread.user.role.role_name if thread.user.role else None,
                )
                if thread.user
                else None
            ),
            children=[serialize(child) for child in thread.children],
        )

    return [serialize(t) for t in tree]
