from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Asana Configuration
    asana_access_token: str = ""
    asana_project_gid: str = ""
    asana_field_researchers_count: str = ""
    asana_field_students_count: str = ""
    asana_field_hardware_types: str = ""
    asana_field_point_of_contact: str = ""

    # Database
    database_url: str = "sqlite:///./academic_program.db"

    # Sync Settings
    sync_schedule_hours: int = 24
    enable_scheduled_sync: bool = True

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
