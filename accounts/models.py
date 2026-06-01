from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        STAFF = "staff", "Staff"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )
    phone = models.CharField(max_length=15, blank=True)
    whatsapp = models.CharField(
        max_length=15,
        blank=True,
        help_text="WhatsApp number for rehab support",
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def display_name(self):
        full = self.get_full_name().strip()
        return full or self.username

    def __str__(self):
        return self.display_name


class PatientProfile(models.Model):
    """Extended clinical profile for registered patients."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    primary_concern = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. ACL rehab, lower back pain",
    )
    injury_history = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes (staff only)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profile — {self.user.display_name}"
