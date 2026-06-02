import hashlib
import hmac
import json
import logging

import razorpay
from django.conf import settings
from django.utils import timezone

from portal.models import Payment
from portal.services.payments import verify_payment

logger = logging.getLogger(__name__)


def get_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def create_order(*, amount_inr: int, receipt: str, notes: dict | None = None):
    """Create Razorpay order; amount_inr is in rupees."""
    client = get_client()
    order = client.order.create(
        {
            "amount": amount_inr * 100,
            "currency": "INR",
            "receipt": receipt[:40],
            "notes": notes or {},
        }
    )
    return order


def verify_checkout_signature(*, order_id: str, payment_id: str, signature: str) -> bool:
    try:
        get_client().utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    except Exception:
        logger.exception("Razorpay signature verification failed")
        return False


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    if not secret or not signature:
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def complete_razorpay_payment(
    *,
    payment: Payment,
    razorpay_payment_id: str,
    razorpay_signature: str = "",
    verified_by=None,
):
    """Mark payment verified after Razorpay confirmation."""
    if payment.status == Payment.Status.VERIFIED:
        return payment

    if razorpay_signature and not verify_checkout_signature(
        order_id=payment.razorpay_order_id,
        payment_id=razorpay_payment_id,
        signature=razorpay_signature,
    ):
        raise ValueError("Invalid Razorpay payment signature")

    payment.razorpay_payment_id = razorpay_payment_id
    payment.upi_transaction_id = razorpay_payment_id
    payment.save(update_fields=["razorpay_payment_id", "upi_transaction_id", "updated_at"])

    return verify_payment(payment=payment, verified_by=verified_by)


def process_webhook_event(payload: dict):
    event = payload.get("event", "")
    if event != "payment.captured":
        return None

    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = entity.get("order_id")
    payment_id = entity.get("id")

    if not order_id:
        return None

    payment = Payment.objects.filter(razorpay_order_id=order_id).first()
    if not payment or payment.status == Payment.Status.VERIFIED:
        return payment

    return complete_razorpay_payment(
        payment=payment,
        razorpay_payment_id=payment_id,
        verified_by=None,
    )
