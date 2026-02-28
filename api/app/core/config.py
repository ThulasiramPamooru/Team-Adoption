from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# Load .env from project root (Team-Adoption/.env)
_ROOT_ENV = Path(__file__).parent.parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "FlowGuard API"
    app_version: str = "1.0.0"
    debug: bool = False
    dev_mode: bool = False          # Set DEV_MODE=true to bypass Auth0 on localhost
    secret_key: str = "change-me-in-production"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://thulasiram@localhost:5432/flowguard"
    database_url_sync: str = "postgresql://thulasiram@localhost:5432/flowguard"

    # Auth0
    auth0_domain: str = ""
    auth0_audience: str = "https://flowguard-api"
    auth0_algorithms: list[str] = ["RS256"]

    # GitHub
    github_token: str = ""
    github_org: str = "ThulasiramPamooru"
    github_repo: str = "Team-Adoption"

    # Jira
    jira_url: str = "https://dolcera.atlassian.net"
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = "DIPA"

    # File paths (overridden by .env JIRA_ISSUES_PATH / TEST_REPORTS_PATH)
    jira_issues_path: str = str(Path(__file__).parent.parent.parent.parent / "JIRA issues")
    test_reports_path: str = str(Path(__file__).parent.parent.parent.parent / "test-reports")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
