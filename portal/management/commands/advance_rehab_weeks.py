from django.core.management.base import BaseCommand

from portal.services.rehab import advance_program_weeks


class Command(BaseCommand):
    help = "Create new rehab progress weeks for active programs (run daily via cron)"

    def handle(self, *args, **options):
        entries = advance_program_weeks()
        if entries:
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(entries)} new progress week(s).")
            )
        else:
            self.stdout.write("No new weeks needed today.")
