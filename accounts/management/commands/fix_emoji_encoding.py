
from django.core.management.base import BaseCommand
from accounts.models import User, InfluencerProfile, CompanyProfile
import ftfy

class Command(BaseCommand):
    help = 'Fixes emoji encoding issues in the database using ftfy'

    def handle(self, *args, **options):
        self.stdout.write('Starting emoji encoding fix...')
        
        # Fix Users
        for user in User.objects.all():
            changed = False
            if user.username:
                fixed_username = ftfy.fix_text(user.username)
                if fixed_username != user.username:
                    user.username = fixed_username
                    changed = True
            
            if changed:
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Fixed User {user.id}'))

        # Fix Influencer Profiles
        for profile in InfluencerProfile.objects.all():
            changed = False
            if profile.bio:
                fixed_bio = ftfy.fix_text(profile.bio)
                if fixed_bio != profile.bio:
                    profile.bio = fixed_bio
                    changed = True
            
            if profile.category:
                fixed_category = ftfy.fix_text(profile.category)
                if fixed_category != profile.category:
                    profile.category = fixed_category
                    changed = True

            if changed:
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'Fixed InfluencerProfile {profile.id}'))

        # Fix Company Profiles
        for profile in CompanyProfile.objects.all():
            changed = False
            if profile.description:
                fixed_description = ftfy.fix_text(profile.description)
                if fixed_description != profile.description:
                    profile.description = fixed_description
                    changed = True
            
            if profile.company_name:
                fixed_name = ftfy.fix_text(profile.company_name)
                if fixed_name != profile.company_name:
                    profile.company_name = fixed_name
                    changed = True

            if changed:
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'Fixed CompanyProfile {profile.id}'))

        self.stdout.write(self.style.SUCCESS('Finished fixing emoji encoding.'))
