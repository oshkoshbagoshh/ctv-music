"""
Payments module (stub)

This module will define interfaces for creating and confirming payment intents.
No provider integration is included yet; methods raise NotImplementedError.
"""
from dataclasses import dataclass
from typing import Optional

from .models import Order


@dataclass
class PaymentIntent:
    order_id: int
    client_secret: Optional[str] = None
    status: str = "requires_confirmation"


class PaymentsService:
    def create_intent(self, order: Order) -> PaymentIntent:
        """Create a payment intent for an order.

        TODO: integrate with a real payment processor and persist state.
        """
        raise NotImplementedError("PaymentsService.create_intent is not implemented yet")

    def confirm_intent(self, order: Order, payload: dict) -> PaymentIntent:
        """Confirm a previously created intent for an order."""
        raise NotImplementedError("PaymentsService.confirm_intent is not implemented yet")
