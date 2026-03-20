from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A geo-aware address book API",
)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Address Book API is running", "version": settings.VERSION}
