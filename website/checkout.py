from urllib.parse import urlencode

from django.conf import settings

from .content import PLANS


def get_plan(slug):
    return next((p for p in PLANS if p["slug"] == slug), None)


def calendly_url_for_plan(plan_slug, redirect_to_payment=True):
    """Build Calendly embed URL for a plan, with post-booking redirect to payment."""
    plan = get_plan(plan_slug)
    if not plan:
        return settings.CALENDLY_URL

    if plan_slug == "monthly-rehab":
        base = settings.CALENDLY_REHAB_URL
    else:
        base = settings.CALENDLY_URL

    if not redirect_to_payment:
        return base

    payment_path = f"/payment/?plan={plan_slug}&booked=1"
    redirect_url = settings.SITE_URL.rstrip("/") + payment_path

    separator = "&" if "?" in base else "?"
    return f"{base}{separator}{urlencode({'redirect_url': redirect_url})}"


def set_checkout_session(request, plan_slug):
    request.session["checkout_plan"] = plan_slug
    request.session.modified = True


def get_checkout_plan(request):
    slug = request.GET.get("plan") or request.session.get("checkout_plan")
    return get_plan(slug), slug


def clear_checkout_session(request):
    request.session.pop("checkout_plan", None)
    request.session.pop("slot_booked", None)
    request.session.modified = True
