from datetime import datetime
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
    # role: Optional[str] = Field(None, alias="role")


class UserSchema(UserBase):
    role: Optional[RoleBase] = None
    posts: Optional[List[PostBase]] = Field(None, alias="posts")
    user_password: Optional[str] = Field(None, exclude=True)
    threads: Optional[List[ThreadBase]] = None


class UserInfo(BaseModel):
    id: int = Field(None, gt=0, example=1)
    user_name: str = Field(..., max_length=255, example="kolbasa")
    email: str = Field(..., max_length=255, example="kolbasa@gmail.com")
    role: Optional[str] = Field(None, alias="role")
    threads_count: int = Field(None, gt=0, example=10)
    posts_count: int = Field(None, gt=0, example=5)


class RoleSchema(RoleBase):
    id: int = Field(None, gt=0, example=1)
    role_name: str = Field(None, max_length=255)


class PostSchema(PostBase): ...


class PostShemaAdvanced(BaseModel):
    posts: List[PostSchema] = Field(None, alias="posts")
    total_count: int = Field(None, gt=0, example=10)


class CategorySchema(CategoryBase): ...


class postSchemaWithAuthor(PostBase):
    author: Optional[UserThreadSchema] = Field(None, alias="author")


class PostSchemaWithThreads(PostBase):
    threads: Optional[List["ThreadSchema"]] = Field(None, alias="threads")
    author: Optional[UserThreadSchema] = Field(None, alias="author")


class Token(BaseModel):
    access_token: str
    token_type: str


class ThreadSchema(ThreadBase):
    user: UserThreadSchema = Field(None)
    # post: Optional[PostBase] = Field(None)
    children: Optional[List["ThreadSchema"]] = None


class ThreadSendSchema(ThreadBase):
    parent: Optional["ThreadBase"] = None
    # children: Optional[List["ThreadBase"]] = None
    user: UserThreadSchema = Field(None)
    post: Optional[PostBase] = Field(None)

    class Config:

        from_attributes = True


class PostCreateSchema(PostBase):
    title: str = Field(..., max_length=255)
    content: str = Field(None)
    category: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class FileResponseSchema(BaseModel):
    url: str = Field(..., example="https://example.com/file.jpg")


ThreadSchema.model_rebuild()
