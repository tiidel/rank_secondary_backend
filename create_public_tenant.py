from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from tenant.models import Client, Domain

class Command(BaseCommand):
    help = 'Creates the public tenant and assigns a domain'

    def handle(self, *args, **options):

        public_tenant, created = Client.objects.get_or_create( schema_name="public", name= "Default host" )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Public tenant created successfully'))
       
        else:
            self.stdout.write(self.style.WARNING('Public tenant already exists'))

        
        current_site = Site.objects.get_current()
        domain_name = current_site.domain
       
        if not Domain.objects.filter(tenant=public_tenant).exists():
            domain = Domain.objects.create('localhost', tenant=public_tenant, is_primary=True)
            self.stdout.write(self.style.SUCCESS('Domain created successfully'))

        else:
            self.stdout.write(self.style.WARNING('Domain already exists for public tenant'))