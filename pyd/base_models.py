from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    id: int = Field(None, gt=0, example=1)
    role_name: str = Field(None, max_length=255, example="Администратор")

    class Config:
        orm_mode = True
        from_attributes = True


class UserBase(BaseModel):
    id: int = Field(None, gt=0, example=1)
    user_name: str = Field(..., max_length=255, example="kolbasa")
    email: str = Field(..., max_length=255, example="kolbasa@gmail.com")
    user_password: Optional[str] = Field(None, min_length=8, max_length=255)
    role_id: int = Field(..., gt=0, examples=[1])

    class Config:
        orm_mode = True
        from_attributes = True


class PostBase(BaseModel):
    # Field используется для описания столбца, None - не обязательно, ... - обязательно
    # gt - больше чем, example - пример для доки
    id: int = Field(...)
    title: str = Field(..., max_length=255, examples=["Еда"])
    content: str = Field(None, examples=["То что можно скушать"])
    image_url: str = Field(None, examples=["https://example.com/image.jpg"])
    author_id: int = Field(..., gt=0)

    category_id: Optional[int] = Field(None, gt=0)

    created_at: datetime = Field(None)
    updated_at: datetime = Field(None)
    threads_count: int = Field(None)
    # author: User

    class Config:
        orm_mode = True
        from_attributes = True


class ThreadBase(BaseModel):
    id: int = Field(..., gt=0, example=1)
    content: str = Field(..., max_length=255, example="Варенная колбаса")
    image_url: str = Field(None, examples=["https://example.com/image.jpg"])
    creator_id: int = Field(..., gt=0, example=1)
    post_id: int = Field(..., gt=0, example=1)
    parent_id: Optional[int] = Field(None, example=1)

    class Config:
        orm_mode = True
        from_attributes = True

class CategoryBase(BaseModel):
    id: int = Field(None, gt=0, example=1)
    name: str = Field(..., max_length=255, example="Еда")
    # description: str = Field(None, max_length=255, example="То что можно скушать")

    class Config:
        orm_mode = True

# class ProductBase(BaseModel):
#     id: int = Field(None, gt=0, example=1)
#     name: str = Field(..., max_length=255, example="Колбаса")
#     description: str = Field(
#         None, max_length=255, example="Варенная колбаса, самая вкусная"
#     )
#     price: int = Field(..., gt=0, example=99.95)

#     class Config:
#         orm_mode = True


# class BaseUser(BaseModel):
#     id: int = Field(None, gt=0, example=1)
#     username: str = Field(..., max_length=255, example="Колбаса")

#     class Config:
#         orm_mode = True
