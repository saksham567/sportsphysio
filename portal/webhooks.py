import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from portal.services.calendly import process_calendly_event, verify_calendly_signature

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def calendly_webhook(request):
    signing_key = getattr(settings, "CALENDLY_WEBHOOK_SIGNING_KEY", "")
    signature = request.headers.get("Calendly-Webhook-Signature", "")

    if signing_key and not verify_calendly_signature(
        request.body, signature, signing_key
    ):
        return HttpResponseForbidden("Invalid signature")
    elif not signing_key and not settings.DEBUG:
        return HttpResponseForbidden("Webhook signing key not configured")

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    event_type = body.get("event", "")
    payload = body.get("payload", {})

    try:
        process_calendly_event(event_type, payload)
    except Exception:
        return JsonResponse({"error": "Processing failed"}, status=500)

    return JsonResponse({"status": "ok"})
