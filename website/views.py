from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from portal.forms import RazorpayCheckoutForm
from portal.models import Payment, ServicePlan
from portal.services.razorpay import complete_razorpay_payment, create_order

from .checkout import (
    calendly_url_for_plan,
    clear_checkout_session,
    get_plan,
    set_checkout_session,
)
from .content import PLANS

VIDEO_CONSULT_SLUG = "video-consultation"


def home(request):
    from .content import HERO_STATS, SERVICES

    return render(
        request,
        "website/home.html",
        {"hero_stats": HERO_STATS, "services": SERVICES[:4]},
    )


def services(request):
    from .content import SERVICES

    return render(request, "website/services.html", {"services": SERVICES})


def plans(request):
    return render(request, "website/plans.html", {"plans": PLANS, "flow_step": 1})


def book_consultation(request):
    """Home CTA: start 1-on-1 video consultation checkout (book slot, then pay)."""
    return redirect(reverse("website:book") + f"?plan={VIDEO_CONSULT_SLUG}")


def book(request):
    plan_slug = request.GET.get("plan", "")
    plan_data = get_plan(plan_slug)

    if not plan_data:
        messages.info(request, "Please choose a plan first.")
        return redirect("website:plans")

    set_checkout_session(request, plan_slug)

    calendly_url = calendly_url_for_plan(plan_slug)
    payment_redirect = reverse("website:payment") + f"?plan={plan_slug}&booked=1"

    return render(
        request,
        "website/book.html",
        {
            "plan": plan_data,
            "calendly_url": calendly_url,
            "payment_redirect_url": payment_redirect,
            "flow_step": 2,
        },
    )


def payment(request):
    plan_slug = request.GET.get("plan", "") or request.session.get("checkout_plan", "")
    plan_data = get_plan(plan_slug)
    renew = request.GET.get("renew") == "1"
    booked = request.GET.get("booked") == "1" or request.session.get("slot_booked") or renew

    if request.user.is_authenticated and renew:
        return redirect(reverse("portal:payments") + (f"?plan={plan_slug}" if plan_slug else ""))

    if not plan_data:
        messages.info(request, "Please select a plan to continue.")
        return redirect("website:plans")

    if not booked:
        messages.info(request, "Please book your slot first, then complete payment.")
        return redirect(reverse("website:book") + f"?plan={plan_slug}")

    request.session["slot_booked"] = True
    request.session["checkout_plan"] = plan_slug
    request.session.modified = True

    set_checkout_session(request, plan_slug)
    service_plan = ServicePlan.objects.filter(slug=plan_slug).first()

    initial = {}
    if request.user.is_authenticated:
        initial = {
            "guest_name": request.user.get_full_name(),
            "guest_email": request.user.email,
            "guest_phone": request.user.phone or request.user.whatsapp,
        }

    form = RazorpayCheckoutForm(initial=initial)

    return render(
        request,
        "website/payment.html",
        {
            "form": form,
            "plan": plan_data,
            "flow_step": 3,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_enabled": bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET),
        },
    )


@require_POST
def razorpay_create_order(request):
    plan_slug = request.POST.get("plan") or request.session.get("checkout_plan")
    plan_data = get_plan(plan_slug)

    if not plan_data:
        return JsonResponse({"error": "Invalid plan"}, status=400)

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse({"error": "Razorpay is not configured"}, status=503)

    form = RazorpayCheckoutForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors}, status=400)

    service_plan = ServicePlan.objects.filter(slug=plan_slug).first()
    receipt = f"sp-{uuid.uuid4().hex[:12]}"

    order = create_order(
        amount_inr=plan_data["price"],
        receipt=receipt,
        notes={
            "plan": plan_slug,
            "email": form.cleaned_data["guest_email"],
        },
    )

    payment = Payment.objects.create(
        guest_name=form.cleaned_data["guest_name"],
        guest_email=form.cleaned_data["guest_email"],
        guest_phone=form.cleaned_data["guest_phone"],
        plan=service_plan,
        plan_label=plan_data["plan_label"],
        amount_inr=plan_data["price"],
        razorpay_order_id=order["id"],
        status=Payment.Status.PENDING,
        patient=request.user if request.user.is_authenticated else None,
    )

    request.session["pending_payment_id"] = payment.id
    request.session.modified = True

    return JsonResponse(
        {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": settings.RAZORPAY_KEY_ID,
            "payment_id": payment.id,
            "prefill": {
                "name": form.cleaned_data["guest_name"],
                "email": form.cleaned_data["guest_email"],
                "contact": form.cleaned_data["guest_phone"],
            },
        }
    )


@require_POST
def razorpay_verify(request):
    order_id = request.POST.get("razorpay_order_id")
    payment_id_razorpay = request.POST.get("razorpay_payment_id")
    signature = request.POST.get("razorpay_signature")

    if not all([order_id, payment_id_razorpay, signature]):
        messages.error(request, "Payment verification failed. Please contact support.")
        return redirect("website:plans")

    payment = get_object_or_404(Payment, razorpay_order_id=order_id)

    try:
        complete_razorpay_payment(
            payment=payment,
            razorpay_payment_id=payment_id_razorpay,
            razorpay_signature=signature,
        )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("website:payment") + f"?plan={request.session.get('checkout_plan', '')}&booked=1"

    clear_checkout_session(request)
    request.session.pop("pending_payment_id", None)
    return redirect("website:payment_success")


def payment_success(request):
    return render(request, "website/payment_submitted.html", {"razorpay": True})


def payment_submitted(request):
    return redirect("website:payment_success")


def reviews(request):
    from .content import REVIEWS

    return render(request, "website/reviews.html", {"reviews": REVIEWS})
