from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Create a staff user for the staff dashboard"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--name", default="Dr. Aahana")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        name = options["name"].strip().split(None, 1)
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": name[0],
                "last_name": name[1] if len(name) > 1 else "",
                "role": User.Role.STAFF,
                "is_staff": True,
                "is_active": True,
            },
        )
        user.set_password(options["password"])
        user.role = User.Role.STAFF
        user.is_staff = True
        user.save()
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} staff user: {email}"))
