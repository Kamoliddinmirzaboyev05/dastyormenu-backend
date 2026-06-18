"""Create admin user automatically."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Create admin user if not exists'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('ADMIN_PASSWORD')

        # Refuse to create a superuser with a known/default password.
        if not password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_PASSWORD not set — skipping superuser creation. '
                'Set a strong ADMIN_PASSWORD env var to auto-create the admin.'
            ))
            return
        if len(password) < 10:
            self.stdout.write(self.style.ERROR(
                'ADMIN_PASSWORD too weak (min 10 chars). Superuser not created.'
            ))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists.'))
