import asyncio
from app.database import async_session_maker  # Импорт твоего session maker
from app.models.models import User, Role, Post, Thread  # Импорт твоих моделей
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


async def seed():
    async with async_session_maker() as session:  # Используем твой async_session_maker
        async with session.begin():  # BEGIN TRANSACTION
            # 1. Создание ролей
            admin_role = Role(role_name="admin")
            user_role = Role(role_name="user")
            session.add_all([admin_role, user_role])
            await session.flush()  # Нужно получить id для ролей

            # 2. Создание пользователей
            admin_user = User(
                email="admin@example.com",
                user_name="Admin",
                user_password="hashedpassword1",  # Лучше потом захешировать через bcrypt
                role_id=admin_role.id,
            )
            regular_user = User(
                email="user@example.com",
                user_name="User",
                user_password="hashedpassword2",
                role_id=user_role.id,
            )
            session.add_all([admin_user, regular_user])
            await session.flush()

            # 3. Создание поста
            post1 = Post(
                author_id=admin_user.id,
                title="Welcome to the Forum",
                content="Welcome to our new forum!",
                image_url="sdasddds",
            )
            session.add(post1)
            await session.flush()

            # 4. Создание треда
            thread1 = Thread(
                content="First comment here!",
                creator_id=regular_user.id,
                image_url="sadsd",
                parent_id=None,
                post_id=post1.id,
            )
            session.add(thread1)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
    print("Database seeded successfully!")
