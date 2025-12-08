"""
项目服务
"""

import json
from typing import Optional
from datetime import datetime

from ..models.project import Project, ProjectCreate, ProjectUpdate
from ..core.minio_client import minio_client


class ProjectService:
    """项目服务"""

    @staticmethod
    def _get_project_path(project_id: str) -> str:
        """获取项目存储路径"""
        return f"projects/{project_id}/project.json"

    @staticmethod
    def list_projects() -> list[Project]:
        """获取项目列表"""
        projects = []

        try:
            # 列出所有项目目录
            objects = minio_client.list_objects("projects/")
            project_files = [o for o in objects if o.endswith("/project.json")]

            for obj_path in project_files:
                data = minio_client.download_file(obj_path)
                if data:
                    project_dict = json.loads(data.decode())
                    projects.append(Project(**project_dict))
        except Exception as e:
            print(f"Warning: Failed to list projects from MinIO: {e}")
            # MinIO 不可用时返回空列表

        return projects

    @staticmethod
    def get_project(project_id: str) -> Optional[Project]:
        """获取项目详情"""
        path = ProjectService._get_project_path(project_id)
        data = minio_client.download_file(path)

        if data:
            project_dict = json.loads(data.decode())
            return Project(**project_dict)

        return None

    @staticmethod
    def create_project(project_data: ProjectCreate) -> Project:
        """创建项目"""
        project = Project(
            name=project_data.name,
            description=project_data.description
        )

        # 保存到MinIO
        path = ProjectService._get_project_path(project.id)
        minio_client.upload_file(
            json.dumps(project.model_dump(), default=str).encode(),
            path,
            "application/json"
        )

        return project

    @staticmethod
    def update_project(project_id: str, project_data: ProjectUpdate) -> Optional[Project]:
        """更新项目"""
        project = ProjectService.get_project(project_id)
        if not project:
            return None

        # 更新字段
        update_data = project_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(project, key, value)

        project.updated_at = datetime.now()

        # 保存
        path = ProjectService._get_project_path(project_id)
        minio_client.upload_file(
            json.dumps(project.model_dump(), default=str).encode(),
            path,
            "application/json"
        )

        return project

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """删除项目"""
        # 删除项目文件
        path = ProjectService._get_project_path(project_id)
        minio_client.delete_file(path)

        # 删除项目目录下的所有文件
        objects = minio_client.list_objects(f"projects/{project_id}/")
        for obj in objects:
            minio_client.delete_file(obj)

        # 删除相关录制
        recordings = minio_client.list_objects(f"recordings/")
        for obj in recordings:
            if obj.endswith("/recording.json"):
                data = minio_client.download_file(obj)
                if data:
                    recording = json.loads(data.decode())
                    if recording.get("project_id") == project_id:
                        # 删除录制及其截图
                        rec_id = recording.get("id")
                        minio_client.delete_file(obj)
                        screenshots = minio_client.list_objects(f"screenshots/{rec_id}/")
                        for ss in screenshots:
                            minio_client.delete_file(ss)

        return True

    @staticmethod
    def add_recording_to_project(project_id: str, recording_id: str) -> Optional[Project]:
        """将录制添加到项目"""
        project = ProjectService.get_project(project_id)
        if not project:
            return None

        if recording_id not in project.recordings:
            project.recordings.append(recording_id)
            project.updated_at = datetime.now()

            path = ProjectService._get_project_path(project_id)
            minio_client.upload_file(
                json.dumps(project.model_dump(), default=str).encode(),
                path,
                "application/json"
            )

        return project
