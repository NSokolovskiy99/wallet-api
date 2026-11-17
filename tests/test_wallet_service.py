import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet
from app.schemas.wallet import OperationType
from app.services.wallet import WalletService
from app.core.exception import (
    WalletNotFoundException,
    InsufficientFundsException,
)



FAKE_UUID = uuid.UUID("12345678-1234-5678-1234-567812345678")


def _make_wallet(balance: Decimal = Decimal("0.00")) -> Wallet:
    """Создаёт объект Wallet без обращения к БД."""
    return Wallet(id=FAKE_UUID, balance=balance)



# create_wallet
async def test_create_wallet():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Act
    wallet = await WalletService.create_wallet(mock_session)

    # Assert
    assert wallet.balance == Decimal("0.00")
    mock_session.add.assert_called_once_with(wallet)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(wallet)



# get_wallet
async def test_get_wallet_found():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.get = AsyncMock(return_value=_make_wallet(Decimal("50.00")))

    # Act
    wallet = await WalletService.get_wallet(mock_session, FAKE_UUID)

    # Assert
    assert wallet.balance == Decimal("50.00")
    mock_session.get.assert_awaited_once_with(Wallet, FAKE_UUID)


async def test_get_wallet_not_found():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.get = AsyncMock(return_value=None)

    # Act / Assert
    with pytest.raises(WalletNotFoundException):
        await WalletService.get_wallet(mock_session, FAKE_UUID)



# handle_operation — DEPOSIT
async def test_deposit_operation():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=_make_wallet())
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    # Act
    wallet = await WalletService.handle_operation(
        mock_session, FAKE_UUID, OperationType.DEPOSIT, Decimal("100.00")
    )

    # Assert
    assert wallet.balance == Decimal("100.00")
    mock_session.commit.assert_awaited_once()



# handle_operation — WITHDRAW
async def test_withdraw_operation():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(
        return_value=_make_wallet(Decimal("200.00"))
    )
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    # Act
    wallet = await WalletService.handle_operation(
        mock_session, FAKE_UUID, OperationType.WITHDRAW, Decimal("50.00")
    )

    # Assert
    assert wallet.balance == Decimal("150.00")
    mock_session.commit.assert_awaited_once()


async def test_withdraw_insufficient_funds():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(
        return_value=_make_wallet(Decimal("10.00"))
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Act / Assert
    with pytest.raises(InsufficientFundsException):
        await WalletService.handle_operation(
            mock_session, FAKE_UUID, OperationType.WITHDRAW, Decimal("50.00")
        )
    mock_session.commit.assert_not_awaited()


async def test_withdraw_wallet_not_found():
    # Arrange
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Act / Assert
    with pytest.raises(WalletNotFoundException):
        await WalletService.handle_operation(
            mock_session, FAKE_UUID, OperationType.WITHDRAW, Decimal("10.00")
        )
    mock_session.commit.assert_not_awaited()