# rental/payments/gateways.py
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class DepositResult:
    ok: bool
    provider: str
    transaction_id: Optional[str]
    error: Optional[str] = None
    meta: Optional[Dict] = None

class PaymentGateway:
    """Interface"""
    def create_deposit(self, *, booking, amount_cents: int, meta: dict | None = None) -> DepositResult:
        raise NotImplementedError

class MockStripeGateway(PaymentGateway):
    """No real charge; simulates success and returns a fake id."""
    def create_deposit(self, *, booking, amount_cents: int, meta: dict | None = None) -> DepositResult:
        fake_tx_id = f"cs_test_{booking.id:06d}"
        return DepositResult(ok=True, provider="mock_stripe", transaction_id=fake_tx_id, meta={"amount_cents": amount_cents})
