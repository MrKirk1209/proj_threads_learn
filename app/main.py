from typing import Union

from fastapi import FastAPI
from .routers import user_router, thread_router

app = FastAPI()


app.include_router(
    user_router,
)
app.include_router(
    thread_router,
)
