import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from portal.models import NotificationLog

logger = logging.getLogger(__name__)


def _log_notification(*, patient, email, phone, channel, subject, body, success, error=""):
    NotificationLog.objects.create(
        patient=patient,
        recipient_email=email or "",
        recipient_phone=phone or "",
        channel=channel,
        subject=subject,
        body=body,
        success=success,
        error_message=error,
    )


def send_email_notification(*, to_email, subject, body, patient=None):
    if not to_email:
        return False
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        _log_notification(
            patient=patient,
            email=to_email,
            phone="",
            channel=NotificationLog.Channel.EMAIL,
            subject=subject,
            body=body,
            success=True,
        )
        return True
    except Exception as exc:
        logger.exception("Email send failed to %s", to_email)
        _log_notification(
            patient=patient,
            email=to_email,
            phone="",
            channel=NotificationLog.Channel.EMAIL,
            subject=subject,
            body=body,
            success=False,
            error=str(exc),
        )
        return False


def send_whatsapp_notification(*, phone, message, patient=None):
    """Send WhatsApp via Twilio when configured; always log the attempt."""
    if not phone:
        return False

    phone = phone.strip().lstrip("+")
    if not phone.startswith("91") and len(phone) == 10:
        phone = f"91{phone}"

    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_number = getattr(settings, "TWILIO_WHATSAPP_FROM", "")

    if account_sid and auth_token and from_number:
        try:
            from twilio.rest import Client

            client = Client(account_sid, auth_token)
            client.messages.create(
                from_=from_number,
                to=f"whatsapp:+{phone}",
                body=message,
            )
            _log_notification(
                patient=patient,
                email="",
                phone=phone,
                channel=NotificationLog.Channel.WHATSAPP,
                subject="WhatsApp",
                body=message,
                success=True,
            )
            return True
        except Exception as exc:
            logger.exception("Twilio WhatsApp failed for %s", phone)
            _log_notification(
                patient=patient,
                email="",
                phone=phone,
                channel=NotificationLog.Channel.WHATSAPP,
                subject="WhatsApp",
                body=message,
                success=False,
                error=str(exc),
            )
            return False

    # Twilio not configured — log for manual follow-up via wa.me link
    wa_link = f"https://wa.me/{phone}?text={message[:200].replace(' ', '%20')}"
    _log_notification(
        patient=patient,
        email="",
        phone=phone,
        channel=NotificationLog.Channel.WHATSAPP,
        subject="WhatsApp (manual — Twilio not configured)",
        body=f"{message}\n\nOpen in WhatsApp: {wa_link}",
        success=False,
        error="Twilio not configured; use wa.me link in log body",
    )
    return False


def notify_patient(*, patient, subject, email_body, whatsapp_body=None):
    """Send both email and WhatsApp to a patient."""
    email_ok = send_email_notification(
        to_email=patient.email,
        subject=subject,
        body=email_body,
        patient=patient,
    )
    phone = patient.whatsapp or patient.phone
    wa_ok = False
    if whatsapp_body and phone:
        wa_ok = send_whatsapp_notification(
            phone=phone,
            message=whatsapp_body,
            patient=patient,
        )
    return email_ok or wa_ok


def notify_payment_verified(*, patient, temporary_password=None):
    context = {
        "patient_name": patient.first_name or patient.display_name,
        "login_url": settings.SITE_URL.rstrip("/") + "/accounts/login/",
        "email": patient.email,
        "temporary_password": temporary_password,
    }
    subject = "Payment confirmed — your patient portal is ready"
    body = render_to_string("notifications/payment_verified_email.txt", context)
    wa_body = render_to_string("notifications/payment_verified_whatsapp.txt", context)
    return notify_patient(
        patient=patient,
        subject=subject,
        email_body=body,
        whatsapp_body=wa_body,
    )


def notify_new_progress_week(*, patient, program, entry):
    context = {
        "patient_name": patient.first_name or patient.display_name,
        "program_title": program.title,
        "week_number": entry.week_number,
        "week_title": entry.title,
        "summary": entry.summary,
        "portal_url": settings.SITE_URL.rstrip("/") + "/portal/progress/",
    }
    subject = f"Week {entry.week_number} of your rehab program is ready"
    body = render_to_string("notifications/new_week_email.txt", context)
    wa_body = render_to_string("notifications/new_week_whatsapp.txt", context)
    return notify_patient(
        patient=patient,
        subject=subject,
        email_body=body,
        whatsapp_body=wa_body,
    )


def notify_booking_confirmed(*, patient, booking):
    when = booking.scheduled_at.strftime("%d %b %Y at %I:%M %p") if booking.scheduled_at else ""
    return notify_booking_confirmed_whatsapp(
        name=patient.first_name or patient.display_name,
        phone=patient.whatsapp or patient.phone,
        email=patient.email,
        plan_label=booking.plan_label or "Session",
        scheduled_when=when,
        payment_pending=True,
        patient=patient,
    )


def notify_booking_confirmed_whatsapp(
    *,
    name: str,
    phone: str,
    email: str = "",
    plan_label: str,
    scheduled_when: str = "",
    payment_pending: bool = True,
    patient=None,
):
    """WhatsApp + email when a Calendly slot is booked (guest or patient)."""
    payment_url = settings.SITE_URL.rstrip("/") + "/payment/"
    slug = _plan_slug_from_label(plan_label)
    payment_url += f"?plan={slug}&booked=1"

    context = {
        "name": name.split()[0] if name else "there",
        "plan_label": plan_label,
        "scheduled_when": scheduled_when,
        "payment_pending": payment_pending,
        "payment_url": payment_url,
    }
    wa_body = render_to_string("notifications/booking_confirmed_whatsapp.txt", context)

    if phone:
        send_whatsapp_notification(phone=phone, message=wa_body, patient=patient)

    if email:
        subject = "Your session with Dr. Aahana is booked"
        body = (
            f"Hi {name},\n\n"
            f"Your appointment is booked"
            f"{f' for {scheduled_when}' if scheduled_when else ''}.\n\n"
            f"Plan: {plan_label}\n\n"
            f"Complete payment: {payment_url}\n\n"
            f"— Dr. Aahana Gupta (PT)"
        )
        send_email_notification(to_email=email, subject=subject, body=body, patient=patient)

    return True


def notify_payment_confirmed_whatsapp(*, payment, patient, temporary_password=None):
    """WhatsApp when Razorpay payment succeeds."""
    booking = (
        Booking.objects.filter(guest_email__iexact=payment.contact_email)
        .order_by("-created_at")
        .first()
    )
    if not booking and payment.patient_id:
        booking = Booking.objects.filter(patient=payment.patient).order_by("-created_at").first()

    scheduled_when = ""
    if booking and booking.scheduled_at:
        scheduled_when = booking.scheduled_at.strftime("%d %b %Y at %I:%M %p")

    context = {
        "name": (payment.contact_name or "there").split()[0],
        "amount_inr": payment.amount_inr,
        "plan_label": payment.plan_label,
        "scheduled_when": scheduled_when,
        "portal_url": settings.SITE_URL.rstrip("/") + "/accounts/login/",
        "email": payment.contact_email,
        "temp_password": temporary_password or "",
    }
    wa_body = render_to_string("notifications/payment_confirmed_whatsapp.txt", context)
    phone = payment.contact_phone or (patient.whatsapp if patient else "") or (patient.phone if patient else "")

    if phone:
        send_whatsapp_notification(phone=phone, message=wa_body, patient=patient)

    if payment.contact_email:
        subject = f"Payment confirmed — {payment.plan_label}"
        send_email_notification(
            to_email=payment.contact_email,
            subject=subject,
            body=wa_body,
            patient=patient,
        )


def _plan_slug_from_label(label: str) -> str:
    lower = label.lower()
    if "monthly" in lower or "rehab" in lower:
        return "monthly-rehab"
    return "video-consultation"


def notify_staff_payment_submitted(*, payment):
    """Alert Dr. Aahana when a patient submits payment proof."""
    staff_email = settings.CONTACT_EMAIL
    subject = f"New payment to verify — {payment.contact_name} (₹{payment.amount_inr})"
    body = (
        f"A new payment proof has been submitted and needs your verification.\n\n"
        f"Patient: {payment.contact_name}\n"
        f"Email: {payment.contact_email}\n"
        f"Phone: {payment.contact_phone or '—'}\n"
        f"Plan: {payment.plan_label}\n"
        f"Amount: ₹{payment.amount_inr}\n"
        f"UPI ref: {payment.upi_transaction_id or '—'}\n\n"
        f"Review in staff dashboard:\n"
        f"{settings.SITE_URL.rstrip('/')}/staff/payments/\n\n"
        f"After verifying, confirm the patient's slot and send portal login details."
    )
    return send_email_notification(to_email=staff_email, subject=subject, body=body)
