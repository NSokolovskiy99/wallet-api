import uuid
from fastapi import APIRouter, HTTPException, status

from app.core.database import SessionDep
from app.core.exception import WalletNotFoundException, InsufficientFundsException
from app.schemas.wallet import WalletRequest, WalletResponse
from app.services.wallet import WalletService

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


@router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(session: SessionDep):
    return await WalletService.create_wallet(session)


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet_balance(session: SessionDep, wallet_id: uuid.UUID):
    try:
        wallet = await WalletService.get_wallet(session, wallet_id)
    except WalletNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    return wallet


@router.post("/{wallet_id}/operation", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def wallet_operation(session: SessionDep, wallet_id: uuid.UUID, body: WalletRequest):
    try:
        wallet = await WalletService.handle_operation(
            session=session,
            wallet_id=wallet_id,
            operation_type=body.operation_type,
            amount=body.amount 
        )
        return wallet
    except WalletNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except InsufficientFundsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )    