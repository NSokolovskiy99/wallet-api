from decimal import Decimal
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet
from app.schemas.wallet import OperationType
from app.core.exception import WalletNotFoundException, InsufficientFundsException


class WalletService:
    @staticmethod
    async def get_wallet(session: AsyncSession, wallet_id: uuid.UUID) -> Wallet:
        wallet = await session.get(Wallet, wallet_id)
        if not wallet:
            raise WalletNotFoundException()
        return wallet
    

    @staticmethod
    async def create_wallet(session: AsyncSession) -> Wallet:
        wallet = Wallet(balance=Decimal("0.00"))
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet) 
        return wallet


    @staticmethod
    async def handle_operation(
        session: AsyncSession,
        wallet_id: uuid.UUID,
        operation_type: OperationType,
        amount: Decimal
    ) -> Wallet:
        query = (
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
        )

        result = await session.execute(query)
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise WalletNotFoundException()

        if operation_type == OperationType.DEPOSIT:
            wallet.balance += amount

        elif operation_type == OperationType.WITHDRAW:
            if wallet.balance < amount:
                raise InsufficientFundsException()
            wallet.balance -= amount

        await session.commit()
        return wallet