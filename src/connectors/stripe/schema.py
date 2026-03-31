from __future__ import annotations

from pydantic import BaseModel


class ChargeInput(BaseModel):
    amount: int
    currency: str
    source: str
    description: str | None = None


class ChargeOutput(BaseModel):
    charge_id: str
    receipt_url: str | None = None

