export interface SyncStatus {
  is_syncing: boolean;
  last_sync_at: string | null;
  last_sync_status: string | null;
  last_sync_tasks: number | null;
}

export interface SyncTriggerResponse {
  sync_id: number;
  message: string;
  status: string;
}
