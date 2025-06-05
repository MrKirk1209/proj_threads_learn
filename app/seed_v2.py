import asyncio
import random
from app.database import async_session_maker
from app.models.models import Category, User, Role, Post, Thread
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from faker import Faker

faker = Faker()

# Конфигурация
NUM_USERS = 20
NUM_POSTS = 50  # Уменьшено для натуральности
THREADS_PER_POST = 4
CHILD_THREADS_PER_POST = 3
NUM_CATEGORIES = 5

# Натуральные данные
CATEGORIES = [
    "Физика",
    "Математика",
    "Программирование",
    "Химия",
]


POST_TITLES = {
    "Физика": [
        "Помогите с задачей по термодинамике",
        "Вопрос по закону Ома",
        "Объясните теорию относительности",
        "Задачи на движение тела под углом",
        "Разбор задачи по квантовой физике",
    ],
    "Математика": [
        "Интегралы сложные",
        "Теория вероятностей - задача",
        "Геометрия 10 класс",
        "Помогите решить уравнение",
        "Математический анализ пределы",
    ],
    "Программирование": [
        "Ошибка в Python коде",
        "Оптимизация алгоритма на C++",
        "Как сделать REST API?",
        "Проблема с асинхронностью",
        "Выбор фреймворка для проекта",
    ],
    "Химия": [
        "Органическая химия - реакции",
        "Задачи по молярной массе",
        "Цепочка превращений",
        "Электрохимические процессы",
        "Расчет pH раствора",
    ],
}

POST_CONTENTS = {
    "request": [
        "Не могу разобраться с этой задачей, помогите пожалуйста. Условие: {problem}",
        "Столкнулся с проблемой: {problem}. Кто может объяснить решение?",
        "Пытаюсь решить {problem}, но не получается. Нужна помощь!",
        "Может кто-то сталкивался с подобной проблемой? {problem}",
    ],
    "solution": [
        "Хочу поделиться решением задачи: {problem}\n\nРешение:\n{solution}",
        "Нашел интересный способ решения {problem}:\n{solution}",
        "Предлагаю свое решение для {problem}:\n{solution}",
        "Разобрался с задачей, вот решение: {problem}\n{solution}",
    ],
}

THREAD_CONTENTS = [
    "Я тоже столкнулся с этой проблемой, спасибо за решение!",
    "Можно поподробнее о втором шаге решения?",
    "У меня есть альтернативный способ решения...",
    "Спасибо, очень помогло!",
    "А есть более оптимальное решение?",
    "Не понятен третий пункт, можете объяснить?",
    "Отличное решение, добавил в закладки!",
    "А как это применить к похожей задаче?",
    "У меня выдает ошибку при таком подходе...",
    "Благодарю за помощь, разобрался!",
]

PROBLEMS = {
    "Физика": [
        "Тело массой 2 кг движется с ускорением 3 м/с². Найдите силу, действующую на тело.",
        "Рассчитайте сопротивление цепи при последовательном соединении резисторов 10 Ом и 15 Ом.",
        "Какая работа совершается при подъеме груза массой 5 кг на высоту 2 м?",
    ],
    "Математика": [
        "Решите уравнение: x² - 5x + 6 = 0",
        "Найдите производную функции f(x) = 3x³ - 2x² + 5x - 7",
        "Вычислите интеграл ∫(2x + 3)dx от 0 до 1",
    ],
    "Программирование": [
        "Напишите функцию на Python, которая реверсирует строку",
        "Как оптимизировать алгоритм поиска кратчайшего пути?",
        "Реализуйте бинарный поиск на C++",
    ],
    "Химия": [
        "Составьте уравнение реакции горения пропана",
        "Рассчитайте массовую долю вещества в растворе",
        "Определите тип гибридизации атома углерода в молекуле метана",
    ],
}

SOLUTIONS = {
    "Физика": [
        "По второму закону Ньютона: F = m*a = 2 кг * 3 м/с² = 6 Н",
        "При последовательном соединении: Rобщ = R1 + R2 = 10 + 15 = 25 Ом",
        "A = m*g*h = 5 кг * 9.8 м/с² * 2 м = 98 Дж",
    ],
    "Математика": [
        "D = b² - 4ac = 25 - 24 = 1, x1 = (5+1)/2=3, x2=(5-1)/2=2",
        "f'(x) = 9x² - 4x + 5",
        "∫(2x+3)dx = x² + 3x | от 0 до 1 = (1+3) - (0+0) = 4",
    ],
    "Программирование": [
        "def reverse_string(s): return s[::-1]",
        "Использовать алгоритм Дейкстры с оптимизированной очередью с приоритетами",
        "int binary_search(int arr[], int l, int r, int x) { while (l <= r) { ... }}",
    ],
    "Химия": [
        "C3H8 + 5O2 → 3CO2 + 4H2O",
        "ω = (m_вещ / m_раствора) * 100%",
        "sp³-гибридизация",
    ],
}


async def seed_roles(session: AsyncSession) -> dict[str, Role]:
    admin_role = Role(role_name="admin")
    user_role = Role(role_name="user")
    session.add_all([admin_role, user_role])
    await session.flush()
    return {"admin": admin_role, "user": user_role}


async def seed_users(session: AsyncSession, roles: dict[str, Role]) -> list[User]:
    users = []
    for i in range(NUM_USERS):

        user = User(
            user_name=faker.user_name(),
            email=faker.email(),
            user_password="hashed_password",  # Заменить на реальный хэш в проде
            role_id=roles["admin"].id if i == 0 else roles["user"].id,
            created_at=datetime(2024, random.randint(1, 12), random.randint(1, 28)),
        )
        session.add(user)
        users.append(user)
    await session.commit()
    return users


async def seed_categories(session: AsyncSession) -> list[Category]:
    categories = []
    for name in CATEGORIES:
        category = Category(name=name)
        session.add(category)
        categories.append(category)
    await session.commit()
    return categories


async def seed_posts(
    session: AsyncSession, users: list[User], categories: list[Category]
) -> list[Post]:
    posts = []
    used_titles = set()  # Для отслеживания уже использованных заголовков

    for _ in range(NUM_POSTS):
        category = random.choice(categories)
        post_type = random.choice(["request", "solution"])

        problem = random.choice(PROBLEMS[category.name])
        solution = (
            random.choice(SOLUTIONS[category.name]) if post_type == "solution" else ""
        )

        # Генерируем уникальный заголовок
        max_attempts = 10
        for _ in range(max_attempts):
            title = random.choice(POST_TITLES[category.name])
            if title not in used_titles:
                used_titles.add(title)
                break
        else:
            # Если не удалось сгенерировать уникальный заголовок за max_attempts попыток
            title = f"{random.choice(POST_TITLES[category.name])} ({random.randint(1, 1000)})"
            used_titles.add(title)

        content_template = random.choice(POST_CONTENTS[post_type])
        content = content_template.format(problem=problem, solution=solution)

        post = Post(
            title=title,
            content=content,
            author_id=random.choice(users).id,
            image_url=None,
            category_id=category.id,
            created_at=datetime(2024, random.randint(1, 12), random.randint(1, 28)),
        )
        session.add(post)
        posts.append(post)

    await session.commit()
    return posts


async def seed_threads(
    session: AsyncSession, users: list[User], posts: list[Post]
) -> None:
    def generate_thread_content(parent_id=None):
        if parent_id:
            # Для ответов используем более конкретные формулировки
            replies = [
                "Спасибо за уточнение!",
                "А если изменить параметры?",
                "Проверил, работает!",
                "Не совсем понял этот момент...",
                "Дополню: есть еще один способ...",
                "У меня аналогичный результат",
            ]
            return random.choice(replies)
        return random.choice(THREAD_CONTENTS)

    for post in posts:
        # Создаем корневые треды
        root_threads = []
        for _ in range(random.randint(2, THREADS_PER_POST)):
            thread = Thread(
                content=generate_thread_content(),
                creator_id=random.choice(users).id,
                parent_id=None,
                post_id=post.id,
                created_at=datetime(2024, random.randint(1, 12), random.randint(1, 28)),
            )
            session.add(thread)
            root_threads.append(thread)

        await session.flush()

        # Создаем дочерние треды
        for root_thread in root_threads:
            for _ in range(random.randint(0, CHILD_THREADS_PER_POST)):
                child_thread = Thread(
                    content=generate_thread_content(parent_id=True),
                    creator_id=random.choice(users).id,
                    parent_id=root_thread.id,
                    post_id=post.id,
                    created_at=datetime(
                        2024, random.randint(1, 12), random.randint(1, 28)
                    ),
                )
                session.add(child_thread)

    await session.commit()


async def seed_all():
    async with async_session_maker() as session:
        roles = await seed_roles(session)
        users = await seed_users(session, roles)
        categories = await seed_categories(session)
        posts = await seed_posts(session, users, categories)
        await seed_threads(session, users, posts)


if __name__ == "__main__":
    asyncio.run(seed_all())
    print("Database seeded successfully with natural data!")
