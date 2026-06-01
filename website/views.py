from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from portal.forms import GuestPaymentForm
from portal.models import ServicePlan
from portal.services.notifications import notify_staff_payment_submitted

from .checkout import (
    calendly_url_for_plan,
    clear_checkout_session,
    get_checkout_plan,
    get_plan,
    set_checkout_session,
)
from .content import PLANS


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
    booked = request.GET.get("booked") == "1" or request.session.get("slot_booked")

    # Logged-in users renewing go to portal
    if request.user.is_authenticated and renew:
        url = reverse("portal:payments")
        if plan_slug:
            url += f"?plan={plan_slug}"
        return redirect(url)

    if not plan_data:
        messages.info(request, "Please select a plan to continue.")
        return redirect("website:plans")

    if not booked:
        messages.info(request, "Please book your slot first, then complete payment.")
        return redirect(reverse("website:book") + f"?plan={plan_slug}")

    if booked:
        request.session["slot_booked"] = True
        request.session["checkout_plan"] = plan_slug
        request.session.modified = True

    set_checkout_session(request, plan_slug)
    service_plan = ServicePlan.objects.filter(slug=plan_slug).first()

    if request.method == "POST":
        form = GuestPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment_obj = form.save(commit=False)
            payment_obj.plan = service_plan
            payment_obj.save()
            notify_staff_payment_submitted(payment=payment_obj)
            clear_checkout_session(request)
            return redirect("website:payment_submitted")
    else:
        form = GuestPaymentForm(
            initial={
                "plan_label": plan_data["plan_label"],
                "amount_inr": plan_data["price"],
            }
        )

    return render(
        request,
        "website/payment.html",
        {
            "form": form,
            "plan": plan_data,
            "flow_step": 3,
        },
    )


def payment_submitted(request):
    return render(request, "website/payment_submitted.html")


def reviews(request):
    from .content import REVIEWS

    return render(request, "website/reviews.html", {"reviews": REVIEWS})
