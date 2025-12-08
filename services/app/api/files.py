"""
文件管理API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io

from ..core.minio_client import minio_client

router = APIRouter()


class UploadResponse(BaseModel):
    """上传响应"""
    url: str
    path: str


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    path: Optional[str] = None
):
    """上传文件到MinIO"""
    content = await file.read()

    # 确定存储路径
    if path:
        object_name = path
    else:
        object_name = f"uploads/{file.filename}"

    # 上传
    url = minio_client.upload_file(
        content,
        object_name,
        file.content_type or "application/octet-stream"
    )

    return UploadResponse(url=url, path=object_name)


@router.get("/files/{path:path}")
async def get_file(path: str):
    """获取文件"""
    data = minio_client.download_file(path)

    if not data:
        raise HTTPException(status_code=404, detail="File not found")

    # 根据文件扩展名确定content type
    content_type = "application/octet-stream"
    if path.endswith(".png"):
        content_type = "image/png"
    elif path.endswith(".jpg") or path.endswith(".jpeg"):
        content_type = "image/jpeg"
    elif path.endswith(".json"):
        content_type = "application/json"

    return StreamingResponse(
        io.BytesIO(data),
        media_type=content_type
    )


@router.delete("/files/{path:path}")
async def delete_file(path: str):
    """删除文件"""
    success = minio_client.delete_file(path)

    if not success:
        raise HTTPException(status_code=404, detail="File not found")

    return {"message": "File deleted"}


@router.get("/files/{path:path}/url")
async def get_file_url(path: str, expires: int = 3600):
    """获取文件预签名URL"""
    url = minio_client.get_presigned_url(path, expires)

    if not url:
        raise HTTPException(status_code=404, detail="File not found")

    return {"url": url}
