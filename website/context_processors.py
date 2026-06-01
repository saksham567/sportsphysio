from django.conf import settings


def site_settings(request):
    return {
        "UPI_ID": settings.UPI_ID,
        "CALENDLY_URL": settings.CALENDLY_URL,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "INSTAGRAM_HANDLE": settings.INSTAGRAM_HANDLE,
        "INSTAGRAM_URL": settings.INSTAGRAM_URL,
    }
