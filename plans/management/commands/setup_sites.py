from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Setup default site configuration'
    
    def handle(self, *args, **options):
        # Default site (ID=1)
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'Telecomedia Development'
            }
        )
        
        if not created:
            site.domain = '127.0.0.1:8000'
            site.name = 'Telecomedia Development'
            site.save()
        
        # Additional sites for different environments
        Site.objects.get_or_create(
            domain='telecomedia.com',
            defaults={'name': 'Telecomedia Production'}
        )
        
        Site.objects.get_or_create(
            domain='staging.telecomedia.com',
            defaults={'name': 'Telecomedia Staging'}
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ Setup site: {site.domain} (ID: {site.id})'
        ))