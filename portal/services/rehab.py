from datetime import timedelta

from django.utils import timezone

from portal.models import ProgressEntry, RehabProgram, ServicePlan
from portal.services.notifications import notify_new_progress_week


def create_rehab_program_for_payment(*, payment, patient):
    """Start monthly rehab program after payment verification."""
    plan = payment.plan
    if not plan and payment.plan_label:
        plan = ServicePlan.objects.filter(slug="monthly-rehab").first()
    if plan and not plan.is_recurring:
        return None

    if not plan:
        plan = ServicePlan.objects.filter(slug="monthly-rehab").first()
    if not plan:
        return None

    existing = RehabProgram.objects.filter(
        patient=patient,
        payment=payment,
        status=RehabProgram.Status.ACTIVE,
    ).first()
    if existing:
        return existing

    today = timezone.localdate()
    program = RehabProgram.objects.create(
        patient=patient,
        plan=plan,
        payment=payment,
        title=f"{plan.name} — {today.strftime('%b %Y')}",
        start_date=today,
        status=RehabProgram.Status.ACTIVE,
        goals="Personalised week-by-week rehab with WhatsApp support.",
    )
    entry = create_progress_week(
        program=program,
        week_number=1,
        title="Week 1 — Foundation & assessment",
        summary=(
            "Welcome to your rehab program. This week focuses on baseline movement "
            "patterns, pain monitoring, and establishing your daily exercise routine. "
            "Exercise videos will be shared on WhatsApp."
        ),
        exercises_total=5,
        notify=True,
    )
    return program


def create_progress_week(
    *,
    program,
    week_number,
    title,
    summary,
    exercises_total=5,
    clinician_notes="",
    notify=True,
):
    today = timezone.localdate()
    entry, created = ProgressEntry.objects.get_or_create(
        program=program,
        week_number=week_number,
        defaults={
            "title": title,
            "summary": summary,
            "exercises_total": exercises_total,
            "exercises_completed": 0,
            "clinician_notes": clinician_notes,
            "recorded_at": today,
        },
    )
    if created and notify and not entry.notified_patient:
        notify_new_progress_week(
            patient=program.patient,
            program=program,
            entry=entry,
        )
        entry.notified_patient = True
        entry.save(update_fields=["notified_patient"])
    return entry


def advance_program_weeks(*, program=None):
    """
    For active programs, add a new week if 7+ days passed since last entry.
    Returns list of newly created ProgressEntry objects.
    """
    today = timezone.localdate()
    programs = RehabProgram.objects.filter(status=RehabProgram.Status.ACTIVE)
    if program:
        programs = programs.filter(pk=program.pk)

    created_entries = []
    for prog in programs:
        latest = prog.progress_entries.order_by("-week_number").first()
        if not latest:
            continue
        days_since = (today - latest.recorded_at).days
        if days_since < 7:
            continue

        next_week = latest.week_number + 1
        entry = create_progress_week(
            program=prog,
            week_number=next_week,
            title=f"Week {next_week} — Progressive loading",
            summary=(
                f"Week {next_week} of your personalised program. Continue daily exercises, "
                "track pain levels, and message Dr. Aahana on WhatsApp with form videos."
            ),
            exercises_total=latest.exercises_total or 5,
            notify=True,
        )
        created_entries.append(entry)

        if next_week >= 4:
            prog.status = RehabProgram.Status.COMPLETED
            prog.end_date = today
            prog.save(update_fields=["status", "end_date", "updated_at"])

    return created_entries
