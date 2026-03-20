"""CRUD service layer for the Address resource.

All database mutations go through this module.  Functions accept a
``Session`` and schema objects as arguments, keeping them independent of
HTTP concerns (no ``HTTPException`` is raised here).

Typical usage from a route handler::

    from sqlalchemy.orm import Session
    from app.db.deps import get_db
    from app.services import address_service

    @router.get("/{address_id}", response_model=AddressResponse)
    def read_address(address_id: int, db: Session = Depends(get_db)):
        address = address_service.get_address(db, address_id)
        if address is None:
            raise HTTPException(status_code=404, detail="Address not found")
        return address
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate


def create_address(db: Session, address_in: AddressCreate) -> Address:
    """Insert a new address record and return it with all DB-generated fields.

    Args:
        db: Active database session.
        address_in: Validated creation payload.

    Returns:
        The newly created ``Address`` ORM instance, refreshed from the DB.
    """
    db_address = Address(**address_in.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def get_address(db: Session, address_id: int) -> Optional[Address]:
    """Fetch a single address by primary key.

    Args:
        db: Active database session.
        address_id: Primary key of the address to retrieve.

    Returns:
        The matching ``Address`` instance, or ``None`` if not found.
    """
    return db.get(Address, address_id)


def get_addresses(db: Session, skip: int = 0, limit: int = 100) -> list[Address]:
    """Return a paginated list of addresses ordered by id.

    Args:
        db: Active database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A list of ``Address`` instances (may be empty).
    """
    return db.query(Address).order_by(Address.id).offset(skip).limit(limit).all()


def update_address(
    db: Session,
    address_id: int,
    address_in: AddressUpdate,
) -> Optional[Address]:
    """Apply a partial update to an existing address.

    Only fields explicitly provided in ``address_in`` are written; omitted
    fields are left unchanged.  The session is committed only when at least
    one field has changed.

    Args:
        db: Active database session.
        address_id: Primary key of the address to update.
        address_in: Partial update payload (only set fields are applied).

    Returns:
        The updated ``Address`` instance, or ``None`` if not found.
    """
    db_address = db.get(Address, address_id)
    if db_address is None:
        return None

    changes = address_in.model_dump(exclude_unset=True)
    if not changes:
        return db_address

    for field, value in changes.items():
        setattr(db_address, field, value)

    db.commit()
    db.refresh(db_address)
    return db_address


def delete_address(db: Session, address_id: int) -> bool:
    """Delete an address by primary key.

    Args:
        db: Active database session.
        address_id: Primary key of the address to delete.

    Returns:
        ``True`` if the record was found and deleted, ``False`` otherwise.
    """
    db_address = db.get(Address, address_id)
    if db_address is None:
        return False

    db.delete(db_address)
    db.commit()
    return True
