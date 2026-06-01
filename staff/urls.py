from django.urls import path

from . import views

app_name = "staff"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("payments/", views.payments, name="payments"),
    path("payments/<int:payment_id>/", views.payment_detail, name="payment_detail"),
    path("bookings/", views.bookings, name="bookings"),
    path("patients/", views.patients, name="patients"),
    path("patients/<int:user_id>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:user_id>/consultation/", views.add_consultation, name="add_consultation"),
    path("patients/<int:user_id>/program/new/", views.program_create, name="program_create"),
    path("programs/", views.programs, name="programs"),
    path("programs/<int:program_id>/", views.program_detail, name="program_detail"),
    path("programs/advance-weeks/", views.advance_weeks, name="advance_weeks"),
    path("notifications/", views.notifications_log, name="notifications"),
]
