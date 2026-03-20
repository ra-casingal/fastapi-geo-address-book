"""Application configuration.

All settings are read from environment variables.  A ``.env`` file in the
project root is loaded automatically (see ``.env.example`` for the full list
of supported variables).

Usage::

    from app.core.config import settings

    engine = create_engine(settings.database_url)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised application settings backed by environment variables.

    Each field maps 1-to-1 to an environment variable of the same name
    (case-insensitive).  Defaults are provided for local development only —
    override every value via ``.env`` or real environment variables in
    production.

    Attributes:
        project_name: Human-readable name shown in the OpenAPI docs.
        version: Current API version string (SemVer).
        database_url: SQLAlchemy-compatible connection string.
            Defaults to a local SQLite file for development.
            Example production value: ``postgresql+psycopg2://user:pass@host/db``
        log_level: Controls verbosity for the entire application.
            Accepted values: DEBUG, INFO, WARNING, ERROR, CRITICAL
            (case-insensitive).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    project_name: str = "Address Book API"
    version: str = "0.1.0"
    database_url: str = "sqlite:///./address_book.db"
    log_level: str = "INFO"


settings = Settings()
