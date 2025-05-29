from fastapi import UploadFile, File, APIRouter,HTTPException
import shutil
import uuid
import os

import pyd
from app.config import settings

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

upload_router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
)
DOMAIN = settings.domain


@upload_router.post("", response_model=pyd.FileResponseSchema)
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Файл не должен превышать 5МБ")
    await file.seek(0)


    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url = f"{DOMAIN}/uploads/{filename}"
    return {"url": url}
