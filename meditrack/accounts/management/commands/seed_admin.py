from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Creates (or updates) the single default administrator account.

    MediTrack is a single-admin system - no public registration page is
    provided. Run this once after migrating:

        python manage.py seed_admin
    """
    help = 'Creates the single default MediTrack admin account.'

    def handle(self, *args, **options):
        email = settings.DEFAULT_ADMIN_EMAIL
        password = settings.DEFAULT_ADMIN_PASSWORD
        name = settings.DEFAULT_ADMIN_NAME

        # Enforce a single admin account: remove any other superusers.
        User.objects.filter(is_superuser=True).exclude(email=email).delete()

        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': name,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        user.email = email
        user.first_name = user.first_name or name
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Default admin account created: {email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Default admin account updated: {email}'))
