"""
录制管理服务
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import select

from ..core.database import session_scope
from ..core.minio_client import minio_client
from ..db.models import RecordingRecord
from ..models.recording import (
    Recording,
    RecordingCreate,
    RecordingUpdate,
    Step,
    StepCreate,
    StepUpdate,
)
from .file_service import FileService
from .project_service import ProjectService


class RecordingService:
    """录制管理服务"""

    @staticmethod
    def _get_recording_path(recording_id: str) -> str:
        """获取录制存储路径"""
        return f"recordings/{recording_id}/recording.json"

    @staticmethod
    def _get_record_row(recording_id: str) -> Optional[RecordingRecord]:
        with session_scope() as session:
            return session.get(RecordingRecord, recording_id)

    @staticmethod
    def _load_recording_from_storage(record: RecordingRecord) -> Optional[Recording]:
        if not record.minio_object:
            return None

        data = minio_client.download_file(record.minio_object)
        if not data:
            return None

        try:
            payload = json.loads(data.decode())
            return Recording(**payload)
        except Exception as exc:
            print(f"Error parsing recording {record.id}: {exc}")
            return None

    @staticmethod
    def _load_recording_from_path(object_path: str, recording_id: str) -> Optional[Recording]:
        data = minio_client.download_file(object_path)
        if not data:
            return None

        try:
            payload = json.loads(data.decode())
            recording = Recording(**payload)
        except Exception as exc:
            print(f"Error decoding recording {recording_id}: {exc}")
            return None

        RecordingService._persist_metadata(recording, object_path)
        FileService.register_file(
            object_path,
            content_type="application/json",
            size=len(data),
            project_id=recording.project_id,
            recording_id=recording.id,
        )
        return recording

    @staticmethod
    def _persist_metadata(recording: Recording, object_path: str) -> None:
        with session_scope() as session:
            record = session.get(RecordingRecord, recording.id)
            if record:
                record.name = recording.name
                record.project_id = recording.project_id
                record.minio_object = object_path
                record.updated_at = datetime.now()
            else:
                record = RecordingRecord(
                    id=recording.id,
                    name=recording.name,
                    project_id=recording.project_id,
                    minio_object=object_path,
                    created_at=recording.created_at,
                    updated_at=datetime.now(),
                )
                session.add(record)
            session.flush()

    @staticmethod
    def _upload_recording(recording: Recording) -> Recording:
        payload = json.dumps(recording.model_dump(), default=str).encode()
        path = RecordingService._get_recording_path(recording.id)

        minio_client.upload_file(payload, path, "application/json")
        FileService.register_file(
            path,
            content_type="application/json",
            size=len(payload),
            project_id=recording.project_id,
            recording_id=recording.id,
        )
        RecordingService._persist_metadata(recording, path)
        return recording

    @staticmethod
    def _bootstrap_from_minio(project_id: Optional[str] = None) -> list[Recording]:
        recordings: list[Recording] = []
        objects = minio_client.list_objects("recordings/")
        recording_files = [o for o in objects if o.endswith("/recording.json")]

        for object_name in recording_files:
            data = minio_client.download_file(object_name)
            if not data:
                continue

            try:
                payload = json.loads(data.decode())
                recording = Recording(**payload)
            except Exception as exc:
                print(f"Error decoding recording file {object_name}: {exc}")
                continue

            if project_id and recording.project_id != project_id:
                continue

            RecordingService._persist_metadata(recording, object_name)
            FileService.register_file(
                object_name,
                content_type="application/json",
                size=len(data),
                project_id=recording.project_id,
                recording_id=recording.id,
            )
            recordings.append(recording)

        return recordings

    @staticmethod
    def list_recordings(project_id: Optional[str] = None) -> list[Recording]:
        """获取录制列表"""
        with session_scope() as session:
            stmt = select(RecordingRecord).order_by(RecordingRecord.created_at.asc())
            if project_id:
                stmt = stmt.where(RecordingRecord.project_id == project_id)
            records = session.scalars(stmt).all()

        result: list[Recording] = []
        for record in records:
            recording = RecordingService._load_recording_from_storage(record)
            if recording:
                result.append(recording)

        if not result:
            return RecordingService._bootstrap_from_minio(project_id)

        return result

    @staticmethod
    def get_recording(recording_id: str) -> Optional[Recording]:
        """获取录制详情"""
        record = RecordingService._get_record_row(recording_id)
        if record:
            recording = RecordingService._load_recording_from_storage(record)
            if recording:
                return recording

        path = RecordingService._get_recording_path(recording_id)
        return RecordingService._load_recording_from_path(path, recording_id)

    @staticmethod
    def create_recording(recording_data: RecordingCreate) -> Recording:
        """创建录制"""
        recording = Recording(
            name=recording_data.name,
            project_id=recording_data.project_id,
        )

        recording = RecordingService._upload_recording(recording)
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
            if value is not None and hasattr(recording, key):
                setattr(recording, key, value)

        return RecordingService._upload_recording(recording)

    @staticmethod
    def delete_recording(recording_id: str) -> bool:
        """删除录制"""
        recording = RecordingService.get_recording(recording_id)
        if not recording:
            return False

        record_row = RecordingService._get_record_row(recording_id)
        object_path = (
            record_row.minio_object if record_row else RecordingService._get_recording_path(recording_id)
        )

        minio_client.delete_file(object_path)
        FileService.delete_file(object_path)

        screenshots = minio_client.list_objects(f"screenshots/{recording_id}/")
        for ss in screenshots:
            minio_client.delete_file(ss)
            FileService.delete_file(ss)

        with session_scope() as session:
            row = session.get(RecordingRecord, recording_id)
            if row:
                session.delete(row)

        return True

    @staticmethod
    def save_recording(recording: Recording) -> None:
        """保存录制"""
        RecordingService._upload_recording(recording)

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
