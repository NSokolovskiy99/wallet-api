import uuid
from decimal import Decimal
from sqlalchemy import Numeric, UUID, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Model

class Wallet(Model):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        default=Decimal("0.00")
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="balance_check_positive"),
    )