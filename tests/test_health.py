from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient):
    # Arrange — нет подготовки, эндпоинт не зависит от данных

    # Act
    response = await client.get("/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}