# ============================================================================
# conftest.py — shared pytest setup for ALL test files in this directory
# ============================================================================
# WHY this file exists:
# Both test_api.py and test_project.py need a test database, a get_db override,
# and the same fixtures. If each file sets `app.dependency_overrides` at import
# time, they CLOBBER each other (the app object is shared, last import wins) —
# so running `pytest tests/` fails even though each file passes alone.
#
# pytest automatically loads conftest.py and makes its fixtures available to
# every test in the directory. Defining the engine + override + fixtures ONCE
# here removes the duplication and the cross-file pollution.
# ============================================================================

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from auth import get_db
from app import app

# ----------------------------------------------------------------------------
# One shared in-memory test database.
# poolclass=StaticPool keeps a SINGLE connection, so create_all() (in the
# fixture) and the request sessions all see the same in-memory DB. Without it,
# each connection gets its own empty in-memory DB -> "no such table".
# ----------------------------------------------------------------------------
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Test database session, swapped in for the real get_db."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Set the override ONCE, in one place, for the whole test session.
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Fresh tables before each test, dropped after — clean slate per test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """A TestClient bound to the app (with the test DB override active)."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register + log in a user, return ready-to-use Bearer auth headers."""
    client.post("/register", json={"username": "testuser", "password": "testpass123"})
    resp = client.post("/login", json={"username": "testuser", "password": "testpass123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
