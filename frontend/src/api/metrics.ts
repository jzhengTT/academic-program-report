import type { AxiosResponse } from 'axios';

import { apiClient } from './index.ts';
import type { CurrentMetrics, GrowthMetrics, MetricsTimeline } from '../types/metrics.ts';

export const metricsApi = {
  getCurrent(): Promise<AxiosResponse<CurrentMetrics>> {
    return apiClient.get<CurrentMetrics>('/metrics/current');
  },

  getTimeline(startDate?: string, endDate?: string): Promise<AxiosResponse<MetricsTimeline>> {
    return apiClient.get<MetricsTimeline>('/metrics/timeline', {
      params: { start_date: startDate, end_date: endDate }
    });
  },

  getGrowth(periodDays: number = 30): Promise<AxiosResponse<GrowthMetrics>> {
    return apiClient.get<GrowthMetrics>('/metrics/growth', {
      params: { period_days: periodDays }
    });
  },

  getHardwareDistribution(): Promise<AxiosResponse<Record<string, number>>> {
    return apiClient.get<Record<string, number>>('/metrics/hardware-distribution');
  },
};
