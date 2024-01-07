from .settings import *




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRE_DATABASE'),
        'USER': config('POSTGRE_USER'),
        'PASSWORD': config('POSTGRE_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
