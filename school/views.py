from django.shortcuts import render
from rest_framework_simplejwt import tokens
from rest_framework.views import APIView, status, Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

    
from .models import Student, Subject, Department, School,Level, Staff, Registration, Guardian
from .serializer import *
from helper.enum import JobApplicantStatus
from core.models import User
from core.serializers import LoginSerializer

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import Group

import base64
import uuid
from django.http import HttpResponseBadRequest

from django.db.models import Case, CharField, Value, When

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
        serializers = []
        for class_data in request.data:
            serializer = self.serializer_class(data=class_data)
            if serializer.is_valid():
                serializer.save()
                serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response([serializer.data for serializer in serializers], status=status.HTTP_201_CREATED)
    


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
            serializer.save()
            
            # send_invite_mail(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response( serializer.errors, status=status.HTTP_400_BAD_REQUEST )


class InviteConfirmationView(APIView):
    def find_invitation(self, slug):
        invitation = Invitation.objects.filter(invitation_code=slug).first()
        return invitation
    
    def assign_user_to_group(self, user, role):
        group = Group.objects.get(name__iexact=role)
        if group:
            return group.user_set.add(user)


    def create_staff_membership(self, user, role):
        staff = Staff.objects.create(user=user, role=role)
        return staff

    def check_validity(self, slug):
        invitation = self.find_invitation(slug)

        if not invitation.is_expired():
            return invitation.role
        else: return False
    
    def confirm_invitee(self, slug, request):
        email = request.data.get('email')
        has_invite = Invitation.objects.filter(invitation_code=slug, recipient_email=email).exists()
        return has_invite
    
    def accept_invitation(self, slug):
        invitation = self.find_invitation(slug)
        invitation.invite_status = 'accepted'
        invitation.save()

    def post(self, request, invite_id):
        invite_role = self.check_validity(invite_id)
        
        if not invite_role:
            return Response({"message": "Your invitation is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.confirm_invitee(invite_id, request):
            return Response({"message": "We cannot find an invitation for this email"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            username = request.data.get('username')
            user_exist = User.objects.filter(username=username).first()
            
            if user_exist:
                return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
            

            user = User.objects.create_user(**request.data)
            user_in_group = self.assign_user_to_group(user, invite_role)
            staff_created = self.create_staff_membership(user, invite_role)
            self.accept_invitation(invite_id)

            if staff_created:
                user_serializer = LoginSerializer(user)
                return Response( user_serializer.data,  status=status.HTTP_201_CREATED)

        except Exception as error:
            print(error)
            return Response( status=status.HTTP_400_BAD_REQUEST)
        
        return Response("Returning something")


class RequestAccessToSchool(APIView):
    serializer_class = SchoolStaffApplySerializer
    def compress_uuid(self, uuid_str):
        uuid_bytes = uuid.UUID(uuid_str).bytes
        compressed = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('utf-8')
        return compressed

    def is_valid_school(self, id):
        school_exist = School.objects.filter(id=id).exists()
        return school_exist
    
    def check_school_id(self, school_code, school_id):
        
        if not self.is_valid_school(school_id):
            raise HttpResponseBadRequest("Invalid school ID")

        compressed_school_id = self.compress_uuid(school_id)

        if compressed_school_id != school_code:
            raise HttpResponseBadRequest("This code is not recorgnized with associated code")
        
        return compressed_school_id
    
    def get(self, request):
        user_list = SchoolStaffApply.objects.filter(hidden=False)
        serializers = self.serializer_class(user_list, many=True)

        return Response( serializers.data, status=status.HTTP_200_OK )

    def post(self, request, school_id):
        school_code = request.data.get('id')
        
        valid_code = self.check_school_id(school_code, school_id)

        if valid_code:
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Provided code is invalid" }, status=status.HTTP_400_BAD_REQUEST)



# class StaffView(APIView):


# class SubjectView(APIView):


# class GuardianView(APIView):


# class RegistrationView(APIView):


# class StudentView(APIView):


class JobApplicantsView(APIView):
    serializer_class = JobSerializer

    def get(self, request):
        # Define custom ordering based on search_status
        custom_order = Case(
            When(search_status=JobApplicantStatus.Active, then=Value(1)),
            When(search_status=JobApplicantStatus.Accepted, then=Value(2)),
            When(search_status=JobApplicantStatus.Low, then=Value(3)),
            When(search_status=JobApplicantStatus.Unqualified, then=Value(4)),
            default=Value(5),
            output_field=CharField(),
        )

        jobs = Job.objects.filter(is_hired=False, rejected=False).exclude(search_status=Job.JobApplicantStatus.ACCEPTED)

        # Apply custom ordering
        jobs = jobs.annotate(custom_order=custom_order).order_by('custom_order')

        serializer = self.serializer_class(jobs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
   
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)