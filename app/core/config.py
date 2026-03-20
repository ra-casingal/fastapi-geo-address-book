"""Application configuration.

All settings are read from environment variables.  A ``.env`` file in the
project root is loaded automatically (see ``.env.example`` for the full list
of supported variables).
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised application settings backed by environment variables.

    Attributes:
        PROJECT_NAME: Human-readable name shown in the OpenAPI docs.
        VERSION: Current API version string (SemVer).
        DATABASE_URL: SQLAlchemy-compatible connection string.
            Defaults to a local SQLite file for development.
            Example production value: ``postgresql+psycopg2://user:pass@host/db``
    """

    PROJECT_NAME: str = "Address Book API"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = "sqlite:///./address_book.db"
    #: Controls verbosity for the entire application.  Accepted values:
    #: DEBUG, INFO, WARNING, ERROR, CRITICAL (case-insensitive).
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
