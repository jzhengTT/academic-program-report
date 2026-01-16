from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UniversityData(BaseModel):
    asana_task_gid: str
    university_name: str
    researchers_count: int = 0
    students_count: int = 0
    hardware_types: list[str] = []
    point_of_contact: str | None = None
    created_at: datetime | None = None


class UniversityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asana_task_gid: str
    university_name: str
    researchers_count: int
    students_count: int
    hardware_types: list[str]
    point_of_contact: str | None
    created_at: datetime
    last_synced_at: datetime


class UniversityListResponse(BaseModel):
    universities: list[UniversityResponse]
    total: int
