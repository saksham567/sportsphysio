from django.conf import settings
from urllib.parse import quote


def site_settings(request):
    wa_number = getattr(settings, "WHATSAPP_NUMBER", "") or ""
    wa_message = quote(getattr(settings, "WHATSAPP_PREFILL_MESSAGE", ""))
    wa_url = ""
    if wa_number:
        wa_url = f"https://wa.me/{wa_number}?text={wa_message}"

    return {
        "CALENDLY_URL": settings.CALENDLY_URL,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "INSTAGRAM_HANDLE": settings.INSTAGRAM_HANDLE,
        "INSTAGRAM_URL": settings.INSTAGRAM_URL,
        "WHATSAPP_URL": wa_url,
        "WHATSAPP_NUMBER": wa_number,
    }
