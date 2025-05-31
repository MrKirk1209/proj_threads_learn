from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, text
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
from typing import Annotated, List
import app.models.models as m
from app.database import get_db
import pyd
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.security import authenticate_user, create_access_token, get_password_hash
from app.security import get_current_user
from app.config import settings
from sqlalchemy import func

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


@user_router.post("", response_model=pyd.Token, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: pyd.CreateUser, db: AsyncSession = Depends(get_db)):
    # print(user_data.user_password)
    hashed_password = get_password_hash(user_data.user_password)

    stmt = select(m.Role).where(m.Role.role_name == "user")
    result = await db.execute(stmt)
    role = result.scalars().first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль user не найдена",
        )
    new_user = m.User(
        email=user_data.email,
        user_name=user_data.user_name,
        user_password=hashed_password,
        role_id=role.id,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email или имя пользователя уже существует",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id)}, expires_delta=access_token_expires
    )
    print(f"Created user: {new_user.user_name} with id: {new_user.id}")
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/posts", response_model=List[pyd.PostSchema])
async def get_all_post(
    db: AsyncSession = Depends(get_db), current_user: m.User = Depends(get_current_user)
):
    # Явно загружаем связанные данные
    stmt = (
        select(m.Post)
        .where(m.Post.author_id == current_user.id)
        .options(
            # selectinload(m.Post.author),
        )
        .order_by(m.Post.id)
        .limit(100)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    return users


@user_router.get("/threads", response_model=List[pyd.ThreadSendSchema])
async def get_all_threads(
    db: AsyncSession = Depends(get_db), current_user: m.User = Depends(get_current_user)
):
    # Явно загружаем связанные данные
    stmt = (
        select(m.Thread)
        .where(m.Thread.creator_id == current_user.id)
        .options(
            selectinload(m.Thread.user),
            selectinload(m.Thread.post),
            subqueryload(m.Thread.parent),
        )
        .order_by(m.Thread.id)
        .limit(100)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    return users


@user_router.get("/me", response_model=pyd.UserInfo)
async def get_current_user_info(
    current_user: m.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о текущем пользователе.
    """
    cur_user = (
        (
            await db.execute(
                select(m.User)
                .options(
                    selectinload(m.User.role),
                )
                .where(m.User.id == current_user.id)
            )
        )
        .scalars()
        .first()
    )
    if not cur_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    q = text(
        """
        SELECT count(creator_id) AS threads_count
        FROM threads t
        
        WHERE t.creator_id = :user_id
        """
    )
    res = await db.execute(q, {"user_id": cur_user.id})
    threads_count = res.scalar() if res else 0

    q = text(
        """
        SELECT count(author_id) AS posts_count
        FROM posts p
        WHERE p.author_id = :user_id
        """
    )
    res = await db.execute(q, {"user_id": cur_user.id})
    post_count = res.scalar() if res else 0

    return pyd.UserInfo(
        id=cur_user.id,
        email=cur_user.email,
        user_name=cur_user.user_name,
        role=cur_user.role.role_name,
        threads_count=threads_count,
        posts_count=post_count,
    )


async def get_count(q):
    count_q = await q.statement.with_only_columns([func.count()]).order_by(None)
    count = await q.session.execute(count_q).scalar()
    return count


# @user_router.post("/login", response_model=pyd.UserSchema)
# async def login_user(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#     db: AsyncSession = Depends(get_db),
# ):
#     user = authenticate_user(form_data.username, form_data.password, db)

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Неверные имя пользователя или пароль",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(
#         data={"sub": user.id}, expires_delta=timedelta(minutes=30)
#     )
#     return pyd.Token(access_token=access_token, token_type="bearer")
