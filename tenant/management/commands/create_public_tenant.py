# from django.apps import apps
# from django.core.management.base import BaseCommand
# from tenant.models import Client, Domain

# class Command(BaseCommand):
#     help = 'Creates the public tenant and assigns a domain'

#     def handle(self, *args, **options):
#         try:
#             # Check if a Client with schema_name 'public' already exists
#             public_tenant = Client.objects.filter(schema_name="public").first()

#             if not public_tenant:
#                 public_tenant = Client.objects.create(schema_name="public", name="Default host")
#                 self.stdout.write(self.style.SUCCESS('Public tenant created successfully'))
#             else:
#                 self.stdout.write(self.style.WARNING('Public tenant already exists'))

#             # Retrieve the Site model dynamically
#             Site = apps.get_model('sites', 'Site')
#             current_site = Site.objects.get_current()
#             domain_name = current_site.domain

#             if not Domain.objects.filter(tenant=public_tenant).exists():
#                 domain = Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)
#                 self.stdout.write(self.style.SUCCESS('Domain created successfully'))
#             else:
#                 self.stdout.write(self.style.WARNING('Domain already exists for public tenant'))

#         except Exception as err:
#             print('error creating tenant', err)


from django.core.management.base import BaseCommand
from tenant.models import Client, Domain

class Command(BaseCommand):
    help = 'Creates the public tenant and assigns a domain'

    def handle(self, *args, **options):
        try:
            public_tenant, created = Client.objects.get_or_create(schema_name="public", name="Default host")

            if created:
                self.stdout.write(self.style.SUCCESS('Public tenant created successfully'))
            else:
                self.stdout.write(self.style.WARNING('Public tenant already exists'))

            domain_name = 'localhost'  # Replace 'localhost' with the actual domain name
            
            if not Domain.objects.filter(tenant=public_tenant).exists():
                domain = Domain.objects.create(domain=domain_name, tenant=public_tenant, is_primary=True)
                self.stdout.write(self.style.SUCCESS('Domain created successfully'))
            else:
                self.stdout.write(self.style.WARNING('Domain already exists for public tenant'))

        except Exception as err:
            print('error creating tenant', err)
