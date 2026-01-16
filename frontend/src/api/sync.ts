import type { AxiosResponse } from 'axios';

import { apiClient } from './index.ts';
import type { SyncStatus, SyncTriggerResponse } from '../types/sync.ts';

export const syncApi = {
  trigger(createSnapshot: boolean = true): Promise<AxiosResponse<SyncTriggerResponse>> {
    return apiClient.post<SyncTriggerResponse>('/sync/trigger', null, {
      params: { create_snapshot: createSnapshot }
    });
  },

  getStatus(): Promise<AxiosResponse<SyncStatus>> {
    return apiClient.get<SyncStatus>('/sync/status');
  },
};
