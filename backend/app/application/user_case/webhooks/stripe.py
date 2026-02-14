from dataclasses import dataclass
import stripe
from datetime import datetime
from typing import Dict, Any
from app.domain.repositories.user import UserRepository
from app.domain.repositories.subscription import SubscriptionRepository
from app.domain.repositories.invoice import InvoiceRepository
from app.domain.repositories.webhook_event import WebhookEventRepository
from app.domain.entities.webhook_event import WebhookEvent
from app.common.exceptions import WebhookProcessingError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class StripeWebhookUseCase:
    user_repo: UserRepository
    sub_repo: SubscriptionRepository
    invoice_repo: InvoiceRepository
    webhook_event_repo: WebhookEventRepository

    async def execute(self, payload: bytes, stripe_signature: str) -> None:
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET.get_secret_value(),
                tolerance=settings.STRIPE_WEBHOOK_TOLERANCE
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid Stripe signature", error=e)
            raise WebhookProcessingError("Invalid signature")

        event_id = event["id"]
        event_type = event["type"]

        # Idempotency check
        existing = await self.webhook_event_repo.get_by_event_id("stripe", event_id)
        if existing:
            if existing.processed:
                logger.info("Stripe webhook already processed", event_id=event_id)
                return
            else:
                # Already received but not processed? Possibly retry
                # We'll process again but mark as processed later
                pass

        # Store event
        webhook_event = WebhookEvent(
            provider="stripe",
            event_id=event_id,
            event_type=event_type,
            payload=event,
            processed=False,
        )
        webhook_event = await self.webhook_event_repo.save(webhook_event)

        try:
            # Process based on event type
            if event_type.startswith("customer.subscription."):
                await self._handle_subscription_event(event)
            elif event_type.startswith("invoice."):
                await self._handle_invoice_event(event)
            elif event_type == "charge.refunded":
                await self._handle_refund_event(event)
            else:
                logger.info("Unhandled Stripe event type", event_type=event_type)

            # Mark as processed
            webhook_event.mark_processed()
            await self.webhook_event_repo.save(webhook_event)

        except Exception as e:
            logger.exception("Error processing Stripe webhook", event_id=event_id, error=e)
            # Increment retry count
            webhook_event.increment_retry()
            await self.webhook_event_repo.save(webhook_event)
            raise WebhookProcessingError(str(e))

    async def _handle_subscription_event(self, event: Dict[str, Any]) -> None:
        stripe_sub = event["data"]["object"]
        sub = await self.sub_repo.get_by_stripe_subscription_id(stripe_sub["id"])
        if not sub:
            # Could be new subscription created via Stripe dashboard? We should have created it locally first.
            logger.warning("Subscription not found locally", stripe_id=stripe_sub["id"])
            return

        sub.update_from_stripe(stripe_sub)
        await self.sub_repo.save(sub)

        # Update user's subscription tier
        user = await self.user_repo.get_by_id(sub.user_id)
        if user:
            # Map stripe price to plan id
            price_id = stripe_sub["items"]["data"][0]["price"]["id"]
            if price_id in [settings.STRIPE_PRICE_PRO, settings.STRIPE_PRICE_PRO_YEARLY]:
                tier = "pro"
            elif price_id in [settings.STRIPE_PRICE_FIRM, settings.STRIPE_PRICE_FIRM_YEARLY]:
                tier = "firm"
            else:
                tier = "free"
            user.update_subscription(tier, stripe_sub["status"])
            await self.user_repo.save(user)

    async def _handle_invoice_event(self, event: Dict[str, Any]) -> None:
        stripe_invoice = event["data"]["object"]
        # Find or create invoice
        invoice = await self.invoice_repo.get_by_stripe_invoice_id(stripe_invoice["id"])
        if not invoice:
            from app.domain.entities.invoice import Invoice
            invoice = Invoice(
                user_id=0,  # will set below
                stripe_invoice_id=stripe_invoice["id"],
            )
        invoice.update_from_stripe(stripe_invoice)

        # Find user from customer
        customer_id = stripe_invoice["customer"]
        user = await self.user_repo.get_by_stripe_customer_id(customer_id)
        if user:
            invoice.user_id = user.id
        await self.invoice_repo.save(invoice)

        # If invoice is paid, update user's subscription if needed (already handled by subscription event)

    async def _handle_refund_event(self, event: Dict[str, Any]) -> None:
        # Handle refunds - could update affiliate commissions or other logic
        pass
