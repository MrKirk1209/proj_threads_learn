# Находимся в ../proj_threads_learn

## Создание миграции
`alembic revision --autogenerate -m "Name migration"`

## Установка миграции
`alembic upgrade head`

## Посев(добавления начальных данных из seed.py)

`python -m app.seed`

## Подключение venv

 `.venv\scripts\activate`

## Установка зависимостей(библиотек)

`pip install -r requirements.txt`

