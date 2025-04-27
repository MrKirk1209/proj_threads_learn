from sqlalchemy import ForeignKey, text, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true
from datetime import date


# Таблица постов
class Post(Base):
    id: Mapped[int_pk]
    title: Mapped[str_uniq] 
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship("User", back_populates="posts")
    # address: Mapped[str] 
    # enrollment_year: Mapped[int]
    # course: Mapped[int]
    # special_notes: Mapped[str_null_true]

    # def __str__(self):
    #     return (f"{self.__class__.__name__}(id={self.id}, "
    #             f"first_name={self.first_name!r},"
    #             f"last_name={self.last_name!r})")

    def __repr__(self):
        return str(self)

# Таблица Тредов
class Thread(Base):
    id: Mapped[int_pk]
    content: Mapped[str] = mapped_column(Text, nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey("threads.id"), nullable=True)
    image_url: Mapped[str]
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="threads")
    user: Mapped["User"] = relationship("User", back_populates="threads")
    parent: Mapped["Thread"] = relationship("Thread", back_populates="threads")

    # count_students: Mapped[int] = mapped_column(server_default=text('0'))

    # def __str__(self):
    #     return f"{self.__class__.__name__}(id={self.id}, major_name={self.major_name!r})"

    def __repr__(self):
        return str(self)


# Таблица Пользователей
class User(Base):
    id: Mapped[int_pk]
    email: Mapped[str_uniq] 
    user_name: Mapped[str_uniq] 
    user_password: Mapped[str] 
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="users")
class Role(Base):
    id: Mapped[int_pk]
    role_name: Mapped[str_uniq] 

    def __repr__(self):
        return str(self)
