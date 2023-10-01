# from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import FireConnect


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


urlpatterns = [
    # path('admin/', admin.site.urls),
   #  path('firebase/', FireConnect.as_view(), name='firebase'),
    path('api/v1/auth/', include('core.urls'), name="AUTH"),
    path('api/v1/', include('school.urls'), name='SCHOOL'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

