
from django.contrib import admin
from django.urls import path, include
from rank.views import not_found

from .views import index

handler404 = not_found 

urlpatterns = [
    path('api/v1/auth/', include('core.urls'), name="AUTH"),
    path('api/v1/', include('school.urls'), name='SCHOOL'),
    path('admin/', admin.site.urls),
    path('', index),
]
