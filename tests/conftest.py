import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_db
from app.main import app
from app.models import Base

# Configure test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    return create_async_engine(TEST_DATABASE_URL, future=True, echo=True)


@pytest.fixture(scope="session")
async def test_session(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    yield async_session
    await test_engine.dispose()


@pytest.fixture
def override_get_db(test_session):
    async def _get_db():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db


@pytest.fixture
def client(override_get_db):
    from fastapi.testclient import TestClient

    return TestClient(app)
