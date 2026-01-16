from datetime import date, datetime

from pydantic import BaseModel


class CurrentMetrics(BaseModel):
    total_universities: int
    total_researchers: int
    total_students: int
    universities_with_tt_hardware: int
    researchers_on_tt_hardware: int
    students_on_tt_hardware: int
    last_updated: datetime | None = None


class TimelineDataPoint(BaseModel):
    date: date
    universities: int
    researchers: int
    students: int


class MetricsTimeline(BaseModel):
    data: list[TimelineDataPoint]
    start_date: date
    end_date: date


class GrowthMetrics(BaseModel):
    universities_growth: float
    researchers_growth: float
    students_growth: float
    period_days: int
    current_universities: int
    current_researchers: int
    current_students: int
    previous_universities: int
    previous_researchers: int
    previous_students: int
