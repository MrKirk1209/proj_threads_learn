from pydantic import BaseModel, Field
from typing import Optional


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


class CreateUser(BaseModel):
    email: str = Field(..., max_length=255, example="kolbasa@gmail.com")
    user_name: str = Field(..., max_length=255, example="kolbasa")
    user_password: str = Field(..., min_length=8, exclude=True, max_length=255)

    class Config:
        orm_mode = True
        from_attributes = True


class CreateThread(BaseModel):
    content: str = Field(..., max_length=4096, example="Тред с контентом")
    image_url: Optional[str] = Field(
        None, max_length=255, example="https://example.com/image.jpg"
    )

    parent_id: Optional[int] = Field(None, gt=0, example=1)
