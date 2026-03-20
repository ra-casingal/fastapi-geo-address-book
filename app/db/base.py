"""SQLAlchemy declarative base.

All ORM model classes must inherit from ``Base`` so that
``Base.metadata.create_all()`` in ``app/main.py`` picks them up.

Example::

    from app.db.base import Base

    class Address(Base):
        __tablename__ = "addresses"
        ...
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models.

    Inheriting from this class registers the model's table with
    ``Base.metadata``, enabling schema creation and introspection.
    """

    pass
