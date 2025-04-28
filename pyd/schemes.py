from .base_models import *
from typing import List, Optional
from pydantic import BaseModel, Field

# Схемы включают в себя ссылки на другие сущности для вложеного вывода
# их нужно выносить отдельно, чтобы избежать рекурсии в импорте
# class CategorySchema(CategoryBase):
#     products: List[ProductBase]


# class ProductSchema(ProductBase):
#     categories: List[CategoryBase]


class UserThreadSchema(BaseModel):
    user_name: str = Field(None, alias="user_name")
    role: Optional[str] = Field(None, alias="role")


class UserSchema(UserBase):
    role: Optional[RoleBase] = None
    posts: Optional[List[PostBase]] = Field(None, alias="posts")
    user_password: None = Field(None, exclude=True)
    threads: Optional[List[ThreadBase]] = None

    class Config:

        exclude = {"user_password"}  # исключаем пароль из ответа


class ThreadSchema(ThreadBase):
    user: UserThreadSchema = Field(None)
    post: Optional[PostBase] = Field(None)
    children: Optional[List["ThreadSchema"]] = None

    class Config:
        orm_mode = True
        from_attributes = True


ThreadSchema.model_rebuild()
