"""
MinIO客户端
"""

import io
from typing import Optional
from minio import Minio
from minio.error import S3Error

from .config import settings


class MinIOClient:
    """MinIO客户端封装"""

    def __init__(self):
        self._client: Optional[Minio] = None

    def _get_client(self) -> Minio:
        """获取MinIO客户端"""
        if self._client is None:
            self._client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            # 确保bucket存在
            self._ensure_bucket()

        return self._client

    def _ensure_bucket(self):
        """确保bucket存在"""
        try:
            if not self._client.bucket_exists(settings.MINIO_BUCKET):
                self._client.make_bucket(settings.MINIO_BUCKET)
        except S3Error as e:
            print(f"MinIO bucket error: {e}")

    def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        上传文件

        Args:
            file_data: 文件数据
            object_name: 对象名称（路径）
            content_type: 内容类型

        Returns:
            MinIO URL
        """
        client = self._get_client()

        data = io.BytesIO(file_data)
        client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
            data=data,
            length=len(file_data),
            content_type=content_type
        )

        return f"minio://{settings.MINIO_BUCKET}/{object_name}"

    def download_file(self, object_name: str) -> Optional[bytes]:
        """
        下载文件

        Args:
            object_name: 对象名称（路径）

        Returns:
            文件数据
        """
        client = self._get_client()

        try:
            response = client.get_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=object_name
            )
            return response.read()
        except S3Error as e:
            print(f"MinIO download error: {e}")
            return None
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

    def delete_file(self, object_name: str) -> bool:
        """
        删除文件

        Args:
            object_name: 对象名称（路径）

        Returns:
            是否成功
        """
        client = self._get_client()

        try:
            client.remove_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=object_name
            )
            return True
        except S3Error as e:
            print(f"MinIO delete error: {e}")
            return False

    def list_objects(self, prefix: str = "") -> list[str]:
        """
        列出对象

        Args:
            prefix: 前缀

        Returns:
            对象名称列表
        """
        client = self._get_client()

        objects = []
        try:
            for obj in client.list_objects(
                bucket_name=settings.MINIO_BUCKET,
                prefix=prefix,
                recursive=True
            ):
                objects.append(obj.object_name)
        except S3Error as e:
            print(f"MinIO list error: {e}")

        return objects

    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600
    ) -> Optional[str]:
        """
        获取预签名URL

        Args:
            object_name: 对象名称
            expires: 过期时间（秒）

        Returns:
            预签名URL
        """
        client = self._get_client()

        try:
            from datetime import timedelta
            url = client.presigned_get_object(
                bucket_name=settings.MINIO_BUCKET,
                object_name=object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            print(f"MinIO presigned URL error: {e}")
            return None


minio_client = MinIOClient()
