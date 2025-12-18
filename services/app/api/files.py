"""文件管理API"""

import io
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

from ..core.minio_client import minio_client
from ..models.file import FileInfo
from ..services.file_service import FileService

router = APIRouter()


@router.post("/upload", response_model=FileInfo)
async def upload_file(
    file: UploadFile = File(...),
    path: Optional[str] = None,
    project_id: Optional[str] = None,
    recording_id: Optional[str] = None,
):
    """上传文件到MinIO 并写入元数据"""
    content = await file.read()

    # 确定存储路径
    object_name = path or f"uploads/{file.filename}"

    # 上传
    minio_client.upload_file(
        content,
        object_name,
        file.content_type or "application/octet-stream"
    )

    return FileService.register_file(
        object_name,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        project_id=project_id,
        recording_id=recording_id,
    )


@router.get("/files/{bucket}/{path:path}")
async def get_file(bucket: str, path: str):
    """获取文件"""
    data = minio_client.download_file(path)
    if not data:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = FileService.get_file(path)
    content_type = file_info.content_type if file_info else "application/octet-stream"

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

    FileService.delete_file(path)

    return {"message": "File deleted"}


@router.get("/files/{path:path}/url")
async def get_file_url(path: str, expires: int = 3600):
    """获取文件预签名URL"""
    url = minio_client.get_presigned_url(path, expires)

    if not url:
        raise HTTPException(status_code=404, detail="File not found")

    return {"url": url}
