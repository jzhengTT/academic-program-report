import json
import logging
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.snapshot import Snapshot, SyncLog, UniversityCurrent, UniversitySnapshot
from app.schemas.university import UniversityData
from app.services.asana_client import AsanaClient

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.asana_client = AsanaClient()

    def is_sync_in_progress(self) -> bool:
        return self.db.query(SyncLog).filter(
            SyncLog.status == "in_progress"
        ).first() is not None

    def start_sync(self, sync_type: str) -> int:
        log = SyncLog(sync_type=sync_type, status="in_progress")
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log.id

    def execute_sync(self, sync_id: int, create_snapshot: bool = True) -> None:
        log = self.db.query(SyncLog).filter(SyncLog.id == sync_id).first()

        try:
            universities = self.asana_client.get_project_tasks()
            logger.info(f"Fetched {len(universities)} universities from Asana")

            self._update_current_state(universities)

            if create_snapshot:
                self._create_snapshot(universities)

            log.status = "success"
            log.tasks_synced = len(universities)
            log.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()

        self.db.commit()

    def _update_current_state(self, universities: list[UniversityData]) -> None:
        """Update universities_current table with latest data."""
        # Get all active university task GIDs from the current sync
        active_gids = {uni.asana_task_gid for uni in universities}

        # Update or insert active universities
        for uni in universities:
            existing = self.db.query(UniversityCurrent).filter(
                UniversityCurrent.asana_task_gid == uni.asana_task_gid
            ).first()

            hardware_json = json.dumps(uni.hardware_types)

            if existing:
                existing.university_name = uni.university_name
                existing.researchers_count = uni.researchers_count
                existing.students_count = uni.students_count
                existing.hardware_types = hardware_json
                existing.point_of_contact = uni.point_of_contact
                existing.last_synced_at = datetime.utcnow()
            else:
                self.db.add(UniversityCurrent(
                    asana_task_gid=uni.asana_task_gid,
                    university_name=uni.university_name,
                    researchers_count=uni.researchers_count,
                    students_count=uni.students_count,
                    hardware_types=hardware_json,
                    point_of_contact=uni.point_of_contact,
                    created_at=uni.created_at or datetime.utcnow()
                ))

        # Remove universities that are no longer active (moved to De-scoped or completed)
        # Only delete if we have active universities (safety check to prevent accidental deletion)
        if active_gids:
            deleted_count = self.db.query(UniversityCurrent).filter(
                UniversityCurrent.asana_task_gid.notin_(active_gids)
            ).delete(synchronize_session=False)

            if deleted_count > 0:
                logger.info(f"Removed {deleted_count} de-scoped or completed universities from database")

        self.db.commit()

    def _create_snapshot(self, universities: list[UniversityData]) -> None:
        """Create a point-in-time snapshot."""
        today = date.today()
        total_researchers = sum(u.researchers_count for u in universities)
        total_students = sum(u.students_count for u in universities)

        existing = self.db.query(Snapshot).filter(
            Snapshot.snapshot_date == today
        ).first()

        if existing:
            self.db.query(UniversitySnapshot).filter(
                UniversitySnapshot.snapshot_id == existing.id
            ).delete()
            snapshot = existing
        else:
            snapshot = Snapshot(snapshot_date=today)
            self.db.add(snapshot)
            self.db.flush()

        snapshot.total_universities = len(universities)
        snapshot.total_researchers = total_researchers
        snapshot.total_students = total_students

        for uni in universities:
            self.db.add(UniversitySnapshot(
                snapshot_id=snapshot.id,
                asana_task_gid=uni.asana_task_gid,
                university_name=uni.university_name,
                researchers_count=uni.researchers_count,
                students_count=uni.students_count,
                hardware_types=json.dumps(uni.hardware_types),
                point_of_contact=uni.point_of_contact,
                created_at=uni.created_at
            ))

        self.db.commit()
        logger.info(f"Created snapshot for {today} with {len(universities)} universities")

    def get_status(self) -> dict[str, Any]:
        """Get current sync status."""
        in_progress = self.db.query(SyncLog).filter(
            SyncLog.status == "in_progress"
        ).first()

        last_completed = self.db.query(SyncLog).filter(
            SyncLog.status.in_(["success", "failed"])
        ).order_by(SyncLog.completed_at.desc()).first()

        return {
            "is_syncing": in_progress is not None,
            "last_sync_at": last_completed.completed_at if last_completed else None,
            "last_sync_status": last_completed.status if last_completed else None,
            "last_sync_tasks": last_completed.tasks_synced if last_completed else None
        }

    def get_history(self, limit: int = 10) -> list[SyncLog]:
        """Get sync history."""
        return self.db.query(SyncLog).order_by(
            SyncLog.started_at.desc()
        ).limit(limit).all()
