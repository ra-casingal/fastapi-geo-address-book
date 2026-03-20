"""SQLAlchemy engine and session factory.

Import ``engine`` when you need direct DDL access (e.g. ``create_all``).
Import ``SessionLocal`` — or, preferably, use the ``get_db`` dependency from
``app.db.deps`` — when you need a transactional session inside a request.
"""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# ``check_same_thread=False`` is a SQLite-only guard that prevents the driver
# from raising an error when the same connection is used across threads.
# SQLAlchemy's session-per-request pattern makes this safe.
_connect_args: dict[str, bool] = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine: Engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
)

#: Session factory bound to the configured engine.
#: Use ``get_db()`` from ``app.db.deps`` in route handlers instead of
#: instantiating SessionLocal directly.
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
