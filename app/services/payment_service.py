"""
Payment processing service.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict
from enum import Enum

from app.config import Config
from app.utils.helpers import format_currency
from app.utils.validators import validate_card_number

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentService:
    """Handles payment processing through a payment gateway."""

    def __init__(self, config: Config):
        self.config = config
        self._transactions: Dict[str, dict] = {}

    def charge(self, amount: float, card_number: str, currency: str = "USD") -> dict:
        """
        Simulate charging a credit card.
        Returns a transaction record.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if not validate_card_number(card_number):
            raise ValueError("Invalid card number.")

        transaction_id = str(uuid.uuid4())
        masked_card = f"****-****-****-{card_number[-4:]}"

        # Simulate gateway call (always succeeds in dev mode)
        status = PaymentStatus.SUCCESS if self.config.DEBUG else self._call_gateway(
            amount, card_number, currency
        )

        record = {
            "transaction_id": transaction_id,
            "amount": amount,
            "formatted_amount": format_currency(amount, currency),
            "card": masked_card,
            "currency": currency,
            "status": status.value,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._transactions[transaction_id] = record
        logger.info(f"Payment {status.value}: {format_currency(amount)} [{transaction_id}]")
        return record

    def refund(self, transaction_id: str) -> Optional[dict]:
        """Refund a previously charged transaction."""
        record = self._transactions.get(transaction_id)
        if not record:
            logger.warning(f"Refund failed: transaction {transaction_id} not found.")
            return None
        if record["status"] != PaymentStatus.SUCCESS.value:
            raise ValueError("Only successful transactions can be refunded.")
        record["status"] = PaymentStatus.REFUNDED.value
        record["refunded_at"] = datetime.utcnow().isoformat()
        logger.info(f"Refund issued for transaction {transaction_id}")
        return record

    def get_transaction(self, transaction_id: str) -> Optional[dict]:
        return self._transactions.get(transaction_id)

    def _call_gateway(self, amount: float, card: str, currency: str) -> PaymentStatus:
        """Stub: would call an external payment gateway API."""
        logger.debug(f"Calling gateway for {format_currency(amount, currency)}")
        return PaymentStatus.SUCCESS
