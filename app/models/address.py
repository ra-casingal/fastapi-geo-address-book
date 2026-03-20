"""Address ORM model.

Represents a geographic address entry with optional label,
coordinates, and automatic audit timestamps.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Address(Base):
    """ORM model for the ``addresses`` table.

    Attributes:
        id: Auto-incrementing primary key.
        latitude: WGS-84 latitude in decimal degrees (-90 to 90).
        longitude: WGS-84 longitude in decimal degrees (-180 to 180).
        name: Optional human-readable label (e.g. "Home", "Office").
        created_at: UTC timestamp set automatically on insert.
        updated_at: UTC timestamp updated automatically on every change.
    """

    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"Address(id={self.id!r}, name={self.name!r}, "
            f"lat={self.latitude}, lon={self.longitude})"
        )
