from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.schemas.sync import SyncHistoryEntry, SyncHistoryResponse, SyncStatus, SyncTriggerResponse
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


def _run_sync_task(sync_id: int, create_snapshot: bool) -> None:
    """Background task to run sync."""
    db = SessionLocal()
    try:
        SyncService(db).execute_sync(sync_id, create_snapshot)
    finally:
        db.close()


@router.post("/trigger", response_model=SyncTriggerResponse)
def trigger_sync(
    background_tasks: BackgroundTasks,
    create_snapshot: bool = Query(True),
    db: Session = Depends(get_db)
) -> SyncTriggerResponse:
    """Manually trigger a sync from Asana."""
    service = SyncService(db)

    if service.is_sync_in_progress():
        raise HTTPException(status_code=409, detail="Sync already in progress")

    sync_id = service.start_sync("manual")
    background_tasks.add_task(_run_sync_task, sync_id, create_snapshot)

    return SyncTriggerResponse(
        sync_id=sync_id,
        message="Sync started",
        status="in_progress"
    )


@router.get("/status", response_model=SyncStatus)
def get_sync_status(db: Session = Depends(get_db)) -> SyncStatus:
    """Get current sync status and last sync info."""
    return SyncStatus(**SyncService(db).get_status())


@router.get("/history", response_model=SyncHistoryResponse)
def get_sync_history(
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
) -> SyncHistoryResponse:
    """Get history of sync operations."""
    logs = SyncService(db).get_history(limit)
    return SyncHistoryResponse(
        history=[SyncHistoryEntry.model_validate(log) for log in logs]
    )
