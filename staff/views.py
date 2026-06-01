from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import PatientProfile, User
from portal.models import Booking, ConsultationHistory, NotificationLog, Payment, ProgressEntry, RehabProgram
from portal.services import advance_program_weeks, verify_payment
from portal.services.payments import reject_payment
from portal.services.rehab import create_progress_week

from .decorators import staff_required
from .forms import ConsultationStaffForm, PaymentActionForm, ProgressEntryStaffForm, RehabProgramForm


@staff_required
def dashboard(request):
    return render(
        request,
        "staff/dashboard.html",
        {
            "pending_payments": Payment.objects.filter(status=Payment.Status.PENDING)[:10],
            "pending_count": Payment.objects.filter(status=Payment.Status.PENDING).count(),
            "upcoming_bookings": Booking.objects.filter(
                status=Booking.Status.CONFIRMED,
            ).order_by("scheduled_at")[:10],
            "active_programs": RehabProgram.objects.filter(
                status=RehabProgram.Status.ACTIVE
            )[:8],
            "patient_count": User.objects.filter(role=User.Role.PATIENT).count(),
        },
    )


@staff_required
def payments(request):
    status = request.GET.get("status", "pending")
    qs = Payment.objects.all()
    if status != "all":
        qs = qs.filter(status=status)
    return render(
        request,
        "staff/payments.html",
        {"payments": qs[:50], "current_status": status},
    )


@staff_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    form = PaymentActionForm()

    if request.method == "POST":
        action = request.POST.get("action")
        form = PaymentActionForm(request.POST)
        if action == "verify":
            try:
                verify_payment(payment=payment, verified_by=request.user)
                if form.is_valid() and form.cleaned_data.get("admin_notes"):
                    payment.admin_notes = form.cleaned_data["admin_notes"]
                    payment.save(update_fields=["admin_notes", "updated_at"])
                messages.success(
                    request,
                    f"Payment verified. Login details sent to {payment.contact_email}.",
                )
            except ValueError as exc:
                messages.error(request, str(exc))
            return redirect("staff:payment_detail", payment_id=payment.id)
        if action == "reject" and form.is_valid():
            reject_payment(
                payment=payment,
                verified_by=request.user,
                reason=form.cleaned_data.get("admin_notes", ""),
            )
            messages.warning(request, "Payment marked as rejected.")
            return redirect("staff:payments")

    return render(
        request,
        "staff/payment_detail.html",
        {"payment": payment, "form": form},
    )


@staff_required
def bookings(request):
    status = request.GET.get("status", "confirmed")
    qs = Booking.objects.all()
    if status != "all":
        qs = qs.filter(status=status)
    return render(
        request,
        "staff/bookings.html",
        {"bookings": qs[:50], "current_status": status},
    )


@staff_required
def patients(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.filter(role=User.Role.PATIENT)
    if q:
        qs = qs.filter(
            Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(phone__icontains=q)
        )
    return render(request, "staff/patients.html", {"patients": qs[:50], "query": q})


@staff_required
def patient_detail(request, user_id):
    patient = get_object_or_404(User, pk=user_id, role=User.Role.PATIENT)
    profile, _ = PatientProfile.objects.get_or_create(user=patient)
    return render(
        request,
        "staff/patient_detail.html",
        {
            "patient": patient,
            "profile": profile,
            "payments": Payment.objects.filter(patient=patient)[:10],
            "bookings": Booking.objects.filter(patient=patient)[:10],
            "programs": RehabProgram.objects.filter(patient=patient),
            "consultations": ConsultationHistory.objects.filter(patient=patient)[:10],
        },
    )


@staff_required
def programs(request):
    return render(
        request,
        "staff/programs.html",
        {"programs": RehabProgram.objects.all()[:50]},
    )


@staff_required
def program_detail(request, program_id):
    program = get_object_or_404(RehabProgram, pk=program_id)

    if request.method == "POST":
        if "add_week" in request.POST:
            next_week = program.current_week_number + 1
            create_progress_week(
                program=program,
                week_number=next_week,
                title=f"Week {next_week} — Progressive loading",
                summary=request.POST.get(
                    "week_summary",
                    f"Week {next_week} exercises and guidance from Dr. Aahana.",
                ),
                exercises_total=int(request.POST.get("exercises_total", 5)),
                notify=True,
            )
            messages.success(request, f"Week {next_week} added and patient notified.")
            return redirect("staff:program_detail", program_id=program.id)

        form = ProgressEntryStaffForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.program = program
            is_new = entry.pk is None
            entry.save()
            if is_new and not entry.notified_patient:
                from portal.services.notifications import notify_new_progress_week

                notify_new_progress_week(
                    patient=program.patient,
                    program=program,
                    entry=entry,
                )
                entry.notified_patient = True
                entry.save(update_fields=["notified_patient"])
            messages.success(request, "Progress entry saved.")
            return redirect("staff:program_detail", program_id=program.id)
    else:
        form = ProgressEntryStaffForm(
            initial={
                "week_number": program.current_week_number + 1,
                "recorded_at": timezone.localdate(),
            }
        )

    return render(
        request,
        "staff/program_detail.html",
        {"program": program, "form": form, "entries": program.progress_entries.all()},
    )


@staff_required
def program_create(request, user_id):
    patient = get_object_or_404(User, pk=user_id, role=User.Role.PATIENT)
    if request.method == "POST":
        form = RehabProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.patient = patient
            program.save()
            create_progress_week(
                program=program,
                week_number=1,
                title="Week 1 — Foundation",
                summary=program.goals or "Initial week of your personalised rehab program.",
                notify=True,
            )
            messages.success(request, "Rehab program created.")
            return redirect("staff:program_detail", program_id=program.id)
    else:
        form = RehabProgramForm()
    return render(
        request,
        "staff/program_create.html",
        {"form": form, "patient": patient},
    )


@staff_required
@require_POST
def advance_weeks(request):
    entries = advance_program_weeks()
    if entries:
        messages.success(request, f"Auto-advanced {len(entries)} program week(s).")
    else:
        messages.info(request, "No programs needed a new week today.")
    return redirect("staff:programs")


@staff_required
def add_consultation(request, user_id):
    patient = get_object_or_404(User, pk=user_id, role=User.Role.PATIENT)
    if request.method == "POST":
        form = ConsultationStaffForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.save()
            messages.success(request, "Consultation record saved.")
            return redirect("staff:patient_detail", user_id=patient.id)
    else:
        form = ConsultationStaffForm()
    return render(
        request,
        "staff/consultation_form.html",
        {"form": form, "patient": patient},
    )


@staff_required
def notifications_log(request):
    return render(
        request,
        "staff/notifications.html",
        {"logs": NotificationLog.objects.all()[:100]},
    )
