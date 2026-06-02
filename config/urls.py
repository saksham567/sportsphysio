from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from portal.webhooks import calendly_webhook, razorpay_webhook

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
    path("accounts/", include("accounts.urls")),
    path("portal/", include("portal.urls")),
    path("staff/", include("staff.urls")),
    path("webhooks/calendly/", calendly_webhook, name="calendly_webhook"),
    path("webhooks/razorpay/", razorpay_webhook, name="razorpay_webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Dr. Aahana Gupta — Admin"
admin.site.site_title = "Sports Physio Admin"
admin.site.index_title = "Practice Management"
