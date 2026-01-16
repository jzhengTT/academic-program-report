from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.metrics import CurrentMetrics, GrowthMetrics, MetricsTimeline
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/current", response_model=CurrentMetrics)
def get_current_metrics(db: Session = Depends(get_db)) -> CurrentMetrics:
    """Get current aggregate metrics from latest data."""
    return MetricsService(db).get_current_metrics()


@router.get("/timeline", response_model=MetricsTimeline)
def get_metrics_timeline(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db)
) -> MetricsTimeline:
    """Get historical metrics for charting."""
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=90)

    return MetricsService(db).get_timeline(start_date, end_date)


@router.get("/growth", response_model=GrowthMetrics)
def get_growth_metrics(
    period_days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
) -> GrowthMetrics:
    """Calculate growth percentages over specified period."""
    return MetricsService(db).calculate_growth(period_days)


@router.get("/hardware-distribution")
def get_hardware_distribution(db: Session = Depends(get_db)) -> dict[str, int]:
    """Get distribution of hardware types across universities."""
    return MetricsService(db).get_hardware_distribution()
