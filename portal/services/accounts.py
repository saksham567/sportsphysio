import secrets
import string

from accounts.models import PatientProfile, User


def generate_temporary_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def get_or_create_patient_from_contact(*, email, name, phone=""):
    email = email.strip().lower()
    user = User.objects.filter(email__iexact=email).first()
    created = False
    temp_password = None

    if user:
        if phone and not user.phone:
            user.phone = phone
            user.whatsapp = phone
            user.save(update_fields=["phone", "whatsapp"])
        return user, created, temp_password

    name = name.strip() or email.split("@")[0]
    parts = name.split(None, 1)
    temp_password = generate_temporary_password()

    user = User.objects.create_user(
        username=email,
        email=email,
        password=temp_password,
        first_name=parts[0],
        last_name=parts[1] if len(parts) > 1 else "",
        phone=phone,
        whatsapp=phone,
        role=User.Role.PATIENT,
        is_active=True,
    )
    PatientProfile.objects.get_or_create(user=user)
    created = True
    return user, created, temp_password


def link_guest_records_to_user(user):
    """Attach orphan bookings/payments that match guest email."""
    from portal.models import Booking, Payment

    email = user.email.lower()
    Booking.objects.filter(guest_email__iexact=email, patient__isnull=True).update(
        patient=user
    )
    Payment.objects.filter(guest_email__iexact=email, patient__isnull=True).update(
        patient=user
    )
