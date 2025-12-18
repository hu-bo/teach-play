"""
SQLAlchemy ORM 模型
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class ProjectRecord(Base):
    """项目表"""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    recordings: Mapped[list["RecordingRecord"]] = relationship(
        "RecordingRecord",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    files: Mapped[list["FileInfoRecord"]] = relationship(
        "FileInfoRecord",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class RecordingRecord(Base):
    """录制表"""

    __tablename__ = "recordings"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    minio_object: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    project: Mapped[ProjectRecord] = relationship(
        "ProjectRecord",
        back_populates="recordings",
        lazy="joined",
    )
    files: Mapped[list["FileInfoRecord"]] = relationship(
        "FileInfoRecord",
        back_populates="recording",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class FileInfoRecord(Base):
    """文件表，存储 MinIO 元数据"""

    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, index=True)
    object_path: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    bucket: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False, default="application/octet-stream")
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    project_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    recording_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    project: Mapped[ProjectRecord | None] = relationship(
        "ProjectRecord",
        back_populates="files",
        lazy="joined",
    )
    recording: Mapped[RecordingRecord | None] = relationship(
        "RecordingRecord",
        back_populates="files",
        lazy="joined",
    )


__all__ = ["ProjectRecord", "RecordingRecord", "FileInfoRecord"]
