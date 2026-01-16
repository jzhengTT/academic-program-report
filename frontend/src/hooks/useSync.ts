import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { syncApi } from '../api/sync.ts';
import type { SyncStatus } from '../types/sync.ts';

interface UseSyncReturn {
  status: SyncStatus | undefined;
  isLoading: boolean;
  isSyncing: boolean;
  triggerSync: (createSnapshot?: boolean) => void;
  error: Error | null;
}

export function useSync(): UseSyncReturn {
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ['sync', 'status'],
    queryFn: () => syncApi.getStatus().then(res => res.data),
    refetchInterval: (query) => {
      return query.state.data?.is_syncing ? 2000 : 3600000;
    },
  });

  const triggerMutation = useMutation({
    mutationFn: (createSnapshot: boolean = true) => syncApi.trigger(createSnapshot),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sync', 'status'] });
    },
    onSettled: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['metrics'] });
        queryClient.invalidateQueries({ queryKey: ['universities'] });
      }, 1000);
    },
  });

  return {
    status: statusQuery.data,
    isLoading: statusQuery.isLoading,
    isSyncing: statusQuery.data?.is_syncing || triggerMutation.isPending,
    triggerSync: triggerMutation.mutate,
    error: statusQuery.error || triggerMutation.error,
  };
}
