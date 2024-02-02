from django.shortcuts import render
from rest_framework_simplejwt import tokens
from rest_framework.views import APIView, status, Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

    
from .models import Student, Subject, Department, School,Level, Staff, Registration, Guardian
from .serializer import *

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser

"""
||=============================================================||
||=============================================================||
||======= MINIMIZE CODE SIZE AND REDUCE COMPLEXITY ============||
||=============================================================||
||=============================================================||
"""


class ProgramView(APIView):
    def get(self, request):
    # queryset = ProgramSerializer.objects.all()
    # serializer_class = ProgramSerializer
        Response("program", status=status.HTTP_200_OK)

class SchoolView(APIView):
    """
    Description: Rest API for all requests involving school
    Author: kimbidarl@gmail
    """

    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schools = School.objects.all()
        serializers = self.serializer_class(schools, many=True)
        return Response( serializers.data, status=status.HTTP_200_OK )
        
    
    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_201_CREATED)

    def delete(self, request):
        pass
    


class SchoolFilesView(APIView):
    parser_classes = [MultiPartParser] 
    serializer_class = SchoolFileSerializer
    def put(self, request, id):
        try:
            school = School.objects.get(id=id)
            
        except School.DoesNotExist:
            return Response({'error': 'School not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializers = self.serializer_class(school, data=request.data)
        
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
#DEPARTMENT  
class DepartementView(APIView):
    serializer_class = DepartmentSerializer
    
    def get(self, request):
        departments = Department.objects.all()
        serializers = self.serializer_class(departments, many=True)
        return Response( serializers.data, status=status.HTTP_200_OK )
    
    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentItemView(APIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def find_department_by_id(self, id):
            return Department.objects.filter(id=id).first()
            

    def get(self, request, department_id):
        department = self.find_department_by_id(department_id)
        if not department:
            return Response(f"Department with id {department_id} not found", status=status.HTTP_404_NOT_FOUND)
        serializers = self.serializer_class(department)
        return Response(serializers.data, status=status.HTTP_200_OK)
        
    
    def put(self, request, department_id):
        try:
            department = self.find_department_by_id(department_id)
            
        except Department.DoesNotExist:
            return Response(f"Department with id {department_id} not found", status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(department, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, department_id):
        department = self.find_department_by_id(department_id)
        if not department:
            return Response({"message": "No department with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

    def patch(self, request, department_id):
        department = self.find_department_by_id(department_id)
        if not department:
            return Response({"message": "No department with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializers = self.serializer_class(department, data=request.data, partial=True)

        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

#  LEVELS
class LevelView(APIView):    
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        levels = Level.objects.all()
        serializers = self.serializer_class(levels, many=True)
        return Response( serializers.data, status=status.HTTP_200_OK )
    
    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST) 

class LevelItemView(APIView):
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def find_level_by_id(self, id):
            return Level.objects.get(id=id, is_deleted=False).first()
    
    def get(self, request, level_id):
        level = self.find_level_by_id(level_id)
        if not level:
            return Response("Level with id {level_id} was not found", status=status.HTTP_404_NOT_FOUND)
        serializers = self.serializer_class(level)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def patch(self, request, level_id):
        level = self.find_level_by_id(level_id)
        if not level:
            return Response({"message": "Level with id {level_id} was not found"}, status=status.HTTP_404_NOT_FOUND)
        serializers = self.serializer_class(level, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_202_ACCEPTED)
    
    def put(self, request, level_id):
        level = self.find_level_by_id(level_id)
        if not level:
            return Response({"message": "Level with id {level_id} was not found"}, status=status.HTTP_404_NOT_FOUND)
        serializers = self.serializer_class( level, data=request.data )
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, level_id):
        level = self.find_level_by_id(level_id)
        if not level:
            return Response({"message": "Level with id {level_id} was not found"}, status=status.HTTP_404_NOT_FOUND)
        if level.is_deleted:
            return Response({"message": "Level with id {level_id} was already deleted"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        level.is_deleted = True
        level.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


#CLASS
class ClassView(APIView):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classes = Class.objects.all()
        serializers = self.serializer_class(classes, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializers = self.serializer_class(data = request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)

        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassItemView(APIView):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    def find_class_by_id(self, id):
            return Class.objects.filter(id=id).first()

    def get(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        serializers = self.serializer_class(cls)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def put(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializers = self.serializer_class(cls, data=request.data)

        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializers = self.serializer_class(cls, data=request.data, partial=True)

        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        if cls.is_delete:
            return Response({"message": "Class with id {class_id} already been deleted"}, status=status.HTTP_400_BAD_REQUEST)
        cls.is_delete = True
        cls.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


#STAFF INVITE
class InvitationView(APIView):
    serializer_class = InvitationSerializer
    def get(self, request):
        return Response({"message": "invitations sent"}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            invitation = serializer.save()
            # Additional logic, such as sending notifications
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST )


# class StaffView(APIView):


# class SubjectView(APIView):


# class GuardianView(APIView):


# class RegistrationView(APIView):


# class StudentView(APIView):

