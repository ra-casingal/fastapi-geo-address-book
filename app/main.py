"""Application entry point.

Initialises the FastAPI application, creates database tables on startup,
and registers top-level routes.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.address import router as address_router
from app.core.config import settings
from app.core.logger import setup_logging
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401 — registers all ORM models with Base.metadata

# Logging must be configured before any module emits records.
setup_logging(settings.log_level)

logger = logging.getLogger(__name__)

# Create all tables on startup (no-op if they already exist).
# app.models must be imported above before this call so every table
# is present in Base.metadata.
Base.metadata.create_all(bind=engine)
logger.info("Database tables verified / created.")

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="A geo-aware address book API",
)

app.include_router(address_router, prefix="/api/v1")

logger.info(
    "Application '%s' v%s starting up (log level: %s).",
    settings.project_name,
    settings.version,
    settings.log_level,
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Return a safe 500 for any unhandled SQLAlchemy database error."""
    logger.error("Unhandled database error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler: return a safe 500 for any otherwise-unhandled exception."""
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Health-check endpoint.

    Returns:
        A JSON object confirming the service is running and its current version.
    """
    return {"message": "Address Book API is running", "version": settings.VERSION}
