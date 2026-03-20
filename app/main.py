"""Application entry point.

Initialises the FastAPI application, creates database tables on startup,
and registers top-level routes.
"""

from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Create all tables on startup (no-op if they already exist).
# Import every model module before this line so that Base.metadata is fully
# populated.  Models added under app/models/ are auto-discovered here.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A geo-aware address book API",
)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Health-check endpoint.

    Returns:
        A JSON object confirming the service is running and its current version.
    """
    return {"message": "Address Book API is running", "version": settings.VERSION}
