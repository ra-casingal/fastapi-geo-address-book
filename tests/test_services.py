"""Tests for the service layer (app/services/address_service.py).

Each test receives a clean, rolled-back database session from conftest.py,
so there is no state leakage between tests.
"""

import pytest
from sqlalchemy.orm import Session

from app.schemas.address import AddressCreate, AddressUpdate
from app.services import address_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make(db: Session, lat: float = 51.5074, lon: float = -0.1278, name: str = "London"):
    """Create and return a persisted address for use in tests."""
    return address_service.create_address(db, AddressCreate(latitude=lat, longitude=lon, name=name))


# ---------------------------------------------------------------------------
# create_address
# ---------------------------------------------------------------------------

class TestCreateAddress:
    def test_returns_address_with_id(self, db_session: Session):
        addr = _make(db_session)
        assert addr.id is not None
        assert addr.latitude == 51.5074
        assert addr.longitude == -0.1278
        assert addr.name == "London"

    def test_timestamps_are_set(self, db_session: Session):
        addr = _make(db_session)
        assert addr.created_at is not None
        assert addr.updated_at is not None

    def test_name_is_optional(self, db_session: Session):
        addr = address_service.create_address(db_session, AddressCreate(latitude=0.0, longitude=0.0))
        assert addr.name is None


# ---------------------------------------------------------------------------
# get_address
# ---------------------------------------------------------------------------

class TestGetAddress:
    def test_returns_existing_address(self, db_session: Session):
        created = _make(db_session)
        fetched = address_service.get_address(db_session, created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_returns_none_for_missing_id(self, db_session: Session):
        result = address_service.get_address(db_session, address_id=99999)
        assert result is None


# ---------------------------------------------------------------------------
# get_addresses
# ---------------------------------------------------------------------------

class TestGetAddresses:
    def test_returns_all_created(self, db_session: Session):
        _make(db_session, name="A")
        _make(db_session, name="B")
        results = address_service.get_addresses(db_session)
        assert len(results) >= 2

    def test_pagination_skip(self, db_session: Session):
        _make(db_session)
        _make(db_session)
        first_page = address_service.get_addresses(db_session, skip=0, limit=1)
        second_page = address_service.get_addresses(db_session, skip=1, limit=1)
        assert len(first_page) == 1
        assert len(second_page) == 1
        assert first_page[0].id != second_page[0].id

    def test_empty_database_returns_empty_list(self, db_session: Session):
        results = address_service.get_addresses(db_session)
        assert results == []


# ---------------------------------------------------------------------------
# update_address
# ---------------------------------------------------------------------------

class TestUpdateAddress:
    def test_partial_update_name(self, db_session: Session):
        addr = _make(db_session)
        updated = address_service.update_address(
            db_session, addr.id, AddressUpdate(name="Updated")
        )
        assert updated is not None
        assert updated.name == "Updated"
        assert updated.latitude == addr.latitude  # unchanged

    def test_partial_update_coordinates(self, db_session: Session):
        addr = _make(db_session)
        updated = address_service.update_address(
            db_session, addr.id, AddressUpdate(latitude=48.8566, longitude=2.3522)
        )
        assert updated.latitude == 48.8566
        assert updated.longitude == 2.3522

    def test_no_fields_returns_unchanged(self, db_session: Session):
        addr = _make(db_session)
        updated = address_service.update_address(db_session, addr.id, AddressUpdate())
        assert updated is not None
        assert updated.name == addr.name

    def test_returns_none_for_missing_id(self, db_session: Session):
        result = address_service.update_address(
            db_session, 99999, AddressUpdate(name="Ghost")
        )
        assert result is None


# ---------------------------------------------------------------------------
# delete_address
# ---------------------------------------------------------------------------

class TestDeleteAddress:
    def test_deletes_existing_address(self, db_session: Session):
        addr = _make(db_session)
        deleted = address_service.delete_address(db_session, addr.id)
        assert deleted is True
        assert address_service.get_address(db_session, addr.id) is None

    def test_returns_false_for_missing_id(self, db_session: Session):
        result = address_service.delete_address(db_session, address_id=99999)
        assert result is False


# ---------------------------------------------------------------------------
# get_addresses_within_distance
# ---------------------------------------------------------------------------

class TestGetAddressesWithinDistance:
    # Approximate real-world distances from London (51.5074, -0.1278):
    #   Paris  (48.8566,  2.3522) ~  340 km
    #   Berlin (52.5200, 13.4050) ~  930 km

    def test_finds_address_within_radius(self, db_session: Session):
        london = _make(db_session, lat=51.5074, lon=-0.1278, name="London")
        _make(db_session, lat=48.8566, lon=2.3522, name="Paris")

        results = address_service.get_addresses_within_distance(
            db_session, latitude=51.5074, longitude=-0.1278, radius_km=400
        )
        names = [r.name for r in results]
        assert "London" in names
        assert "Paris" in names

    def test_excludes_address_outside_radius(self, db_session: Session):
        _make(db_session, lat=51.5074, lon=-0.1278, name="London")
        _make(db_session, lat=52.5200, lon=13.4050, name="Berlin")

        results = address_service.get_addresses_within_distance(
            db_session, latitude=51.5074, longitude=-0.1278, radius_km=400
        )
        names = [r.name for r in results]
        assert "London" in names
        assert "Berlin" not in names

    def test_empty_when_no_matches(self, db_session: Session):
        _make(db_session, lat=35.6762, lon=139.6503, name="Tokyo")

        results = address_service.get_addresses_within_distance(
            db_session, latitude=51.5074, longitude=-0.1278, radius_km=100
        )
        assert results == []
