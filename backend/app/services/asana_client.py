import logging
from datetime import datetime
from typing import Any

import asana
from asana.rest import ApiException

from app.config import get_settings
from app.schemas.university import UniversityData

logger = logging.getLogger(__name__)

OPT_FIELDS = [
    "name",
    "gid",
    "completed",
    "created_at",
    "memberships",
    "memberships.section",
    "memberships.section.name",
    "custom_fields",
    "custom_fields.gid",
    "custom_fields.name",
    "custom_fields.text_value",
    "custom_fields.number_value",
    "custom_fields.enum_value",
    "custom_fields.multi_enum_values",
    "custom_fields.display_value"
]


class AsanaClient:
    def __init__(self) -> None:
        settings = get_settings()
        configuration = asana.Configuration()
        configuration.access_token = settings.asana_access_token
        self.api_client = asana.ApiClient(configuration)
        self.tasks_api = asana.TasksApi(self.api_client)
        self.settings = settings

    def get_project_tasks(self) -> list[UniversityData]:
        """Fetch all tasks from the configured Asana project with custom fields."""
        opts = {"opt_fields": ",".join(OPT_FIELDS), "limit": 100}

        try:
            tasks = list(self.tasks_api.get_tasks_for_project(
                self.settings.asana_project_gid,
                opts
            ))
            logger.info(f"Fetched {len(tasks)} tasks from Asana")

            universities = [
                self._parse_task_to_university(task)
                for task in tasks
                if not task.get("completed") and not self._is_descoped(task)
            ]
            logger.info(f"Filtered to {len(universities)} active universities (excluding De-scoped)")
            return universities

        except ApiException as e:
            logger.error(f"Asana API error: {e}")
            raise

    def _is_descoped(self, task: dict[str, Any]) -> bool:
        """Check if a task is in the De-scoped section."""
        memberships = task.get("memberships", [])
        for membership in memberships:
            section = membership.get("section")
            if section and section.get("name", "").lower() == "de-scoped":
                return True
        return False

    def _parse_task_to_university(self, task: dict[str, Any]) -> UniversityData:
        """Parse Asana task data into UniversityData schema."""
        custom_fields = {cf["gid"]: cf for cf in task.get("custom_fields", [])}

        researchers_count = self._get_field_value(
            custom_fields,
            self.settings.asana_field_researchers_count,
            "number"
        ) or 0

        students_count = self._get_field_value(
            custom_fields,
            self.settings.asana_field_students_count,
            "number"
        ) or 0

        hardware_types = self._get_field_value(
            custom_fields,
            self.settings.asana_field_hardware_types,
            "multi_enum"
        ) or []

        point_of_contact = self._get_field_value(
            custom_fields,
            self.settings.asana_field_point_of_contact,
            "text"
        )

        # Parse created_at from Asana (ISO 8601 format)
        created_at = None
        if task.get("created_at"):
            try:
                created_at = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                created_at = None

        return UniversityData(
            asana_task_gid=task["gid"],
            university_name=task.get("name", "Unknown"),
            researchers_count=int(researchers_count),
            students_count=int(students_count),
            hardware_types=hardware_types,
            point_of_contact=point_of_contact,
            created_at=created_at
        )

    def _get_field_value(
        self,
        custom_fields: dict[str, Any],
        field_gid: str,
        field_type: str
    ) -> Any:
        """Extract value from custom field based on type."""
        if not field_gid:
            return None

        field = custom_fields.get(field_gid)
        if not field:
            return None

        match field_type:
            case "text":
                return field.get("text_value")
            case "number":
                return field.get("number_value")
            case "enum":
                enum_val = field.get("enum_value")
                return enum_val.get("name") if enum_val else None
            case "multi_enum":
                values = field.get("multi_enum_values", [])
                return [v.get("name") for v in values if v]
            case _:
                return field.get("display_value")
