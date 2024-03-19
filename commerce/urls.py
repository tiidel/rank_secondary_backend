from django.urls import path

from .views import *


urlpatterns = [
    path('store-materials/', StoreMaterialAPIView.as_view(), name='store_material'),
]
