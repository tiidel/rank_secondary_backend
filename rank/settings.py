from pathlib import Path
from decouple import config
import os
import dj_database_url

from firebase_admin import initialize_app, credentials

from datetime import timedelta
from helper.helper import *

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIRS = os.path.join(BASE_DIR, 'templates')

FRONTEND_DOMAIN = 'https://rank.com'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG')


FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": config('FIREBASE_SERVER_KEY'),
    "DEFAULT_FIREBASE_APP": None,
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": False,
    "PROJECT_ID": "rank-7ec5b",
}

ALLOWED_HOSTS = ['*', CLIENT_URL, CLIENT_URL_WILDCARD]


# Application definition
TENANT_APPS = [
    'school',
    'core',
    'commerce',
]

SHARED_APPS = [
    'core',
    'commerce',
    'django_tenants',
    'tenant',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_extensions',
    'celery',
    'fcm_django',
]


# WKHTMLTOPDF = os.path.join(BASE_DIR, 'wkhtmltopdf/bin/wkhtmltopdf.exe')
# WKHTMLTOPDF_CMD_OPTIONS = {
#     'quiet': True,
# }

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS ]
AUTH_USER_MODEL = 'core.user'

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ],
    
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
}


ROOT_URLCONF = 'rank.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIRS],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



WSGI_APPLICATION = 'rank.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django_tenants.postgresql_backend',
#         'NAME': 'postgres',
#         'USER': 'ragrbugguk',
#         'PASSWORD': '#@!prodigy#676638050&&',
#         'HOST': 'rank-server.postgres.database.azure.com',
#         'PORT': '5432',
#     }
# }



DATABASE_ROUTERS = [
    'django_tenants.routers.TenantSyncRouter',
]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = os.path.join(BASE_DIR, 'static'),
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')


MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
}

## CELERY BROKER SETTING
CELERY_BROKER_URL = config('CELERY_URL')
CELERY_RESULT_BACKEND =  config('CELERY_URL')
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_CONCURRENCY = 4 


# AWS S3 BUCKET CONFIGURATION
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None



## CONFIGURATION FOR MAIL SERVER
EMAIL_USE_TLS = True     
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=config('EMAIL_PORT')
EMAIL_HOST_USER= config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD= config('EMAIL_HOST_PASSWORD')
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'

## TENANT MANAGEMENT
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TENANT_MODEL = "tenant.Client"

TENANT_DOMAIN_MODEL = "tenant.Domain"

PUBLIC_SCHEMA_URLCONF = 'rank.urls'



#FIREBASE CONFIGURATION
cred = credentials.Certificate(os.path.join(BASE_DIR, 'credentials.json'))
FIREBASE_APP = initialize_app(cred)


FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCsyMAEaw1JXhB-UjsGKClN-Vu8ACn-RAg",
    "authDomain": "rank-7c233.firebaseapp.com",
    "projectId": "rank-7c233",
    "storageBucket": "rank-7c233.appspot.com",
    "messagingSenderId": "238023174027",
    "appId": "1:238023174027:web:31fc5f2571cf9a07e0f18e",
    "fcm": "BEkco1ByWwEZteLwy_MHJAYZxIVn-j7gLXnC59e6lOKjcvUnoO4TQeWvGu6KfG4MifujJY7PItjbo2-Er0294Ks",
}


