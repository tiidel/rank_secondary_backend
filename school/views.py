from django.shortcuts import render
from rest_framework_simplejwt import tokens
from .models import Student, Subject, Department, School,Level, Staff, Registration, Guardian
from .serializer import SchoolSerializer, SubjectSerializer, StudentSerializer, DepartmentSerializer, LevelSerializer, ProgramSerializer, StaffSerializer, RegistrationSerializer, GuardianSerializer
from .serializer import ProgramSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView, status, Response


class ProgramView(APIView):
    def get(self, request):
    # queryset = ProgramSerializer.objects.all()
    # serializer_class = ProgramSerializer
        Response("program", status=status.HTTP_200_OK)

class SchoolView(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class DepartmentView(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class LevelView(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class StaffView(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


class SubjectView(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class GuardianView(viewsets.ModelViewSet):
    queryset = Guardian.objects.all()
    serializer_class = GuardianSerializer


class RegistrationView(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer


class StudentView(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

