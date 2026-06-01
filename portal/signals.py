from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import ServicePlan

DEFAULT_PLANS = [
    {
        "slug": "video-consultation",
        "name": "1-on-1 Video Consultation",
        "description": "30-minute live video consultation with movement assessment.",
        "price_inr": 500,
        "duration_label": "30 minutes",
        "is_recurring": False,
    },
    {
        "slug": "monthly-rehab",
        "name": "Monthly Rehab Program",
        "description": "Personalised week-by-week online rehab with WhatsApp support.",
        "price_inr": 3000,
        "duration_label": "Full month",
        "is_recurring": True,
    },
]


@receiver(post_migrate)
def seed_service_plans(sender, **kwargs):
    if sender.name != "portal":
        return
    for plan in DEFAULT_PLANS:
        ServicePlan.objects.update_or_create(slug=plan["slug"], defaults=plan)
