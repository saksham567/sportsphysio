from django.conf import settings
from django.db import models


class ServicePlan(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price_inr = models.PositiveIntegerField()
    duration_label = models.CharField(max_length=80, blank=True)
    is_recurring = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price_inr"]

    def __str__(self):
        return f"{self.name} — ₹{self.price_inr:,}"

    @property
    def price_display(self):
        return f"₹{self.price_inr:,}"


class Booking(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        null=True,
        blank=True,
    )
    guest_name = models.CharField(max_length=200, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=15, blank=True)
    plan = models.ForeignKey(
        ServicePlan,
        on_delete=models.PROTECT,
        related_name="bookings",
        null=True,
        blank=True,
    )
    plan_label = models.CharField(max_length=200, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    calendly_event_uri = models.CharField(max_length=255, blank=True)
    calendly_invitee_uri = models.CharField(
        max_length=255,
        blank=True,
        unique=True,
        null=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at", "-created_at"]

    @property
    def contact_name(self):
        if self.patient_id:
            return self.patient.display_name
        return self.guest_name or "Guest"

    @property
    def contact_email(self):
        if self.patient_id:
            return self.patient.email
        return self.guest_email

    def __str__(self):
        when = self.scheduled_at.strftime("%d %b %Y") if self.scheduled_at else "Unscheduled"
        return f"{self.contact_name} — {when}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending verification"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    guest_name = models.CharField(max_length=200, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=15, blank=True)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    plan = models.ForeignKey(
        ServicePlan,
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
    )
    plan_label = models.CharField(max_length=200)
    amount_inr = models.PositiveIntegerField()
    upi_transaction_id = models.CharField(max_length=120, blank=True)
    payment_note = models.CharField(max_length=255, blank=True)
    screenshot = models.ImageField(upload_to="payments/%Y/%m/", blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_payments",
    )
    login_credentials_sent = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def contact_name(self):
        if self.patient_id:
            return self.patient.display_name
        return self.guest_name or self.payment_note

    @property
    def contact_email(self):
        if self.patient_id:
            return self.patient.email
        return self.guest_email

    @property
    def contact_phone(self):
        if self.patient_id:
            return self.patient.phone or self.patient.whatsapp
        return self.guest_phone

    def __str__(self):
        name = self.contact_name
        return f"₹{self.amount_inr:,} — {name} ({self.get_status_display()})"


class RehabProgram(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rehab_programs",
    )
    plan = models.ForeignKey(
        ServicePlan,
        on_delete=models.PROTECT,
        related_name="rehab_programs",
        null=True,
        blank=True,
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rehab_programs",
    )
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} — {self.patient.display_name}"

    @property
    def current_week_number(self):
        latest = self.progress_entries.order_by("-week_number").first()
        return latest.week_number if latest else 0


class ProgressEntry(models.Model):
    program = models.ForeignKey(
        RehabProgram,
        on_delete=models.CASCADE,
        related_name="progress_entries",
    )
    week_number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    summary = models.TextField()
    exercises_completed = models.PositiveSmallIntegerField(default=0)
    exercises_total = models.PositiveSmallIntegerField(default=0)
    pain_level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="0–10 scale reported by patient",
    )
    patient_notes = models.TextField(blank=True)
    clinician_notes = models.TextField(blank=True)
    recorded_at = models.DateField()
    notified_patient = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at", "-week_number"]
        unique_together = [("program", "week_number")]

    def __str__(self):
        return f"Week {self.week_number} — {self.program.title}"

    @property
    def completion_percent(self):
        if not self.exercises_total:
            return None
        return round(100 * self.exercises_completed / self.exercises_total)


class ConsultationHistory(models.Model):
    class SessionType(models.TextChoices):
        VIDEO = "video", "Video consultation"
        FOLLOW_UP = "follow_up", "Follow-up"
        ASSESSMENT = "assessment", "Assessment"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultations",
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultation",
    )
    session_type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.VIDEO,
    )
    session_date = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    chief_complaint = models.CharField(max_length=255, blank=True)
    assessment_summary = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-session_date"]
        verbose_name_plural = "Consultation histories"

    def __str__(self):
        return f"{self.get_session_type_display()} — {self.patient.display_name}"


class NotificationLog(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        WHATSAPP = "whatsapp", "WhatsApp"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.channel} — {self.subject or self.recipient_email}"


class CalendlyWebhookLog(models.Model):
    event_type = models.CharField(max_length=80)
    invitee_uri = models.CharField(max_length=255, blank=True)
    payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} — {self.created_at:%d %b %Y %H:%M}"
