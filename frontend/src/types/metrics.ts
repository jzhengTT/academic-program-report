export interface CurrentMetrics {
  total_universities: number;
  total_researchers: number;
  total_students: number;
  universities_with_tt_hardware: number;
  researchers_on_tt_hardware: number;
  students_on_tt_hardware: number;
  last_updated: string | null;
}

export interface TimelineDataPoint {
  date: string;
  universities: number;
  researchers: number;
  students: number;
}

export interface MetricsTimeline {
  data: TimelineDataPoint[];
  start_date: string;
  end_date: string;
}

export interface GrowthMetrics {
  universities_growth: number;
  researchers_growth: number;
  students_growth: number;
  period_days: number;
  current_universities: number;
  current_researchers: number;
  current_students: number;
  previous_universities: number;
  previous_researchers: number;
  previous_students: number;
}
