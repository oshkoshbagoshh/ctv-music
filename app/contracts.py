"""
Contracts module (stub)

This module will house the contract generation and signing flow for approved orders.
For now, it exposes interfaces and raises NotImplementedError to indicate TODO work.
"""
from dataclasses import dataclass
from typing import Optional

from .models import Order


@dataclass
class Contract:
    order_id: int
    url: Optional[str] = None
    status: str = "pending"


class ContractService:
    def create_for_order(self, order: Order) -> Contract:
        """Create a contract for the approved order and return a representation.

        TODO: implement storage, PDF generation, and signing provider integration.
        """
        raise NotImplementedError("ContractService.create_for_order is not implemented yet")

    def get_status(self, order: Order) -> str:
        """Return current status of the contract for an order."""
        raise NotImplementedError("ContractService.get_status is not implemented yet")
