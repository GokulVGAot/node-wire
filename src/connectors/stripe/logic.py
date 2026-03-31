from __future__ import annotations

import logging

import stripe

from runtime import BaseConnector

from .schema import ChargeInput, ChargeOutput

logger = logging.getLogger("connectors.stripe")


class StripeChargeConnector(BaseConnector[ChargeInput, ChargeOutput]):
    """
    Stripe connector for creating charges using the official Stripe SDK.
    """

    connector_id = "stripe"
    action = "charge"

    async def internal_execute(self, params: ChargeInput, *, trace_id: str) -> ChargeOutput:
        # API key is expected to be provided by SecretProvider.
        api_key = self.secret_provider.get_secret("stripe_api_key")
        stripe.api_key = api_key

        logger.info(
            "Creating Stripe charge",
            extra={
                "trace_id": trace_id,
                "connector_id": self.connector_id,
                "action": self.action,
                "amount": params.amount,
                "currency": params.currency,
            },
        )

        try:
            charge = await stripe.Charge.create(  # type: ignore[attr-defined]
                amount=params.amount,
                currency=params.currency,
                source=params.source,
                description=params.description,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Stripe charge creation failed",
                extra={
                    "trace_id": trace_id,
                    "connector_id": self.connector_id,
                    "action": self.action,
                    "amount": params.amount,
                    "currency": params.currency,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
            )
            raise

        logger.info(
            "Stripe charge created successfully",
            extra={
                "trace_id": trace_id,
                "connector_id": self.connector_id,
                "action": self.action,
                "charge_id": charge.get("id"),
            },
        )

        return ChargeOutput(
            charge_id=charge.get("id"),
            receipt_url=charge.get("receipt_url"),
        )

