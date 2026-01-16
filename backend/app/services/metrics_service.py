import json
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.snapshot import Snapshot, UniversityCurrent
from app.schemas.metrics import CurrentMetrics, GrowthMetrics, MetricsTimeline, TimelineDataPoint


def _calc_growth(current_val: int, previous_val: int) -> float:
    """Calculate percentage growth between two values."""
    if previous_val == 0:
        return 100.0 if current_val > 0 else 0.0
    return round(((current_val - previous_val) / previous_val) * 100, 1)


def _parse_hardware_types(hardware_json: str | None) -> list[str]:
    """Parse hardware types from JSON string."""
    return json.loads(hardware_json) if hardware_json else []


class MetricsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_current_metrics(self) -> CurrentMetrics:
        """Get current aggregate metrics from universities_current table."""
        result = self.db.query(
            func.count(UniversityCurrent.id).label("total_universities"),
            func.coalesce(func.sum(UniversityCurrent.researchers_count), 0).label("total_researchers"),
            func.coalesce(func.sum(UniversityCurrent.students_count), 0).label("total_students"),
            func.max(UniversityCurrent.last_synced_at).label("last_updated")
        ).first()

        # Calculate TT-Hardware specific metrics
        universities = self.db.query(UniversityCurrent).all()
        universities_with_tt = 0
        researchers_on_tt = 0
        students_on_tt = 0

        for uni in universities:
            hardware_list = _parse_hardware_types(uni.hardware_types)
            if hardware_list:
                universities_with_tt += 1
                researchers_on_tt += uni.researchers_count or 0
                students_on_tt += uni.students_count or 0

        return CurrentMetrics(
            total_universities=result.total_universities or 0,
            total_researchers=int(result.total_researchers or 0),
            total_students=int(result.total_students or 0),
            universities_with_tt_hardware=universities_with_tt,
            researchers_on_tt_hardware=researchers_on_tt,
            students_on_tt_hardware=students_on_tt,
            last_updated=result.last_updated
        )

    def get_timeline(self, start_date: date, end_date: date) -> MetricsTimeline:
        """Get historical metrics for charting."""
        snapshots = self.db.query(Snapshot).filter(
            Snapshot.snapshot_date >= start_date,
            Snapshot.snapshot_date <= end_date
        ).order_by(Snapshot.snapshot_date).all()

        data = [
            TimelineDataPoint(
                date=s.snapshot_date,
                universities=s.total_universities,
                researchers=s.total_researchers,
                students=s.total_students
            )
            for s in snapshots
        ]

        return MetricsTimeline(data=data, start_date=start_date, end_date=end_date)

    def calculate_growth(self, period_days: int = 30) -> GrowthMetrics:
        """Calculate growth percentages over specified period."""
        current = self.get_current_metrics()
        past_date = date.today() - timedelta(days=period_days)

        past_snapshot = self.db.query(Snapshot).filter(
            Snapshot.snapshot_date <= past_date
        ).order_by(Snapshot.snapshot_date.desc()).first()

        if past_snapshot:
            prev_universities = past_snapshot.total_universities
            prev_researchers = past_snapshot.total_researchers
            prev_students = past_snapshot.total_students
        else:
            prev_universities = prev_researchers = prev_students = 0

        return GrowthMetrics(
            universities_growth=_calc_growth(current.total_universities, prev_universities),
            researchers_growth=_calc_growth(current.total_researchers, prev_researchers),
            students_growth=_calc_growth(current.total_students, prev_students),
            period_days=period_days,
            current_universities=current.total_universities,
            current_researchers=current.total_researchers,
            current_students=current.total_students,
            previous_universities=prev_universities,
            previous_researchers=prev_researchers,
            previous_students=prev_students
        )

    def get_hardware_distribution(self) -> dict[str, int]:
        """Get distribution of hardware types across universities."""
        universities = self.db.query(UniversityCurrent).all()

        hardware_counts: dict[str, int] = {}
        for uni in universities:
            for hw_type in _parse_hardware_types(uni.hardware_types):
                hardware_counts[hw_type] = hardware_counts.get(hw_type, 0) + 1

        return hardware_counts
