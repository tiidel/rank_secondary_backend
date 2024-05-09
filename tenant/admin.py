from django.contrib import admin

from .models import *
from django_tenants.admin import TenantAdminMixin

@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_on')



models = [
    Domain
]

admin.site.register( models )