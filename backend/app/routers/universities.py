import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.snapshot import Snapshot, UniversityCurrent, UniversitySnapshot
from app.schemas.university import UniversityListResponse, UniversityResponse

router = APIRouter(prefix="/universities", tags=["universities"])

SORT_COLUMNS = {
    "university_name": UniversityCurrent.university_name,
    "researchers_count": UniversityCurrent.researchers_count.desc(),
    "students_count": UniversityCurrent.students_count.desc(),
    "created_at": UniversityCurrent.created_at.desc(),
}


def _parse_hardware_types(hardware_json: str | None) -> list[str]:
    """Parse hardware types from JSON string."""
    return json.loads(hardware_json) if hardware_json else []


def _university_to_response(uni: UniversityCurrent) -> UniversityResponse:
    """Convert UniversityCurrent model to response schema."""
    return UniversityResponse(
        asana_task_gid=uni.asana_task_gid,
        university_name=uni.university_name,
        researchers_count=uni.researchers_count,
        students_count=uni.students_count,
        hardware_types=_parse_hardware_types(uni.hardware_types),
        point_of_contact=uni.point_of_contact,
        created_at=uni.created_at,
        last_synced_at=uni.last_synced_at
    )


@router.get("/", response_model=UniversityListResponse)
def get_universities(
    search: str | None = Query(None),
    sort_by: str = Query("university_name"),
    has_tenstorrent: bool | None = Query(None),
    db: Session = Depends(get_db)
) -> UniversityListResponse:
    """Get list of all universities with current data."""
    query = db.query(UniversityCurrent)

    if search:
        query = query.filter(
            UniversityCurrent.university_name.ilike(f"%{search}%")
        )

    if has_tenstorrent:
        query = query.filter(
            UniversityCurrent.hardware_types.isnot(None),
            UniversityCurrent.hardware_types != '[]'
        )

    sort_column = SORT_COLUMNS.get(sort_by, UniversityCurrent.university_name)
    universities = query.order_by(sort_column).all()

    response_list = [_university_to_response(uni) for uni in universities]
    return UniversityListResponse(universities=response_list, total=len(response_list))


@router.get("/{task_gid}", response_model=UniversityResponse)
def get_university_detail(task_gid: str, db: Session = Depends(get_db)) -> UniversityResponse:
    """Get detailed info for a specific university."""
    uni = db.query(UniversityCurrent).filter(
        UniversityCurrent.asana_task_gid == task_gid
    ).first()

    if not uni:
        raise HTTPException(status_code=404, detail="University not found")

    return _university_to_response(uni)


@router.get("/{task_gid}/history")
def get_university_history(
    task_gid: str,
    limit: int = Query(30, le=365),
    db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    """Get historical snapshots for a specific university."""
    snapshots = db.query(UniversitySnapshot, Snapshot.snapshot_date).join(
        Snapshot
    ).filter(
        UniversitySnapshot.asana_task_gid == task_gid
    ).order_by(
        Snapshot.snapshot_date.desc()
    ).limit(limit).all()

    return [
        {
            "date": snapshot_date,
            "researchers_count": uni_snapshot.researchers_count,
            "students_count": uni_snapshot.students_count,
            "hardware_types": _parse_hardware_types(uni_snapshot.hardware_types)
        }
        for uni_snapshot, snapshot_date in snapshots
    ]
