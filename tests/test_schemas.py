"""Tests for Pydantic schemas (app/schemas/address.py).

Validates that coordinate constraints and field-length rules are enforced
at the schema level, before any service or database code is involved.
"""

import pytest
from pydantic import ValidationError

from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse


# ---------------------------------------------------------------------------
# AddressCreate — valid inputs
# ---------------------------------------------------------------------------

class TestAddressCreateValid:
    def test_minimal_valid(self):
        """Latitude + longitude alone are sufficient."""
        addr = AddressCreate(latitude=0.0, longitude=0.0)
        assert addr.latitude == 0.0
        assert addr.longitude == 0.0
        assert addr.name is None

    def test_with_name(self):
        addr = AddressCreate(latitude=51.5074, longitude=-0.1278, name="London")
        assert addr.name == "London"

    def test_boundary_latitude_min(self):
        addr = AddressCreate(latitude=-90.0, longitude=0.0)
        assert addr.latitude == -90.0

    def test_boundary_latitude_max(self):
        addr = AddressCreate(latitude=90.0, longitude=0.0)
        assert addr.latitude == 90.0

    def test_boundary_longitude_min(self):
        addr = AddressCreate(latitude=0.0, longitude=-180.0)
        assert addr.longitude == -180.0

    def test_boundary_longitude_max(self):
        addr = AddressCreate(latitude=0.0, longitude=180.0)
        assert addr.longitude == 180.0

    def test_name_at_max_length(self):
        """A name of exactly 100 characters must be accepted."""
        addr = AddressCreate(latitude=0.0, longitude=0.0, name="x" * 100)
        assert len(addr.name) == 100


# ---------------------------------------------------------------------------
# AddressCreate — invalid inputs
# ---------------------------------------------------------------------------

class TestAddressCreateInvalid:
    def test_latitude_too_low(self):
        with pytest.raises(ValidationError) as exc_info:
            AddressCreate(latitude=-90.1, longitude=0.0)
        assert "latitude" in str(exc_info.value)

    def test_latitude_too_high(self):
        with pytest.raises(ValidationError):
            AddressCreate(latitude=90.1, longitude=0.0)

    def test_longitude_too_low(self):
        with pytest.raises(ValidationError) as exc_info:
            AddressCreate(latitude=0.0, longitude=-180.1)
        assert "longitude" in str(exc_info.value)

    def test_longitude_too_high(self):
        with pytest.raises(ValidationError):
            AddressCreate(latitude=0.0, longitude=180.1)

    def test_name_too_long(self):
        """A name exceeding 100 characters must be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddressCreate(latitude=0.0, longitude=0.0, name="x" * 101)
        assert "name" in str(exc_info.value)

    def test_missing_latitude(self):
        with pytest.raises(ValidationError):
            AddressCreate(longitude=0.0)

    def test_missing_longitude(self):
        with pytest.raises(ValidationError):
            AddressCreate(latitude=0.0)


# ---------------------------------------------------------------------------
# AddressUpdate — all fields are optional
# ---------------------------------------------------------------------------

class TestAddressUpdate:
    def test_empty_update_is_valid(self):
        """An empty payload is valid for a partial update."""
        update = AddressUpdate()
        assert update.latitude is None
        assert update.longitude is None
        assert update.name is None

    def test_partial_update_latitude_only(self):
        update = AddressUpdate(latitude=48.8566)
        assert update.latitude == 48.8566
        assert update.longitude is None

    def test_update_invalid_latitude(self):
        with pytest.raises(ValidationError):
            AddressUpdate(latitude=91.0)

    def test_update_name_too_long(self):
        with pytest.raises(ValidationError):
            AddressUpdate(name="y" * 101)
