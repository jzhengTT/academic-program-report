from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_date = Column(Date, nullable=False, unique=True)
    total_universities = Column(Integer, nullable=False, default=0)
    total_researchers = Column(Integer, nullable=False, default=0)
    total_students = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    universities = relationship(
        "UniversitySnapshot",
        back_populates="snapshot",
        cascade="all, delete-orphan"
    )


class UniversitySnapshot(Base):
    __tablename__ = "university_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(
        Integer,
        ForeignKey("snapshots.id", ondelete="CASCADE"),
        nullable=False
    )
    asana_task_gid = Column(String, nullable=False)
    university_name = Column(String, nullable=False)
    researchers_count = Column(Integer, default=0)
    students_count = Column(Integer, default=0)
    hardware_types = Column(Text)  # JSON string
    point_of_contact = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    snapshot = relationship("Snapshot", back_populates="universities")


class UniversityCurrent(Base):
    __tablename__ = "universities_current"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asana_task_gid = Column(String, unique=True, nullable=False)
    university_name = Column(String, nullable=False)
    researchers_count = Column(Integer, default=0)
    students_count = Column(Integer, default=0)
    hardware_types = Column(Text)  # JSON string
    point_of_contact = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_type = Column(String, nullable=False)  # 'manual' or 'scheduled'
    status = Column(String, nullable=False)  # 'success', 'failed', 'in_progress'
    tasks_synced = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
