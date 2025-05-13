from typing import Union

from fastapi import FastAPI
from sqladmin import Admin
from .routers import user_router, thread_router, role_router, post_router, auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.admin import AdminAuth, UsersAdmin,RolesAdmin
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    user_router,
)

app.include_router(
    role_router,
)

app.include_router(
    post_router,
)

app.include_router(
    thread_router,
)

app.include_router(auth_router)

# add the views to admin
def create_admin(app):
    authentication_backend = AdminAuth(secret_key="tableadmin")
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(UsersAdmin)
    admin.add_view(RolesAdmin)
    
    return admin
create_admin(app)