import hashlib
import hmac
import logging
from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from accounts.models import User
from portal.models import Booking, CalendlyWebhookLog, ServicePlan
from portal.services.accounts import link_guest_records_to_user
from portal.services.notifications import notify_booking_confirmed_whatsapp

logger = logging.getLogger(__name__)


def verify_calendly_signature(raw_body: bytes, signature_header: str, signing_key: str) -> bool:
    if not signing_key or not signature_header:
        return False
    try:
        parts = dict(p.split("=") for p in signature_header.split(","))
        timestamp = parts.get("t", "")
        signature = parts.get("v1", "")
        message = f"{timestamp}.{raw_body.decode('utf-8')}"
        expected = hmac.new(
            signing_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception:
        logger.exception("Calendly signature verification failed")
        return False


def process_calendly_event(event_type: str, payload: dict) -> Booking | None:
    log = CalendlyWebhookLog.objects.create(
        event_type=event_type,
        payload=payload,
    )

    try:
        if event_type == "invitee.created":
            booking = _handle_invitee_created(payload)
        elif event_type == "invitee.canceled":
            booking = _handle_invitee_canceled(payload)
        else:
            log.processed = True
            log.save(update_fields=["processed"])
            return None

        log.invitee_uri = payload.get("uri", "")
        log.processed = True
        log.save(update_fields=["invitee_uri", "processed"])
        return booking
    except Exception as exc:
        log.error_message = str(exc)
        log.save(update_fields=["error_message"])
        logger.exception("Calendly webhook processing error")
        raise


def _parse_scheduled_time(payload: dict):
    scheduled_event = payload.get("scheduled_event") or {}
    start = scheduled_event.get("start_time") or payload.get("event_start_time")
    if not start:
        return None
    dt = parse_datetime(start)
    if dt and timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


def _handle_invitee_created(payload: dict) -> Booking:
    invitee_uri = payload.get("uri", "")
    email = (payload.get("email") or "").strip().lower()
    name = payload.get("name") or payload.get("first_name", "") or ""
    phone = ""
    questions = payload.get("questions_and_answers") or []
    for qa in questions:
        q = (qa.get("question") or "").lower()
        if "phone" in q or "whatsapp" in q:
            phone = qa.get("answer") or ""

    scheduled_at = _parse_scheduled_time(payload)
    event_uri = (payload.get("scheduled_event") or {}).get("uri", "")
    event_name = (payload.get("scheduled_event") or {}).get("name") or ""

    patient = User.objects.filter(email__iexact=email).first()

    if "rehab" in event_name.lower() or "monthly" in event_name.lower():
        plan = ServicePlan.objects.filter(slug="monthly-rehab").first()
        plan_label = plan.name if plan else "Monthly Rehab Program — ₹3,000/month"
    else:
        plan = ServicePlan.objects.filter(slug="video-consultation").first()
        plan_label = plan.name if plan else "Video Consultation — ₹500 (30 min)"

    booking, created = Booking.objects.update_or_create(
        calendly_invitee_uri=invitee_uri,
        defaults={
            "patient": patient,
            "guest_name": name,
            "guest_email": email,
            "guest_phone": phone,
            "plan": plan,
            "plan_label": plan_label,
            "scheduled_at": scheduled_at,
            "status": Booking.Status.CONFIRMED,
            "calendly_event_uri": event_uri,
            "notes": f"Auto-created from Calendly on {timezone.now():%d %b %Y}",
        },
    )

    when = ""
    if booking.scheduled_at:
        when = booking.scheduled_at.strftime("%d %b %Y at %I:%M %p")

    if phone or email:
        notify_booking_confirmed_whatsapp(
            name=name,
            phone=phone,
            email=email,
            plan_label=booking.plan_label,
            scheduled_when=when,
            payment_pending=True,
            patient=patient if patient and patient.is_active else None,
        )

    if patient and patient.is_active:
        link_guest_records_to_user(patient)

    return booking


def _handle_invitee_canceled(payload: dict) -> Booking | None:
    invitee_uri = payload.get("uri", "")
    booking = Booking.objects.filter(calendly_invitee_uri=invitee_uri).first()
    if booking:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
    return booking
