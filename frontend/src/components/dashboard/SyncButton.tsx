import { format, parseISO } from 'date-fns';
import type { ReactElement } from 'react';

import { useSync } from '../../hooks/useSync.ts';
import './SyncButton.css';

interface SyncButtonProps {
  onSyncComplete?: () => void;
}

const SYNC_COMPLETE_DELAY = 3000;

function formatLastSync(lastSyncAt: string | null | undefined): string {
  if (!lastSyncAt) {
    return 'Never synced';
  }
  try {
    return `Last synced: ${format(parseISO(lastSyncAt), 'MMM d, yyyy h:mm a')}`;
  } catch {
    return 'Last synced: Unknown';
  }
}

export function SyncButton({ onSyncComplete }: SyncButtonProps): ReactElement {
  const { status, isSyncing, triggerSync } = useSync();

  function handleSync(): void {
    triggerSync(true);
    if (onSyncComplete) {
      setTimeout(onSyncComplete, SYNC_COMPLETE_DELAY);
    }
  }

  return (
    <div className="sync-container">
      <button
        className={`sync-button ${isSyncing ? 'syncing' : ''}`}
        onClick={handleSync}
        disabled={isSyncing}
      >
        {isSyncing ? (
          <>
            <span className="spinner" />
            Syncing...
          </>
        ) : (
          <>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 4v6h-6" />
              <path d="M1 20v-6h6" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            Sync from Asana
          </>
        )}
      </button>
      <span className="sync-status">
        {formatLastSync(status?.last_sync_at)}
        {status?.last_sync_status === 'failed' && (
          <span className="sync-error"> (Failed)</span>
        )}
      </span>
    </div>
  );
}
