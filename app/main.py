"""Application entry point.

Initialises the FastAPI application, creates database tables on startup,
and registers top-level routes.
"""

import logging

from fastapi import FastAPI

from app.api.routes.address import router as address_router
from app.core.config import settings
from app.core.logger import setup_logging
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401 — registers all ORM models with Base.metadata

# Logging must be configured before any module emits records.
setup_logging(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)

# Create all tables on startup (no-op if they already exist).
# app.models must be imported above before this call so every table
# is present in Base.metadata.
Base.metadata.create_all(bind=engine)
logger.info("Database tables verified / created.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A geo-aware address book API",
)

app.include_router(address_router, prefix="/api/v1")

logger.info(
    "Application '%s' v%s starting up (log level: %s).",
    settings.PROJECT_NAME,
    settings.VERSION,
    settings.LOG_LEVEL,
)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Health-check endpoint.

    Returns:
        A JSON object confirming the service is running and its current version.
    """
    return {"message": "Address Book API is running", "version": settings.VERSION}
