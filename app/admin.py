from sqladmin import Admin, ModelView

from app.models.models import User,Role,Post,Category,Thread

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
#This page will implement the authentication for your admin pannel
from app.security import verify_password
from app.security import authenticate_user, create_access_token, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, List
import pyd
from datetime import timedelta
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import relationship, selectinload, subqueryload, Session
import app.models.models as m
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        # print(username, password)
        # Получаем асинхронный генератор
        db_generator = get_db()
        
        try:
            # Получаем сессию из генератора
            db: AsyncSession = await db_generator.__anext__()
        except StopAsyncIteration:
            db = None
        
        if not db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

        try:
            stmt = (
                select(User)
                .options(
            selectinload(User.role),
                    )
                .where(User.user_name == username)
            )
            result = await db.execute(stmt)
            user = result.scalars().first()
            # print(user)
            if not user or not verify_password(password, user.user_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверные учетные данные"
                )
            if user.role.role_name != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Доступ запрещен"
                )
            access_token = create_access_token(
                data={"sub": str(user.id)}, 
                expires_delta=timedelta(minutes=30)
            )
            request.session.update({"token": access_token})
            return True
            
        finally:
            # Закрываем генератор
            await db_generator.aclose()
    async def logout(self, request: Request):
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        token = request.session.get("token")
        return token is not None
    
# create a view for your models
class UsersAdmin(ModelView, model=User):
    column_list = [
        'id', 'email', 'user_name', 'user_password', 'role.role_name'
    ]
    can_export = True
    column_labels = {
        'id': 'ID',
        'email': 'Почта',
        'user_name': 'Имя',
        'user_password': 'Пароль',
        'role.role_name': 'Роль'
    }

# class User(Base):
#     id: Mapped[int_pk]
#     email: Mapped[str_uniq]
#     user_name: Mapped[str_uniq]
#     user_password: Mapped[str]
#     role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

#     role: Mapped["Role"] = relationship(
#         "Role",
#         back_populates="users",
#     )
#     posts: Mapped[list["Post"]] = relationship(
#         "Post", back_populates="author", cascade="all, delete"
#     )
#     threads: Mapped[list["Thread"]] = relationship(
#         "Thread", back_populates="user", cascade="all, delete"
#     )

#     def __repr__(self):
#         return f"User(id={self.id}, email={self.email})"
class RolesAdmin(ModelView, model=Role):
    column_list = [
        'id', 'role_name'
    ]
    column_labels = {
        'id': 'ID',
        'role_name': 'Название роли', 

    }
    can_export = True
#class Role(Base):
#     id: Mapped[int_pk]
#     role_name: Mapped[str_uniq]

#     users: Mapped[list["User"]] = relationship(
#         "User", back_populates="role", cascade="all, delete"
#     )

#     def __repr__(self):
#         return f"role(id={self.id}, role_name={self.role_name})"

class PostAdmin(ModelView, model=Post):
    column_list = [
        'id', 'title', 'content', 'image_url', 'threads_count'
    ]
    column_labels = {
        'id': 'ID',
        'title': 'Заголовок',
        'content': 'Текст',
        'image_url': 'URL картинки',
        'threads_count': 'Количество комментариев',

    }
    can_export = True
#     class Post(Base):
#     id: Mapped[int_pk]
#     title: Mapped[str_uniq]
#     content: Mapped[str] = mapped_column(Text, nullable=False)
#     image_url: Mapped[str] = mapped_column(default=None, nullable=True)
#     threads_count: Mapped[int] = mapped_column(server_default=text("0"))

#     category_id: Mapped[int] = mapped_column(ForeignKey("categorys.id"), nullable=True)
#     author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

#     author: Mapped["User"] = relationship(
#         "User",
#         back_populates="posts",
#     )
#     # address: Mapped[str]

#     threads: Mapped[list["Thread"]] = relationship(
#         "Thread", back_populates="post", cascade="all, delete"
#     )

#     category: Mapped["Category"] = relationship("Category", back_populates="posts")

#     # enrollment_year: Mapped[int]
#     # course: Mapped[int]
#     # special_notes: Mapped[str_null_true]

#     # def __str__(self):
#     #     return (f"{self.__class__.__name__}(id={self.id}, "
#     #             f"first_name={self.first_name!r},"
#     #             f"last_name={self.last_name!r})")

#     def __repr__(self):
#         return f"Post(id={self.id}, title={self.title})"

class ThreadAdmin(ModelView, model=Thread):
    column_list = [
        'id',  'content', 'image_url', 'creator_id', 'parent_id', 'post_id'
    ]
    column_labels = {
        'id': 'ID',
        'content': 'Текст',
        'image_url': 'URL картинки',
        'creator_id': 'ID автора',
        'parent_id': 'ID родительского треда',
        'post_id': 'ID поста',

    }
    can_export = True
# # Таблица Тредов
# class Thread(Base):
#     id: Mapped[int_pk]
#     content: Mapped[str] = mapped_column(Text, nullable=False)
#     image_url: Mapped[str] = mapped_column(default=None, nullable=True)

#     creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
#     parent_id: Mapped[int] = mapped_column(ForeignKey("threads.id"), nullable=True)
#     post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)

#     post: Mapped["Post"] = relationship("Post", back_populates="threads")
#     user: Mapped["User"] = relationship("User", back_populates="threads")
#     parent: Mapped["Thread"] = relationship(
#         "Thread", back_populates="children", remote_side="Thread.id"
#     )
#     children: Mapped[list["Thread"]] = relationship(
#         "Thread", back_populates="parent", cascade="all, delete-orphan"
#     )

#     def __repr__(self):
#         return f"Thread(id={self.id})"

#     # count_students: Mapped[int] = mapped_column(server_default=text('0'))

#     # def __str__(self):
#     #     return f"{self.__class__.__name__}(id={self.id}, major_name={self.major_name!r})"


class CategoryAdmin(ModelView, model=Category):
    column_list = [
        'id', 'name', 'posts_count'
    ]
    column_labels = {
        'id': 'ID',
        'name': 'Название',
        'posts_count': 'Количество постов',

    }
    can_export = True

# class Category(Base):
#     id: Mapped[int_pk]
#     name: Mapped[str_uniq]
#     posts_count: Mapped[int] = mapped_column(server_default=text("0"))

#     posts: Mapped[list["Post"]] = relationship(
#         "Post", back_populates="category", cascade="all, delete"
#     )