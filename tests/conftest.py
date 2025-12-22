import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.api.deps import get_db
from app.db.base import Base

# Import models (register metadata)
from app.models.organization import Organization  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.activity import ActivityLog  # noqa: F401

TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client():
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
