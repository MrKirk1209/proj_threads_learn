# вставка начальных данных
from sqlalchemy.orm import Session
from app.database import engine
import app.models.models as models

with Session(bind=engine) as session:
    cat1 = models.Category(name='Еда', description='Вкусная, для людей')
    cat2 = models.Category(name='Вода', description='Без вкуса, для людей')
    cat3 = models.Category(name='Одежда', description='Без стиля, для людей')

    prod1 = models.Product(name='Дошик', description='Не вкусный, для студентов', price=66.5,categories=[cat1])
    prod2 = models.Product(name='Святой источник', description='Обычная вода, для людей', price=33.4,categories=[cat2])
    prod3 = models.Product(name='Кепка ОДМО', description='Специально для ОДМОшников', price=350.0,categories=[cat3])
    session.add_all([cat1, cat2, cat3, prod1, prod2, prod3])
    session.commit()