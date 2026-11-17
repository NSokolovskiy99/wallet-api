import uuid
from httpx import AsyncClient

WALLETS_ENDPOINT = "/api/v1/wallets"


async def _create_wallet(client: AsyncClient) -> uuid.UUID:
    """Вспомогательная функция: создаёт кошелек и возвращает его ID."""
    resp = await client.post(WALLETS_ENDPOINT)
    assert resp.status_code == 201
    return uuid.UUID(resp.json()["id"])


# POST /api/v1/wallets
async def test_create_wallet(client: AsyncClient):
    # Arrange — новый кошелек, тело запроса не требуется

    # Act
    response = await client.post(WALLETS_ENDPOINT)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["balance"] == "0.00"
    uuid.UUID(data["id"])  # не должен бросить — валидный UUID


# GET /api/v1/wallets/{wallet_id}
async def test_get_wallet_balance(client: AsyncClient):
    # Arrange — создаём кошелек
    wallet_id = await _create_wallet(client)

    # Act
    response = await client.get(f"{WALLETS_ENDPOINT}/{wallet_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == "0.00"
    assert uuid.UUID(data["id"]) == wallet_id


async def test_get_wallet_not_found(client: AsyncClient):
    # Arrange — несуществующий UUID
    fake_id = uuid.UUID("11111111-2222-3333-4444-555555555555")

    # Act
    response = await client.get(f"{WALLETS_ENDPOINT}/{fake_id}")

    # Assert
    assert response.status_code == 404


# POST /api/v1/wallets/{wallet_id}/operation
async def test_deposit(client: AsyncClient):
    # Arrange — создаём кошелек и готовим тело запроса
    wallet_id = await _create_wallet(client)
    body = {"operation_type": "DEPOSIT", "amount": "100.00"}

    # Act
    response = await client.post(f"{WALLETS_ENDPOINT}/{wallet_id}/operation", json=body)

    # Assert
    assert response.status_code == 201
    assert response.json()["balance"] == "100.00"


async def test_withdraw(client: AsyncClient):
    # Arrange — создаём, пополняем, потом снимаем
    wallet_id = await _create_wallet(client)
    await client.post(
        f"{WALLETS_ENDPOINT}/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "200.00"},
    )

    # Act
    response = await client.post(
        f"{WALLETS_ENDPOINT}/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "50.00"},
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["balance"] == "150.00"


async def test_withdraw_insufficient_funds(client: AsyncClient):
    # Arrange — пустой кошелек, пытаемся снять больше, чем есть
    wallet_id = await _create_wallet(client)
    body = {"operation_type": "WITHDRAW", "amount": "100.00"}

    # Act
    response = await client.post(f"{WALLETS_ENDPOINT}/{wallet_id}/operation", json=body)

    # Assert
    assert response.status_code == 400


async def test_withdraw_wallet_not_found(client: AsyncClient):
    # Arrange — операция для несуществующего кошелька
    fake_id = uuid.UUID("11111111-2222-3333-4444-555555555555")
    body = {"operation_type": "WITHDRAW", "amount": "50.00"}

    # Act
    response = await client.post(f"{WALLETS_ENDPOINT}/{fake_id}/operation", json=body)

    # Assert
    assert response.status_code == 404


# Валидация входных данных
async def test_invalid_uuid_format(client: AsyncClient):
    # Arrange — невалидный UUID в path
    invalid_uuid = "not-a-uuid"

    # Act
    response = await client.get(f"{WALLETS_ENDPOINT}/{invalid_uuid}")

    # Assert
    assert response.status_code == 422


async def test_invalid_amount(client: AsyncClient):
    # Arrange — сумма <= 0
    wallet_id = await _create_wallet(client)
    body = {"operation_type": "DEPOSIT", "amount": "-10.00"}

    # Act
    response = await client.post(f"{WALLETS_ENDPOINT}/{wallet_id}/operation", json=body)

    # Assert
    assert response.status_code == 422


async def test_invalid_operation_type(client: AsyncClient):
    # Arrange — несуществующий тип операции
    wallet_id = await _create_wallet(client)
    body = {"operation_type": "TRANSFER", "amount": "50.00"}

    # Act
    response = await client.post(f"{WALLETS_ENDPOINT}/{wallet_id}/operation", json=body)

    # Assert
    assert response.status_code == 422


# Граничные кейсы
async def test_withdraw_exact_balance(client: AsyncClient):
    # Arrange — пополняем на 100 и снимаем ровно всё
    wallet_id = await _create_wallet(client)
    await client.post(
        f"{WALLETS_ENDPOINT}/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.00"},
    )

    # Act
    response = await client.post(
        f"{WALLETS_ENDPOINT}/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "100.00"},
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["balance"] == "0.00"


async def test_zero_amount_returns_422(client: AsyncClient):
    # Arrange — существующий кошелек, нулевая сумма
    wallet_id = await _create_wallet(client)

    # Act
    response = await client.post(
        f"{WALLETS_ENDPOINT}/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "0.00"},
    )

    # Assert
    assert response.status_code == 422


async def test_three_decimal_places_returns_422(client: AsyncClient):
    # Arrange — существующий кошелек, три знака после запятой
    wallet_id = await _create_wallet(client)

    # Act
    response = await client.post(
        f"{WALLETS_ENDPOINT}/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "10.005"},
    )

    # Assert
    assert response.status_code == 422
