from django.utils import timezone

from portal.models import Booking, ConsultationHistory, Payment, ServicePlan
from portal.services.accounts import get_or_create_patient_from_contact, link_guest_records_to_user
from portal.services.notifications import notify_payment_confirmed_whatsapp
from portal.services.rehab import create_rehab_program_for_payment


def verify_payment(*, payment: Payment, verified_by=None):
    if payment.status == Payment.Status.VERIFIED:
        return payment

    email = payment.contact_email
    if not email:
        raise ValueError("Payment has no email — cannot create patient login.")

    name = payment.contact_name
    phone = payment.contact_phone or ""

    user = payment.patient
    temp_password = None
    account_created = False

    if not user:
        user, account_created, temp_password = get_or_create_patient_from_contact(
            email=email,
            name=name,
            phone=phone,
        )
        payment.patient = user
    else:
        link_guest_records_to_user(user)

    payment.status = Payment.Status.VERIFIED
    payment.verified_at = timezone.now()
    payment.verified_by = verified_by
    payment.save()

    link_guest_records_to_user(user)

    if not payment.login_credentials_sent:
        payment.login_credentials_sent = True
        payment.save(update_fields=["login_credentials_sent", "updated_at"])

    plan = payment.plan
    if not plan:
        if "monthly" in payment.plan_label.lower() or "rehab" in payment.plan_label.lower():
            plan = ServicePlan.objects.filter(slug="monthly-rehab").first()
        else:
            plan = ServicePlan.objects.filter(slug="video-consultation").first()

    if plan and plan.is_recurring:
        create_rehab_program_for_payment(payment=payment, patient=user)
    elif plan:
        ConsultationHistory.objects.get_or_create(
            patient=user,
            session_date=payment.verified_at,
            defaults={
                "session_type": ConsultationHistory.SessionType.VIDEO,
                "chief_complaint": payment.plan_label,
                "assessment_summary": "Consultation payment confirmed via Razorpay.",
            },
        )

    notify_payment_confirmed_whatsapp(
        payment=payment,
        patient=user,
        temporary_password=temp_password if account_created else None,
    )

    return payment


def reject_payment(*, payment: Payment, verified_by=None, reason=""):
    payment.status = Payment.Status.REJECTED
    payment.verified_by = verified_by
    if reason:
        payment.admin_notes = reason
    payment.save()
    return payment
