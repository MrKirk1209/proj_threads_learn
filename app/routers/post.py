from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import List
import app.models.models as m
from app.database import get_db
from app.routers.thread import build_thread_tree, get_threads_by_post_id
import pyd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc
from app.security import get_current_user
from fastapi.responses import JSONResponse
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError

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


@post_router.get("", response_model=pyd.PostShemaAdvanced, status_code=200)
async def get_all_post_sort(
    sort: str | None = None,
    search: str | None = Query(None),
    category: str | None = Query(None),
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    # 1) Начальный запрос к таблице Post (без OFFSET/LIMIT)
    base_stmt = select(m.Post).options(selectinload(m.Post.author))

    if category:
        category_db = (
            await db.execute(select(m.Category).where(m.Category.name == category))
        ).scalar_one_or_none()
        print("Category:", category)
        if not category_db:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        base_stmt = base_stmt.where(m.Post.category_id == category_db.id)
    # print("Base stmt:", base_stmt.compile(compile_kwargs={"literal_binds": True}))
    # 2) Если есть поисковая строка — добавляем WHERE
    if search:

        ilike_pattern = f"%{search}%"
        base_stmt = base_stmt.where(
            or_(
                m.Post.title.ilike(ilike_pattern),
                m.Post.content.ilike(ilike_pattern),
            )
        )

    # 3) Сначала считаем общее количество (без пагинации)
    count_stmt = select(func.count()).select_from(m.Post)
    if search or category:
        count_stmt = select(func.count()).select_from(base_stmt.subquery())

    # 3) Сначала считаем общее количество (без пагинации)
    # if search or category:
    #     count_result = await db.execute(count_stmt)
    # count_sql = text(
    #     """
    #     SELECT COUNT(*)
    #     FROM posts
    #     WHERE title ILIKE :pattern OR content ILIKE :pattern
    # """
    # )
    # params = {"pattern": f"%{search}%"}
    # count_result = await db.execute(count_sql, params)
    # else:
    # print("No search")
    # count_sql = text("SELECT COUNT(*) FROM posts")
    # count_result = await db.execute(count_sql)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0
    # print("Total:", total)

    # 4) Теперь применяем сортировку к базовому запросу и добавляем пагинацию
    match sort:
        case "recent":
            base_stmt = base_stmt.order_by(desc(m.Post.created_at))
        case "relevant":
            base_stmt = base_stmt.order_by(desc(m.Post.threads_count))
        case "old":
            base_stmt = base_stmt.order_by(asc(m.Post.created_at))
        case _:
            base_stmt = base_stmt.order_by(m.Post.id)

    paginated_stmt = base_stmt.offset(offset).limit(limit)
    result = await db.execute(paginated_stmt)
    posts = result.scalars().all()

    # 5) Подготавливаем JSON-ответ и прикладываем заголовок X-Total-Count
    payload = [
        pyd.postSchemaWithAuthor(
            id=post.id,
            title=post.title,
            content=post.content,
            category_id=post.category_id,
            image_url=post.image_url,
            author_id=post.author_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
            threads_count=post.threads_count,
            author=pyd.UserThreadSchema(user_name=post.author.user_name),
        ).model_dump(mode="json")
        for post in posts
    ]

    return JSONResponse(
        content={
            "posts": payload,
            "total": total,
        }
    )


@post_router.get(
    "/{post_id}",
    response_model=pyd.PostSchemaWithThreads,
)
async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(m.Post)
        .where(m.Post.id == post_id)
        .options(
            selectinload(m.Post.threads).selectinload(
                m.Thread.children, recursion_depth=4
            ),
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


@post_router.post("", response_model=pyd.PostSchema, status_code=201)
async def create_post(
    post_data: pyd.CreatePost,
    current_user: m.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category_db = None

    if post_data.category:
        category_db = (
            (
                await db.execute(
                    select(m.Category).where(m.Category.name == post_data.category)
                )
            )
            .scalars()
            .first()
        )

    # Создаём новый пост
    new_post = m.Post(
        content=post_data.content,
        title=post_data.title,
        image_url=post_data.image_url,
        author_id=current_user.id,
    )

    if post_data.category and category_db:
        new_post.category_id = category_db.id
    try:
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        new_post = pyd.PostSchema(
            **new_post.__dict__,
            user=pyd.UserThreadSchema(
                user_name=current_user.user_name,
            ),
        )
    except IntegrityError as e:
        await db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Пост с таким названием уже существует",
        )

    return new_post
