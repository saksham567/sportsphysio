from django.contrib import admin

from .models import (
    Booking,
    CalendlyWebhookLog,
    ConsultationHistory,
    NotificationLog,
    Payment,
    ProgressEntry,
    RehabProgram,
    ServicePlan,
)


@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_inr", "is_recurring", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("contact_name", "contact_email", "scheduled_at", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("guest_email", "guest_name", "patient__email")
    raw_id_fields = ("patient",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("contact_name", "amount_inr", "plan_label", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("guest_email", "guest_name", "patient__email", "upi_transaction_id")
    raw_id_fields = ("patient", "booking", "verified_by")


@admin.register(RehabProgram)
class RehabProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "status", "start_date")
    list_filter = ("status",)
    raw_id_fields = ("patient",)


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ("program", "week_number", "recorded_at", "pain_level")


@admin.register(ConsultationHistory)
class ConsultationHistoryAdmin(admin.ModelAdmin):
    list_display = ("patient", "session_type", "session_date")
    raw_id_fields = ("patient", "booking")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("channel", "recipient_email", "subject", "success", "created_at")
    list_filter = ("channel", "success")


@admin.register(CalendlyWebhookLog)
class CalendlyWebhookLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "invitee_uri", "processed", "created_at")
    list_filter = ("processed", "event_type")
