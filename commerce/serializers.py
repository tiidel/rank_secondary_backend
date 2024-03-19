from rest_framework import serializers
from .models import *
from core.serializers import LoginSerializer

class SchoolMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolMaterial
        fields = '__all__'
