from .base_models import *
from typing import List, Optional

# Схемы включают в себя ссылки на другие сущности для вложеного вывода
# их нужно выносить отдельно, чтобы избежать рекурсии в импорте
# class CategorySchema(CategoryBase):
#     products: List[ProductBase]


# class ProductSchema(ProductBase):
#     categories: List[CategoryBase]


class UserSchema(UserBase):
    role: Optional[RoleBase] = None
    posts: Optional[List[PostBase]] = Field(None, alias="posts")
    user_password: Optional[str] = Field(None, exclude=True)
    threads: Optional[List[ThreadBase]] = None

    class Config:

        exclude = {"user_password"}  # исключаем пароль из ответа
