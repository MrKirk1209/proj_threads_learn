from pydantic import BaseModel, Field
from typing import List


# тут модели которые используются при создании/редактировании сущностей
# class CategoryCreate(BaseModel):
#     name: str = Field(..., max_length=255, example='Еда')
#     description: str = Field(None, max_length=255, example='То что можно скушать')

#     class Config:
#         orm_mode = True


# class ProductCreate(BaseModel):
#     name: str = Field(..., max_length=255, example='Колбаса')
#     description: str = Field(None, max_length=255, example='Варенная колбаса, самая вкусная')
#     price: int = Field(..., gt=0, example=99.95)

#     category_ids: List[int] = None

#     class Config:
#         orm_mode = True


# class CreateUser(BaseModel):
#     username: str = Field(..., max_length=255, example='Колбаса')
#     password: str = Field(..., max_length=255, example='Колбаса')

#     class Config:
#         orm_mode = True
