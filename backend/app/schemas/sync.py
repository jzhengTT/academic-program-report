from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SyncTriggerResponse(BaseModel):
    sync_id: int
    message: str
    status: str


class SyncStatus(BaseModel):
    is_syncing: bool
    last_sync_at: datetime | None = None
    last_sync_status: str | None = None
    last_sync_tasks: int | None = None


class SyncHistoryEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sync_type: str
    status: str
    tasks_synced: int
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


class SyncHistoryResponse(BaseModel):
    history: list[SyncHistoryEntry]
