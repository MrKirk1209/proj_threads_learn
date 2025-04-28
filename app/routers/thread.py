from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import List
import app.models.models as m
from app.database import get_db
import pyd
from sqlalchemy.ext.asyncio import AsyncSession

# контролер пользователя
thread_router = APIRouter(
    prefix="/thread",
    tags=["thread"],
)


@thread_router.get("/{post_id}", response_model=List[pyd.ThreadSchema])
async def get_threads_by_post_id(post_id: int, db: AsyncSession = Depends(get_db)):
    # Явно загружаем связанные данные
    stmt = (
        select(m.Thread)
        .where(m.Thread.post_id == post_id)
        .options(
            selectinload(m.Thread.user).selectinload(m.User.role),
            selectinload(m.Thread.children, recursion_depth=4),
            selectinload(m.Thread.post),
            subqueryload(m.Thread.parent),
        )
        .limit(100)
    )

    result = await db.execute(stmt)
    threads = list(result.scalars().all())

    return build_thread_tree(threads)


def build_thread_tree(threads: List[m.Thread]) -> List[pyd.ThreadSchema]:
    thread_dict = {thread.id: thread for thread in threads}
    tree = []

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
            post=(
                pyd.PostBase(
                    id=thread.post.id,
                    title=thread.post.title,
                    content=thread.post.content,
                    image_url=thread.post.image_url,
                    author_id=thread.post.author_id,
                )
                if thread.parent_id is None
                else None
            ),
            children=[serialize(child) for child in thread.children],
        )

    return [serialize(t) for t in tree]
