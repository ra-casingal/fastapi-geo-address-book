"""FastAPI dependency callables for database access.

Usage in a route::

    from fastapi import Depends
    from sqlalchemy.orm import Session
    from app.db.deps import get_db

    @router.get("/items")
    def list_items(db: Session = Depends(get_db)) -> list[dict]:
        ...
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped database session.

    Opens a new ``Session`` at the start of each request and guarantees it is
    closed — even if the handler raises an exception — via a ``finally`` block.
    The session is **not** automatically committed; handlers must call
    ``db.commit()`` explicitly after mutating state.

    Yields:
        An active ``sqlalchemy.orm.Session`` bound to the configured engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
