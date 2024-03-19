from django.shortcuts import render
from rest_framework_simplejwt import tokens
from rest_framework.views import APIView, status, Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
# Create your views here.

from .serializers import *


class StoreMaterialAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser] 
    serializer_class = SchoolMaterialSerializer

    def get(self, request):
        materials = SchoolMaterial.objects.filter(owner = request.user)
        serializer = self.serializer_class(materials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        request.data['owner'] = request.user.id
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        