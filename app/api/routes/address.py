"""API routes for the Address resource.

All route handlers are intentionally thin: they validate HTTP-level concerns,
delegate to the service layer, and translate service results into HTTP responses.
No database logic lives here.

Route overview:

    POST   /addresses              Create a new address
    GET    /addresses              List all addresses (paginated)
    GET    /addresses/nearby       Find addresses within a radius
    GET    /addresses/{address_id} Fetch a single address
    PUT    /addresses/{address_id} Replace / update an address
    DELETE /addresses/{address_id} Remove an address
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate
from app.services import address_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/addresses", tags=["Addresses"])

# ---------------------------------------------------------------------------
# Type alias for the injected DB session — keeps signatures concise
# ---------------------------------------------------------------------------
DB = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(body: AddressCreate, db: DB) -> AddressResponse:
    """Create a new address.

    Args:
        body: Validated address creation payload.
        db: Injected database session.

    Returns:
        The newly created address, including its generated ``id`` and timestamps.
    """
    logger.info("Creating address: lat=%s lon=%s name=%r", body.latitude, body.longitude, body.name)
    try:
        address = address_service.create_address(db, body)
    except Exception:
        logger.error("Unexpected error creating address.", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
    logger.info("Address created successfully: id=%d", address.id)
    return address


@router.get("/", response_model=list[AddressResponse])
def list_addresses(
    db: DB,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip.")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="Maximum records to return.")] = 100,
) -> list[AddressResponse]:
    """Return a paginated list of all addresses.

    Args:
        db: Injected database session.
        skip: Offset for pagination (default 0).
        limit: Page size, capped at 500 (default 100).

    Returns:
        A list of address records (may be empty).
    """
    logger.info("Listing addresses: skip=%d limit=%d", skip, limit)
    try:
        return address_service.get_addresses(db, skip=skip, limit=limit)
    except Exception:
        logger.error("Unexpected error listing addresses.", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )


# NOTE: /nearby MUST be declared before /{address_id}.
# FastAPI matches routes in order; placing a literal path segment after a
# dynamic one would cause "nearby" to be parsed as an integer and raise 422.
@router.get("/nearby", response_model=list[AddressResponse])
def get_nearby_addresses(
    db: DB,
    latitude: Annotated[float, Query(ge=-90, le=90, description="Reference latitude.")],
    longitude: Annotated[float, Query(ge=-180, le=180, description="Reference longitude.")],
    radius_km: Annotated[float, Query(gt=0, description="Search radius in kilometres.")],
) -> list[AddressResponse]:
    """Return all addresses within a geodesic radius of the given coordinates.

    Args:
        db: Injected database session.
        latitude: Reference point latitude in decimal degrees.
        longitude: Reference point longitude in decimal degrees.
        radius_km: Search radius in kilometres (must be > 0).

    Returns:
        All addresses whose geodesic distance from the reference point is
        less than or equal to ``radius_km``.
    """
    logger.info("Nearby search: lat=%s lon=%s radius_km=%s", latitude, longitude, radius_km)
    try:
        results = address_service.get_addresses_within_distance(
            db, latitude=latitude, longitude=longitude, radius_km=radius_km
        )
    except Exception:
        logger.error("Unexpected error during nearby search.", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
    logger.info("Nearby search returned %d result(s).", len(results))
    return results


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: DB) -> AddressResponse:
    """Fetch a single address by ID.

    Args:
        address_id: Primary key of the address to retrieve.
        db: Injected database session.

    Returns:
        The matching address record.

    Raises:
        HTTPException: 404 if no address with ``address_id`` exists.
    """
    logger.info("Fetching address id=%d", address_id)
    try:
        address = address_service.get_address(db, address_id)
    except Exception:
        logger.error("Unexpected error fetching address id=%d.", address_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
    if address is None:
        logger.warning("Address id=%d not found.", address_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with id={address_id} not found.",
        )
    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, body: AddressUpdate, db: DB) -> AddressResponse:
    """Update an existing address (partial update supported).

    Only fields present in the request body are modified; omitted fields
    retain their current values.

    Args:
        address_id: Primary key of the address to update.
        body: Partial or full update payload.
        db: Injected database session.

    Returns:
        The updated address record.

    Raises:
        HTTPException: 404 if no address with ``address_id`` exists.
    """
    logger.info("Updating address id=%d with fields: %s", address_id, body.model_dump(exclude_unset=True))
    try:
        address = address_service.update_address(db, address_id, body)
    except Exception:
        logger.error("Unexpected error updating address id=%d.", address_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
    if address is None:
        logger.warning("Update failed — address id=%d not found.", address_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with id={address_id} not found.",
        )
    logger.info("Address id=%d updated successfully.", address_id)
    return address


@router.delete("/{address_id}", status_code=status.HTTP_200_OK)
def delete_address(address_id: int, db: DB) -> dict[str, str]:
    """Delete an address by ID.

    Args:
        address_id: Primary key of the address to delete.
        db: Injected database session.

    Returns:
        A confirmation message.

    Raises:
        HTTPException: 404 if no address with ``address_id`` exists.
    """
    logger.info("Deleting address id=%d", address_id)
    try:
        deleted = address_service.delete_address(db, address_id)
    except Exception:
        logger.error("Unexpected error deleting address id=%d.", address_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
    if not deleted:
        logger.warning("Delete failed — address id=%d not found.", address_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with id={address_id} not found.",
        )
    logger.info("Address id=%d deleted successfully.", address_id)
    return {"message": f"Address {address_id} deleted successfully."}
