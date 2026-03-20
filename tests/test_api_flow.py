"""End-to-end API flow test — full CRUD lifecycle for the Address resource.

This module is intentionally self-contained. It creates its own file-based
SQLite test database, overrides the FastAPI ``get_db`` dependency, and removes
the database file when the module finishes.

Run this file in isolation with:

    pytest tests/test_api_flow.py -v
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.deps import get_db
from app.main import app

# ---------------------------------------------------------------------------
# Test database — file-based so it can be inspected if a test fails
# ---------------------------------------------------------------------------

_TEST_DB_FILE = "test_api_flow.db"
_TEST_DB_URL = f"sqlite:///./{_TEST_DB_FILE}"

_engine = create_engine(_TEST_DB_URL, connect_args={"check_same_thread": False})
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


# ---------------------------------------------------------------------------
# Module-scoped client fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client() -> TestClient:
    """TestClient backed by an isolated file-based SQLite database.

    Creates all tables before the module runs, then tears them down and
    deletes the database file once the last test in the module finishes.
    """
    Base.metadata.create_all(bind=_engine)

    def override_get_db():
        db = _SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Teardown — runs after all tests in this module
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=_engine)
    _engine.dispose()
    if os.path.exists(_TEST_DB_FILE):
        os.remove(_TEST_DB_FILE)


# ---------------------------------------------------------------------------
# End-to-end flow
# ---------------------------------------------------------------------------

def test_full_api_flow(client: TestClient):
    """Walk through the complete CRUD lifecycle for a single address.

    Steps
    -----
    1.  POST   — create an address
    2.  GET    — retrieve by id
    3.  GET    — list all and confirm presence
    4.  PUT    — partial update
    5.  GET    — nearby search
    6.  DELETE — remove
    7.  GET    — confirm 404 after deletion
    """

    # ------------------------------------------------------------------
    # 1. Create
    # ------------------------------------------------------------------
    r = client.post(
        "/api/v1/addresses/",
        json={"latitude": 14.5995, "longitude": 120.9842, "name": "Home"},
    )
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["name"] == "Home"
    assert created["latitude"] == 14.5995
    assert created["longitude"] == 120.9842
    assert created["id"] is not None
    assert created["created_at"] is not None
    assert created["updated_at"] is not None

    address_id = created["id"]

    # ------------------------------------------------------------------
    # 2. Retrieve by id
    # ------------------------------------------------------------------
    r = client.get(f"/api/v1/addresses/{address_id}")
    assert r.status_code == 200
    fetched = r.json()
    assert fetched["id"] == address_id
    assert fetched["name"] == "Home"
    assert fetched["latitude"] == 14.5995
    assert fetched["longitude"] == 120.9842

    # ------------------------------------------------------------------
    # 3. List all — confirm the created address is present
    # ------------------------------------------------------------------
    r = client.get("/api/v1/addresses/")
    assert r.status_code == 200
    all_ids = [a["id"] for a in r.json()]
    assert address_id in all_ids

    # ------------------------------------------------------------------
    # 4. Update — rename only; coordinates must remain unchanged
    # ------------------------------------------------------------------
    r = client.put(f"/api/v1/addresses/{address_id}", json={"name": "Office"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "Office"
    assert updated["latitude"] == 14.5995   # unchanged
    assert updated["longitude"] == 120.9842  # unchanged

    # ------------------------------------------------------------------
    # 5. Nearby search — 1 km radius centred on the address itself
    # ------------------------------------------------------------------
    r = client.get(
        "/api/v1/addresses/nearby",
        params={"latitude": 14.5995, "longitude": 120.9842, "radius_km": 1},
    )
    assert r.status_code == 200
    nearby_ids = [a["id"] for a in r.json()]
    assert address_id in nearby_ids

    # ------------------------------------------------------------------
    # 6. Delete
    # ------------------------------------------------------------------
    r = client.delete(f"/api/v1/addresses/{address_id}")
    assert r.status_code == 200

    # ------------------------------------------------------------------
    # 7. Confirm the address is gone
    # ------------------------------------------------------------------
    r = client.get(f"/api/v1/addresses/{address_id}")
    assert r.status_code == 404
