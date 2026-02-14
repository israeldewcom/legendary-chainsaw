import stripe
from typing import Optional, Dict, Any
from app.config import settings
import structlog

logger = structlog.get_logger()


class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY.get_secret_value() if settings.STRIPE_SECRET_KEY else None
        stripe.api_version = settings.STRIPE_API_VERSION

    async def create_customer(self, email: str, name: Optional[str] = None) -> str:
        customer = stripe.Customer.create(
            email=email,
            name=name,
        )
        logger.info("Stripe customer created", customer_id=customer.id, email=email)
        return customer.id

    async def create_subscription(self, customer_id: str, price_id: str, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "customer": customer_id,
            "items": [{"price": price_id}],
            "expand": ["latest_invoice.payment_intent"],
        }
        if coupon_code:
            params["coupon"] = coupon_code
        subscription = stripe.Subscription.create(**params)
        return subscription

    async def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> None:
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=at_period_end,
        )
        logger.info("Stripe subscription cancelled", subscription_id=subscription_id, at_period_end=at_period_end)

    async def update_payment_method(self, customer_id: str, payment_method_id: str) -> None:
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )
        logger.info("Stripe payment method updated", customer_id=customer_id)

    async def create_checkout_session(self, customer_id: str, price_id: str, success_url: str, cancel_url: str) -> str:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url

    async def create_connect_account(self, email: str, country: str = "US") -> str:
        account = stripe.Account.create(
            type="express",
            country=country,
            email=email,
            capabilities={
                "transfers": {"requested": True},
            },
        )
        logger.info("Stripe Connect account created", account_id=account.id, email=email)
        return account.id

    async def create_connect_login_link(self, account_id: str) -> str:
        link = stripe.Account.create_login_link(account_id)
        return link.url

    async def create_transfer(self, amount: int, currency: str, destination: str, metadata: Dict = None) -> Dict:
        transfer = stripe.Transfer.create(
            amount=amount,
            currency=currency,
            destination=destination,
            metadata=metadata or {},
        )
        logger.info("Stripe transfer created", transfer_id=transfer.id, amount=amount, destination=destination)
        return transfer
