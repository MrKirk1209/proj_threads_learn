from pydantic import BaseModel, Field


# файл с базовыми моделями

class CategoryBase(BaseModel):
    # Field используется для описания столбца, None - не обязательно, ... - обязательно
    # gt - больше чем, example - пример для доки
    id: int = Field(None, gt=0, example=1)
    name: str = Field(..., max_length=255, example='Еда')
    description: str = Field(None, max_length=255, example='То что можно скушать')

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    id: int = Field(None, gt=0, example=1)
    name: str = Field(..., max_length=255, example='Колбаса')
    description: str = Field(None, max_length=255, example='Варенная колбаса, самая вкусная')
    price: int = Field(..., gt=0, example=99.95)

    class Config:
        orm_mode = True


class BaseUser(BaseModel):
    id: int = Field(None, gt=0, example=1)
    username: str = Field(..., max_length=255, example='Колбаса')

    class Config:
        orm_mode = True