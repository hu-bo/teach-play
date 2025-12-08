"""
录制管理服务
"""

import json
from typing import Optional

from ..models.recording import (
    Recording,
    RecordingCreate,
    RecordingUpdate,
    Step,
    StepCreate,
    StepUpdate,
)
from ..core.minio_client import minio_client
from .project_service import ProjectService


class RecordingService:
    """录制管理服务"""

    @staticmethod
    def _get_recording_path(recording_id: str) -> str:
        """获取录制存储路径"""
        return f"recordings/{recording_id}/recording.json"

    @staticmethod
    def list_recordings(project_id: Optional[str] = None) -> list[Recording]:
        """获取录制列表"""
        recordings = []

        objects = minio_client.list_objects("recordings/")
        recording_files = [o for o in objects if o.endswith("/recording.json")]

        for obj_path in recording_files:
            data = minio_client.download_file(obj_path)
            if data:
                recording_dict = json.loads(data.decode())

                # 如果指定了项目ID，过滤
                if project_id and recording_dict.get("project_id") != project_id:
                    continue

                recordings.append(Recording(**recording_dict))

        return recordings

    @staticmethod
    def get_recording(recording_id: str) -> Optional[Recording]:
        """获取录制详情"""
        path = RecordingService._get_recording_path(recording_id)
        data = minio_client.download_file(path)

        if data:
            recording_dict = json.loads(data.decode())
            return Recording(**recording_dict)

        return None

    @staticmethod
    def create_recording(recording_data: RecordingCreate) -> Recording:
        """创建录制"""
        recording = Recording(
            name=recording_data.name,
            project_id=recording_data.project_id
        )

        # 保存到MinIO
        path = RecordingService._get_recording_path(recording.id)
        minio_client.upload_file(
            json.dumps(recording.model_dump(), default=str).encode(),
            path,
            "application/json"
        )

        # 添加到项目
        ProjectService.add_recording_to_project(recording.project_id, recording.id)

        return recording

    @staticmethod
    def update_recording(recording_id: str, recording_data: RecordingUpdate) -> Optional[Recording]:
        """更新录制"""
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            return None

        update_data = recording_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(recording, key, value)

        path = RecordingService._get_recording_path(recording_id)
        minio_client.upload_file(
            json.dumps(recording.model_dump(), default=str).encode(),
            path,
            "application/json"
        )

        return recording

    @staticmethod
    def delete_recording(recording_id: str) -> bool:
        """删除录制"""
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            return False

        # 删除录制文件
        path = RecordingService._get_recording_path(recording_id)
        minio_client.delete_file(path)

        # 删除截图
        screenshots = minio_client.list_objects(f"screenshots/{recording_id}/")
        for ss in screenshots:
            minio_client.delete_file(ss)

        return True

    @staticmethod
    def save_recording(recording: Recording) -> None:
        """保存录制"""
        path = RecordingService._get_recording_path(recording.id)
        minio_client.upload_file(
            json.dumps(recording.model_dump(), default=str).encode(),
            path,
            "application/json"
        )

    # 步骤管理

    @staticmethod
    def get_steps(recording_id: str) -> list[Step]:
        """获取步骤列表"""
        recording = RecordingService.get_recording(recording_id)
        if recording:
            return recording.steps
        return []

    @staticmethod
    def get_step(recording_id: str, step_id: str) -> Optional[Step]:
        """获取单个步骤"""
        recording = RecordingService.get_recording(recording_id)
        if recording:
            for step in recording.steps:
                if step.id == step_id:
                    return step
        return None

    @staticmethod
    def add_step(recording_id: str, step_data: StepCreate) -> Optional[Step]:
        """添加步骤"""
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            return None

        step = Step(
            **step_data.model_dump(),
            index=len(recording.steps)
        )

        recording.steps.append(step)
        RecordingService.save_recording(recording)

        return step

    @staticmethod
    def update_step(
        recording_id: str,
        step_id: str,
        step_data: StepUpdate
    ) -> Optional[Step]:
        """更新步骤"""
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            return None

        for i, step in enumerate(recording.steps):
            if step.id == step_id:
                update_data = step_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    if value is not None:
                        setattr(step, key, value)

                recording.steps[i] = step
                RecordingService.save_recording(recording)
                return step

        return None

    @staticmethod
    def delete_step(recording_id: str, step_id: str) -> bool:
        """删除步骤"""
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            return False

        for i, step in enumerate(recording.steps):
            if step.id == step_id:
                recording.steps.pop(i)

                # 重新排序
                for j, s in enumerate(recording.steps):
                    s.index = j

                RecordingService.save_recording(recording)
                return True

        return False

    @staticmethod
    def reorder_steps(recording_id: str, step_ids: list[str]) -> Optional[list[Step]]:
        """重新排序步骤"""
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            return None

        # 构建步骤映射
        step_map = {step.id: step for step in recording.steps}

        # 重新排序
        new_steps = []
        for i, step_id in enumerate(step_ids):
            if step_id in step_map:
                step = step_map[step_id]
                step.index = i
                new_steps.append(step)

        recording.steps = new_steps
        RecordingService.save_recording(recording)

        return recording.steps
