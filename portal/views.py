from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from website.content import PLANS

from .forms import ProgressNoteForm
from .models import Booking, ConsultationHistory, Payment, ProgressEntry, RehabProgram, ServicePlan


def _patient_required(view_func):
    decorated = login_required(view_func)
    decorated.__patient_required__ = True
    return decorated


@_patient_required
def dashboard(request):
    user = request.user
    return render(
        request,
        "portal/dashboard.html",
        {
            "active_programs": RehabProgram.objects.filter(
                patient=user, status=RehabProgram.Status.ACTIVE
            )[:3],
            "recent_payments": Payment.objects.filter(patient=user)[:5],
            "upcoming_bookings": Booking.objects.filter(
                patient=user,
                status__in=[Booking.Status.REQUESTED, Booking.Status.CONFIRMED],
            )[:5],
            "recent_consultations": ConsultationHistory.objects.filter(patient=user)[:3],
        },
    )


@_patient_required
def payments(request):
    user = request.user
    plan_slug = request.GET.get("plan", "")
    if plan_slug:
        return redirect(
            reverse("website:payment") + f"?plan={plan_slug}&booked=1&renew=1"
        )
    return render(
        request,
        "portal/payments.html",
        {
            "payments_list": Payment.objects.filter(patient=user),
        },
    )


@_patient_required
def progress(request):
    user = request.user
    programs = RehabProgram.objects.filter(patient=user).prefetch_related("progress_entries")
    return render(request, "portal/progress.html", {"programs": programs})


@_patient_required
def progress_update(request, entry_id):
    entry = get_object_or_404(
        ProgressEntry,
        pk=entry_id,
        program__patient=request.user,
    )
    if request.method == "POST":
        form = ProgressNoteForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("portal:progress")
    else:
        form = ProgressNoteForm(instance=entry)
    return render(request, "portal/progress_update.html", {"form": form, "entry": entry})


@_patient_required
def history(request):
    user = request.user
    return render(
        request,
        "portal/history.html",
        {
            "consultations": ConsultationHistory.objects.filter(patient=user),
            "bookings": Booking.objects.filter(patient=user),
        },
    )


@_patient_required
def book_plan(request):
    """Record intent to book a plan; redirects to Calendly booking page."""
    plan_slug = request.GET.get("plan", "")
    plan_data = next((p for p in PLANS if p["slug"] == plan_slug), None)
    service_plan = ServicePlan.objects.filter(slug=plan_slug).first() if plan_slug else None

    if plan_data:
        Booking.objects.create(
            patient=request.user,
            plan=service_plan,
            plan_label=plan_data["plan_label"],
            status=Booking.Status.REQUESTED,
        )
        return redirect(f"{reverse('website:book')}?plan={plan_slug}")

    return redirect("website:book")
