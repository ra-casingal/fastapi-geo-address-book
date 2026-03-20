"""Tests for the HTTP API layer (app/api/routes/address.py).

Uses the ``client`` fixture from conftest.py, which provides a TestClient
backed by an isolated in-memory database.  Each test starts with a clean
database due to the per-test transaction rollback in the session fixture.
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create(client: TestClient, lat: float = 51.5074, lon: float = -0.1278, name: str = "London") -> dict:
    """POST a new address and return the response body."""
    r = client.post("/api/v1/addresses/", json={"latitude": lat, "longitude": lon, "name": name})
    assert r.status_code == 201
    return r.json()


# ---------------------------------------------------------------------------
# POST /api/v1/addresses/
# ---------------------------------------------------------------------------

class TestCreateAddress:
    def test_creates_address_returns_201(self, client: TestClient):
        r = client.post("/api/v1/addresses/", json={"latitude": 51.5074, "longitude": -0.1278, "name": "London"})
        assert r.status_code == 201
        body = r.json()
        assert body["id"] is not None
        assert body["latitude"] == 51.5074
        assert body["longitude"] == -0.1278
        assert body["name"] == "London"

    def test_name_is_optional(self, client: TestClient):
        r = client.post("/api/v1/addresses/", json={"latitude": 0.0, "longitude": 0.0})
        assert r.status_code == 201
        assert r.json()["name"] is None

    def test_invalid_latitude_returns_422(self, client: TestClient):
        r = client.post("/api/v1/addresses/", json={"latitude": 91.0, "longitude": 0.0})
        assert r.status_code == 422

    def test_invalid_longitude_returns_422(self, client: TestClient):
        r = client.post("/api/v1/addresses/", json={"latitude": 0.0, "longitude": 181.0})
        assert r.status_code == 422

    def test_missing_latitude_returns_422(self, client: TestClient):
        r = client.post("/api/v1/addresses/", json={"longitude": 0.0})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/addresses/
# ---------------------------------------------------------------------------

class TestListAddresses:
    def test_empty_list_by_default(self, client: TestClient):
        r = client.get("/api/v1/addresses/")
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_created_addresses(self, client: TestClient):
        _create(client, name="London")
        _create(client, lat=48.8566, lon=2.3522, name="Paris")
        r = client.get("/api/v1/addresses/")
        assert r.status_code == 200
        names = [a["name"] for a in r.json()]
        assert "London" in names
        assert "Paris" in names

    def test_pagination_limit(self, client: TestClient):
        _create(client, name="A")
        _create(client, name="B")
        _create(client, name="C")
        r = client.get("/api/v1/addresses/?limit=2")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_pagination_skip(self, client: TestClient):
        _create(client, name="First")
        _create(client, name="Second")
        r = client.get("/api/v1/addresses/?skip=1&limit=1")
        assert r.status_code == 200
        assert len(r.json()) == 1


# ---------------------------------------------------------------------------
# GET /api/v1/addresses/{id}
# ---------------------------------------------------------------------------

class TestGetAddress:
    def test_returns_existing_address(self, client: TestClient):
        created = _create(client)
        r = client.get(f"/api/v1/addresses/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_returns_404_for_missing_id(self, client: TestClient):
        r = client.get("/api/v1/addresses/99999")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/v1/addresses/{id}
# ---------------------------------------------------------------------------

class TestUpdateAddress:
    def test_updates_name(self, client: TestClient):
        created = _create(client, name="Old Name")
        r = client.put(f"/api/v1/addresses/{created['id']}", json={"name": "New Name"})
        assert r.status_code == 200
        assert r.json()["name"] == "New Name"

    def test_partial_update_preserves_other_fields(self, client: TestClient):
        created = _create(client, lat=51.5074, lon=-0.1278, name="London")
        r = client.put(f"/api/v1/addresses/{created['id']}", json={"name": "Updated"})
        body = r.json()
        assert body["latitude"] == 51.5074
        assert body["longitude"] == -0.1278

    def test_returns_404_for_missing_id(self, client: TestClient):
        r = client.put("/api/v1/addresses/99999", json={"name": "Ghost"})
        assert r.status_code == 404

    def test_invalid_coordinate_returns_422(self, client: TestClient):
        created = _create(client)
        r = client.put(f"/api/v1/addresses/{created['id']}", json={"latitude": 200.0})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /api/v1/addresses/{id}
# ---------------------------------------------------------------------------

class TestDeleteAddress:
    def test_deletes_existing_address(self, client: TestClient):
        created = _create(client)
        r = client.delete(f"/api/v1/addresses/{created['id']}")
        assert r.status_code == 200

    def test_deleted_address_is_no_longer_accessible(self, client: TestClient):
        created = _create(client)
        client.delete(f"/api/v1/addresses/{created['id']}")
        r = client.get(f"/api/v1/addresses/{created['id']}")
        assert r.status_code == 404

    def test_returns_404_for_missing_id(self, client: TestClient):
        r = client.delete("/api/v1/addresses/99999")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/addresses/nearby
# ---------------------------------------------------------------------------

class TestNearbyAddresses:
    def test_returns_address_within_radius(self, client: TestClient):
        _create(client, lat=51.5074, lon=-0.1278, name="London")
        r = client.get("/api/v1/addresses/nearby?latitude=51.5074&longitude=-0.1278&radius_km=10")
        assert r.status_code == 200
        names = [a["name"] for a in r.json()]
        assert "London" in names

    def test_excludes_address_outside_radius(self, client: TestClient):
        # London → Berlin is ~930 km; 400 km radius should exclude Berlin
        _create(client, lat=51.5074, lon=-0.1278, name="London")
        _create(client, lat=52.5200, lon=13.4050, name="Berlin")
        r = client.get("/api/v1/addresses/nearby?latitude=51.5074&longitude=-0.1278&radius_km=400")
        assert r.status_code == 200
        names = [a["name"] for a in r.json()]
        assert "London" in names
        assert "Berlin" not in names

    def test_empty_result_when_no_matches(self, client: TestClient):
        _create(client, lat=35.6762, lon=139.6503, name="Tokyo")
        r = client.get("/api/v1/addresses/nearby?latitude=51.5074&longitude=-0.1278&radius_km=100")
        assert r.status_code == 200
        assert r.json() == []

    def test_missing_required_params_returns_422(self, client: TestClient):
        r = client.get("/api/v1/addresses/nearby?latitude=51.5074")
        assert r.status_code == 422

    def test_zero_radius_returns_422(self, client: TestClient):
        r = client.get("/api/v1/addresses/nearby?latitude=0&longitude=0&radius_km=0")
        assert r.status_code == 422
