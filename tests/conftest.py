import os
import pytest
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import Model, get_db
from app.main import app

# ---------------------------------------------------------------------------
# In-memory SQLite для тестов
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(autouse=True, scope="session")
async def setup_test_db():
    """Однократное создание таблиц в начале сессии тестов."""
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Свежая сессия БД для каждого теста с откатом после него."""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


# Подмена зависимости get_db
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный HTTP-клиент для тестирования."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac