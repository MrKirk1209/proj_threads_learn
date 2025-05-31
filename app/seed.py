import asyncio
import random
import sys
from app.database import async_session_maker  # Импорт твоего session maker
from app.models.models import Category, User, Role, Post, Thread  # Импорт твоих моделей
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from faker import Faker


faker = Faker()

NUM_USERS = 20
NUM_POSTS = 500
THREADS_PER_POST = 4
CHILD_THREADS_PER_POST = 4
NUM_CATEGORIES = 5

#     async with async_session_maker() as session:  # Используем твой async_session_maker
#         async with session.begin():  # BEGIN TRANSACTION
#             # 1. Создание ролей
#             admin_role = Role(role_name="admin")
#             user_role = Role(role_name="user")
#             session.add_all([admin_role, user_role])
#             await session.flush()  # Нужно получить id для ролей

#             # 2. Создание пользователей
#             admin_user = User(
#                 email="admin@example.com",
#                 user_name="Admin",
#                 user_password="hashedpassword1",  # Лучше потом захешировать через bcrypt
#                 role_id=admin_role.id,
#             )
#             regular_user = User(
#                 email="user@example.com",
#                 user_name="User",
#                 user_password="hashedpassword2",
#                 role_id=user_role.id,
#             )
#             session.add_all([admin_user, regular_user])
#             await session.flush()

#             # 3. Создание поста
#             post1 = Post(
#                 author_id=admin_user.id,
#                 title="Welcome to the Forum",
#                 content="Welcome to our new forum!",
#                 image_url="sdasddds",
#             )
#             session.add(post1)
#             await session.flush()

#             # 4. Создание треда
#             thread1 = Thread(
#                 content="First comment here!",
#                 creator_id=regular_user.id,
#                 image_url="sadsd",
#                 parent_id=None,
#                 post_id=post1.id,
#             )
#             session.add(thread1)

#         await session.commit()


async def seed_users(session: AsyncSession) -> list[User]:
    users = []
    for _ in range(NUM_USERS):
        user = User(
            user_name=faker.user_name(),
            email=faker.email(),
            user_password="hashedpassword",
            role_id=random.randint(9, 10),  # Можно потом сделать фейковый хэш
        )
        session.add(user)
        users.append(user)

    await session.commit()
    return users


async def seed_categories(session: AsyncSession) -> list[Category]:
    categories = []
    for _ in range(NUM_CATEGORIES):
        category = Category(name=faker.word())
        session.add(category)
        categories.append(category)

    await session.commit()
    return categories


async def seed_posts(session: AsyncSession, users: list[User]) -> list[Post]:
    posts = []
    categories = await seed_categories(session)
    for _ in range(NUM_POSTS):
        post = Post(
            title=faker.sentence(nb_words=6),
            content=faker.paragraph(nb_sentences=5),
            author_id=random.choice(users).id,
            image_url=faker.image_url(),
        )
        post.category = random.choice(categories)
        session.add(post)
        posts.append(post)

    await session.commit()
    return posts


async def seed_threads(
    session: AsyncSession, users: list[User], posts: list[Post]
) -> None:
    MAX_DEPTH = 3  # максимальная глубина вложенности
    THREADS_PER_POST = 20  # сколько "начальных" веток на пост

    async def create_thread(post_id: int, parent_id: int | None, depth: int = 0):
        thread = Thread(
            content=faker.text(max_nb_chars=250),
            creator_id=random.choice(users).id,
            parent_id=parent_id,
            image_url=faker.image_url(),
            post_id=post_id,
        )
        session.add(thread)
        await session.flush()  # чтобы получить id

        # Если ещё не достигли максимальной глубины — рекурсивно создать детей
        if depth < MAX_DEPTH:
            num_children = random.randint(0, 3)  # от 0 до 3 детей у одного треда
            for _ in range(num_children):
                await create_thread(post_id, thread.id, depth + 1)

    for post in posts:
        for _ in range(THREADS_PER_POST):
            await create_thread(post_id=post.id, parent_id=None)

    await session.commit()


async def seed_all():
    async with async_session_maker() as session:
        users = await seed_users(session)
        posts = await seed_posts(session, users)
        await seed_threads(session, users, posts)


if __name__ == "__main__":
    asyncio.run(seed_all())
    print("Database seeded successfully!")
