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


post_router = APIRouter(
    prefix="/post",
    tags=["post"],
)


@post_router.get("/all", response_model=List[pyd.PostSchema])
async def get_all_post(db: AsyncSession = Depends(get_db)):
    # Явно загружаем связанные данные
    stmt = select(m.Post).order_by(m.Post.id).limit(100)

    result = await db.execute(stmt)
    post = result.scalars().all()

    return post


@post_router.get("", response_model=List[pyd.postSchemaWithAuthor], status_code=200)
async def get_all_post_sort(
    sort: str | None = None, db: AsyncSession = Depends(get_db)
):
    # Явно загружаем связанные данные
    stmt = select(m.Post).options(selectinload(m.Post.author)).limit(100)

    match sort:
        case "recent":
            stmt = stmt.order_by(desc(m.Post.created_at))
        case "relevant":
            stmt = stmt.order_by(desc(m.Post.threads_count))
        case "old":
            stmt = stmt.order_by(asc(m.Post.created_at))

        case None:
            stmt = stmt.order_by(m.Post.id)

    result = await db.execute(stmt)
    posts = result.scalars().all()
    print(posts)
    return posts


@post_router.get(
    "/{post_id}",
    response_model=pyd.PostSchemaWithThreads,
)
async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(m.Post)
        .where(m.Post.id == post_id)
        .options(
            selectinload(m.Post.threads).selectinload(m.Thread.children),
            selectinload(m.Post.author),
        )
    )

    result = await db.execute(stmt)
    post = result.scalars().first()

    threads = await get_threads_by_post_id(post_id, db)
    responce_post = pyd.PostSchemaWithThreads(
        id=post.id,
        title=post.title,
        content=post.content,
        image_url=post.image_url,
        author_id=post.author_id,
        created_at=post.created_at,
        updated_at=post.updated_at,
        threads_count=post.threads_count,
        author=pyd.UserThreadSchema(
            user_name=post.author.user_name,
        ),
        threads=threads,
    )

    # if not post:
    #     raise HTTPException(status_code=404, detail="Post not found")
    # # for thread in post.threads:
    # #     thread.children = []
    # print(post.threads)
    # responce_post = pyd.PostSchemaWithThreads(
    #     id=post.id,
    #     title=post.title,
    #     content=post.content,
    #     image_url=post.image_url,
    #     author_id=post.author_id,
    #     created_at=post.created_at,
    #     updated_at=post.updated_at,
    #     threads_count=post.threads_count,
    #     author=pyd.UserThreadSchema(
    #         user_name=post.author.user_name,
    #         role=post.author.role.role_name,
    #     ),
    #     threads=[],
    # )
    # responce_post.threads = build_thread_tree(post.threads)
    # print(responce_post)
    return responce_post
