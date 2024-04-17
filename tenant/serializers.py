from rest_framework import serializers
from .models import *

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class DomainSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()
    class Meta:
        model = Domain
        fields = '__all__'
