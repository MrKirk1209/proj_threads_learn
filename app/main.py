from typing import Union

from fastapi import FastAPI
from .routers import user_router,role_router,post_router

app = FastAPI()




app.include_router(
    user_router,
    
)

app.include_router(
    role_router,
)

app.include_router(
    post_router,
)

