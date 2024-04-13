from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from .views import *

from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet, FCMDeviceViewSet

schema_view = get_schema_view(
   openapi.Info(
      title="SECONDARY SCHOOL MANAGEMENT SYSTEM",
      default_version='v1',
      description="application to validate students in a university",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


handler404 = not_found

urlpatterns = [
    path('api/v1/create-tenant/', create_tenant_view, name='TENANT_VIEW'),
    path('api/v1/tenant-exist/', tenant_exist_view, name='TENANT_VIEW'),
    path('api/v1/auth/', include('core.urls'), name="AUTH"),
    path('api/v1/', include('school.urls'), name='SCHOOL'),
    path('api/v1/commerce/', include('commerce.urls'), name='SCHOOL STORE'),
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', index, name='index'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

   #FIREBASE ROUTES
   path('api/v1/devices/register/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
   path('api/v1/devices/', FCMDeviceViewSet.as_view({'get': 'list'}), name='list_fcm_device'),

   # ANOUNCEMENT
   #  path('send-notification/', send_notification, name='send_notification'),

]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
