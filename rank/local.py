from .settings import *




DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'rank',
        'USER': 'postgres',
        'PASSWORD': 'prodigy',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)
