import uuid
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletRequest(BaseModel):
    operation_type: OperationType = Field(description="Тип операции")
    amount: Decimal = Field(
        gt=0, decimal_places=2, description="Сумма операции", examples=[150.50]
    )


class WalletResponse(BaseModel):
    id: uuid.UUID = Field(description="ID кошелька")
    balance: Decimal = Field(description="Баланс кошелька")

    model_config = ConfigDict(from_attributes=True)