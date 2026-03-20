"""Shared pytest fixtures for the Address Book API test suite.

An isolated in-memory SQLite database is created once per test session.
Tables are created before the first test and dropped afterwards.
Each test function receives a fresh transaction that is rolled back on
teardown, so no test can pollute the state seen by the next one.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.deps import get_db
from app.main import app

# ---------------------------------------------------------------------------
# Engine — shared across the whole session, in-memory database
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite://"  # pure in-memory, no file

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # StaticPool ensures every connection reuses the same in-memory database
    # (the default pool would create a new, empty DB for each connection).
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Session-scoped table lifecycle
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once before the test session and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Function-scoped DB fixture — each test gets an isolated transaction
# ---------------------------------------------------------------------------

@pytest.fixture
def db_session() -> Session:
    """Yield a transactional database session.

    Each test runs inside a transaction that is always rolled back on
    teardown, guaranteeing a clean slate for the next test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# FastAPI dependency override + TestClient
# ---------------------------------------------------------------------------

@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Return a TestClient that uses the isolated test session.

    The real ``get_db`` dependency is overridden so every request shares the
    same transactional session used by the test, enabling assertions on DB
    state without committing anything permanently.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
