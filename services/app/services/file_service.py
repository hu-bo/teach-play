"""文件服务"""

from __future__ import annotations

import uuid
from typing import Optional

import httpx
from sqlalchemy import select

from ..core.config import settings
from ..core.database import session_scope
from ..core.minio_client import minio_client
from ..db.models import FileInfoRecord
from ..models.file import FileInfo


class FileService:
    """管理 MinIO 文件及元数据"""

    @staticmethod
    def _build_object_url(object_path: str) -> str:
        scheme = "https" if settings.MINIO_SECURE else "http"
        return f"{scheme}://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{object_path}"

    @staticmethod
    def _to_model(record: FileInfoRecord) -> FileInfo:
        return FileInfo(
            id=record.id,
            bucket=record.bucket,
            path=record.object_path,
            url=record.url,
            content_type=record.content_type,
            size=record.size,
            checksum=record.checksum,
            project_id=record.project_id,
            recording_id=record.recording_id,
            created_at=record.created_at,
        )

    @staticmethod
    def register_file(
        object_path: str,
        *,
        content_type: str = "application/octet-stream",
        size: int = 0,
        project_id: Optional[str] = None,
        recording_id: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> FileInfo:
        """写入或更新文件元数据"""
        with session_scope() as session:
            stmt = select(FileInfoRecord).where(FileInfoRecord.object_path == object_path)
            record = session.scalars(stmt).first()

            if record:
                record.content_type = content_type
                record.size = size
                record.checksum = checksum
                record.project_id = project_id
                record.recording_id = recording_id
                record.bucket = settings.MINIO_BUCKET
                record.url = FileService._build_object_url(object_path)
            else:
                record = FileInfoRecord(
                    id=f"file_{uuid.uuid4().hex[:8]}",
                    object_path=object_path,
                    bucket=settings.MINIO_BUCKET,
                    url=FileService._build_object_url(object_path),
                    content_type=content_type,
                    size=size,
                    checksum=checksum,
                    project_id=project_id,
                    recording_id=recording_id,
                )
                session.add(record)

            session.flush()
            session.refresh(record)
            info = FileService._to_model(record)

        FileService.verify_downloadable(object_path)
        return info

    @staticmethod
    def get_file(object_path: str) -> Optional[FileInfo]:
        with session_scope() as session:
            stmt = select(FileInfoRecord).where(FileInfoRecord.object_path == object_path)
            record = session.scalars(stmt).first()
            return FileService._to_model(record) if record else None

    @staticmethod
    def delete_file(object_path: str) -> bool:
        with session_scope() as session:
            stmt = select(FileInfoRecord).where(FileInfoRecord.object_path == object_path)
            record = session.scalars(stmt).first()
            if not record:
                return False
            session.delete(record)
        return True

    @staticmethod
    def list_files(
        *,
        project_id: Optional[str] = None,
        recording_id: Optional[str] = None,
    ) -> list[FileInfo]:
        with session_scope() as session:
            stmt = select(FileInfoRecord)
            if project_id:
                stmt = stmt.where(FileInfoRecord.project_id == project_id)
            if recording_id:
                stmt = stmt.where(FileInfoRecord.recording_id == recording_id)
            records = session.scalars(stmt).all()
            return [FileService._to_model(record) for record in records]

    @staticmethod
    def verify_downloadable(object_path: str) -> bool:
        """通过预签名地址检查 MinIO 是否可访问"""
        url = minio_client.get_presigned_url(object_path, expires=60)
        if not url:
            return False

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.head(url)
                return response.is_success
        except httpx.HTTPError as exc:
            print(f"MinIO download check failed for {object_path}: {exc}")
            return False
