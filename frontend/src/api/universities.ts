import type { AxiosResponse } from 'axios';

import { apiClient } from './index.ts';
import type { University, UniversityListResponse } from '../types/university.ts';

export interface UniversityHistoryEntry {
  date: string;
  researchers_count: number;
  students_count: number;
  hardware_types: string[];
}

export const universitiesApi = {
  getAll(search?: string, sortBy: string = 'university_name', hasTenstorrent?: boolean): Promise<AxiosResponse<UniversityListResponse>> {
    return apiClient.get<UniversityListResponse>('/universities/', {
      params: { search, sort_by: sortBy, has_tenstorrent: hasTenstorrent }
    });
  },

  getById(taskGid: string): Promise<AxiosResponse<University>> {
    return apiClient.get<University>(`/universities/${taskGid}`);
  },

  getHistory(taskGid: string, limit: number = 30): Promise<AxiosResponse<UniversityHistoryEntry[]>> {
    return apiClient.get<UniversityHistoryEntry[]>(`/universities/${taskGid}/history`, {
      params: { limit }
    });
  },
};
