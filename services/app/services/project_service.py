"""项目服务"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select

from ..core.database import session_scope
from ..core.minio_client import minio_client
from ..db.models import ProjectRecord, RecordingRecord
from ..models.project import Project, ProjectCreate, ProjectUpdate
from .file_service import FileService


class ProjectService:
    """项目服务"""

    @staticmethod
    def _to_model(record: ProjectRecord) -> Project:
        recordings = [rec.id for rec in record.recordings]
        return Project(
            id=record.id,
            name=record.name,
            description=record.description,
            created_at=record.created_at,
            updated_at=record.updated_at,
            recordings=recordings,
        )

    @staticmethod
    def list_projects() -> list[Project]:
        """获取项目列表"""
        with session_scope() as session:
            stmt = select(ProjectRecord).order_by(ProjectRecord.created_at.asc())
            records = session.scalars(stmt).all()
            return [ProjectService._to_model(record) for record in records]

    @staticmethod
    def get_project(project_id: str) -> Optional[Project]:
        """获取项目详情"""
        with session_scope() as session:
            record = session.get(ProjectRecord, project_id)
            if not record:
                return None
            return ProjectService._to_model(record)

    @staticmethod
    def create_project(project_data: ProjectCreate) -> Project:
        """创建项目"""
        project = Project(
            name=project_data.name,
            description=project_data.description,
        )

        with session_scope() as session:
            record = ProjectRecord(
                id=project.id,
                name=project.name,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            session.add(record)

        return project

    @staticmethod
    def update_project(project_id: str, project_data: ProjectUpdate) -> Optional[Project]:
        """更新项目"""
        update_fields = project_data.model_dump(exclude_unset=True)
        if not update_fields:
            return ProjectService.get_project(project_id)

        with session_scope() as session:
            record = session.get(ProjectRecord, project_id)
            if not record:
                return None

            for key, value in update_fields.items():
                if value is not None and hasattr(record, key):
                    setattr(record, key, value)

            record.updated_at = datetime.now()
            session.add(record)
            session.flush()
            session.refresh(record)
            return ProjectService._to_model(record)

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """删除项目"""
        # 收集所有关联的录制
        with session_scope() as session:
            record = session.get(ProjectRecord, project_id)
            if not record:
                return False
            recording_ids = [rec.id for rec in record.recordings]

        # 删除录制（包含 MinIO 文件）
        from .recording_service import RecordingService

        for rec_id in recording_ids:
            RecordingService.delete_recording(rec_id)

        # 删除项目级别的文件
        for file_info in FileService.list_files(project_id=project_id):
            minio_client.delete_file(file_info.path)
            FileService.delete_file(file_info.path)

        # 删除项目记录
        with session_scope() as session:
            record = session.get(ProjectRecord, project_id)
            if record:
                session.delete(record)

        return True

    @staticmethod
    def add_recording_to_project(project_id: str, recording_id: str) -> Optional[Project]:
        """确保录制归属于指定项目"""
        with session_scope() as session:
            project = session.get(ProjectRecord, project_id)
            if not project:
                return None

            recording = session.get(RecordingRecord, recording_id)
            if not recording:
                return None

            if recording.project_id != project_id:
                recording.project_id = project_id
                session.add(recording)

            session.flush()
            session.refresh(project)
            return ProjectService._to_model(project)
