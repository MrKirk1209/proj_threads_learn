from sqladmin import Admin, ModelView
from app.models.models import User,Role
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

class RolesAdmin(ModelView, model=Role):
    column_list = [
        'id', 'role_name'
    ]
    column_labels = {
        'id': 'ID',
        'role_name': 'Название роли', 

    }