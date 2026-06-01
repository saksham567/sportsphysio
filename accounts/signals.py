from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PatientProfile, User


@receiver(post_save, sender=User)
def ensure_patient_profile(sender, instance, created, **kwargs):
    if instance.role == User.Role.PATIENT:
        PatientProfile.objects.get_or_create(user=instance)
