import { useQuery, type UseQueryResult } from '@tanstack/react-query';

import { universitiesApi } from '../api/universities.ts';
import type { UniversityListResponse } from '../types/university.ts';

const STALE_TIME = 5 * 60 * 1000; // 5 minutes

export function useUniversities(
  search?: string,
  sortBy: string = 'university_name',
  hasTenstorrent?: boolean
): UseQueryResult<UniversityListResponse, Error> {
  return useQuery({
    queryKey: ['universities', search, sortBy, hasTenstorrent],
    queryFn: () => universitiesApi.getAll(search, sortBy, hasTenstorrent).then(res => res.data),
    staleTime: STALE_TIME,
  });
}
