import { useQuery } from '@tanstack/react-query';
import { format, subDays } from 'date-fns';

import { metricsApi } from '../api/metrics.ts';
import type { CurrentMetrics, GrowthMetrics, MetricsTimeline } from '../types/metrics.ts';

const STALE_TIME = 5 * 60 * 1000; // 5 minutes

interface UseMetricsReturn {
  currentMetrics: CurrentMetrics | undefined;
  timeline: MetricsTimeline | undefined;
  growth: GrowthMetrics | undefined;
  hardwareDistribution: Record<string, number> | undefined;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useMetrics(timelineDays: number = 90): UseMetricsReturn {
  const currentQuery = useQuery({
    queryKey: ['metrics', 'current'],
    queryFn: () => metricsApi.getCurrent().then(res => res.data),
    staleTime: STALE_TIME,
  });

  const timelineQuery = useQuery({
    queryKey: ['metrics', 'timeline', timelineDays],
    queryFn: () => {
      const endDate = format(new Date(), 'yyyy-MM-dd');
      const startDate = format(subDays(new Date(), timelineDays), 'yyyy-MM-dd');
      return metricsApi.getTimeline(startDate, endDate).then(res => res.data);
    },
    staleTime: STALE_TIME,
  });

  const growthQuery = useQuery({
    queryKey: ['metrics', 'growth'],
    queryFn: () => metricsApi.getGrowth(30).then(res => res.data),
    staleTime: STALE_TIME,
  });

  const hardwareQuery = useQuery({
    queryKey: ['metrics', 'hardware'],
    queryFn: () => metricsApi.getHardwareDistribution().then(res => res.data),
    staleTime: STALE_TIME,
  });

  function refetch(): void {
    currentQuery.refetch();
    timelineQuery.refetch();
    growthQuery.refetch();
    hardwareQuery.refetch();
  }

  return {
    currentMetrics: currentQuery.data,
    timeline: timelineQuery.data,
    growth: growthQuery.data,
    hardwareDistribution: hardwareQuery.data,
    isLoading: currentQuery.isLoading || timelineQuery.isLoading || growthQuery.isLoading,
    error: currentQuery.error || timelineQuery.error || growthQuery.error,
    refetch,
  };
}
