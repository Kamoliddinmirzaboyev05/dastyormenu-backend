"""Create missing user profiles for existing users."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Create missing user profiles for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization-id',
            type=str,
            help='Organization ID to assign to users without profile',
        )
        parser.add_argument(
            '--role',
            type=str,
            default='manager',
            help='Default role for users without profile (default: manager)',
        )

    def handle(self, *args, **options):
        organization_id = options.get('organization_id')
        default_role = options.get('role', 'manager')
        
        # Get users without profile
        users_without_profile = User.objects.filter(userprofile__isnull=True)
        
        if not users_without_profile.exists():
            self.stdout.write(
                self.style.SUCCESS('✅ All users have profiles!')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  Found {users_without_profile.count()} users without profile')
        )
        
        # Get or create default organization
        if organization_id:
            try:
                organization = Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Organization with ID {organization_id} not found')
                )
                return
        else:
            # Get first organization or create default
            organization = Organization.objects.first()
            if not organization:
                organization = Organization.objects.create(
                    name='Default Organization',
                    slug='default',
                    is_active=True
                )
                self.stdout.write(
                    self.style.WARNING('⚠️  Created default organization')
                )
        
        # Create profiles
        created_count = 0
        for user in users_without_profile:
            full_name = user.get_full_name() or user.username
            
            profile = UserProfile.objects.create(
                user=user,
                organization=organization,
                full_name=full_name,
                role=default_role,
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created profile for: {user.username} ({full_name})')
            )
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully created {created_count} profiles!')
        )
        self.stdout.write(
            self.style.WARNING(f'📋 Organization: {organization.name}')
        )
        self.stdout.write(
            self.style.WARNING(f'👤 Default role: {default_role}')
        )
