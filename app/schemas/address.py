"""Pydantic schemas for the Address resource.

Schema hierarchy:

    AddressBase          shared readable/writable fields
        └── AddressCreate    POST body (no extra fields needed)
    AddressUpdate        PATCH body (all fields optional)
    AddressResponse      GET / response body (includes DB-generated fields)
"""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Reusable annotated types with coordinate constraints
# ---------------------------------------------------------------------------

Latitude = Annotated[
    float,
    Field(ge=-90.0, le=90.0, description="WGS-84 latitude in decimal degrees."),
]

Longitude = Annotated[
    float,
    Field(ge=-180.0, le=180.0, description="WGS-84 longitude in decimal degrees."),
]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AddressBase(BaseModel):
    """Fields shared by create and response schemas.

    Attributes:
        latitude: WGS-84 latitude, validated to [-90, 90].
        longitude: WGS-84 longitude, validated to [-180, 180].
        name: Optional human-readable label (max 100 characters).
    """

    latitude: Latitude
    longitude: Longitude
    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional label for this location (e.g. 'Home', 'Office').",
    )


class AddressCreate(AddressBase):
    """Request body for ``POST /addresses``.

    Inherits all fields and validation rules from ``AddressBase``.
    ``latitude`` and ``longitude`` are required; ``name`` is optional.
    """


class AddressUpdate(BaseModel):
    """Request body for ``PATCH /addresses/{id}``.

    All fields are optional so clients can send only the fields they want
    to change (partial update / JSON Merge Patch semantics).

    Attributes:
        latitude: New latitude, or omitted to leave unchanged.
        longitude: New longitude, or omitted to leave unchanged.
        name: New label, or omitted to leave unchanged.
    """

    latitude: Optional[Latitude] = None
    longitude: Optional[Longitude] = None
    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional label for this location.",
    )


class AddressResponse(AddressBase):
    """Response body returned by all address endpoints.

    Extends ``AddressBase`` with the database-generated fields that are
    not accepted as input.

    Attributes:
        id: Auto-assigned primary key.
        created_at: UTC timestamp of record creation.
        updated_at: UTC timestamp of the most recent update.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Auto-assigned primary key.")
    created_at: datetime = Field(description="UTC timestamp of record creation.")
    updated_at: datetime = Field(description="UTC timestamp of the last update.")
