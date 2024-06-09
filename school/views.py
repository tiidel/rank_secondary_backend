from django.shortcuts import render
from django.db import transaction
from rest_framework_simplejwt import tokens
from rest_framework.views import APIView, status, Response
from rest_framework.pagination import PageNumberPagination
from wkhtmltopdf.views import PDFTemplateResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from collections import defaultdict
from django.db.models.signals import pre_save
    
from .models import *
from .serializer import *
from core.permissions import *
from helper.enum import JobApplicantStatus
from django.db.models import Count, Q, F
from helper.workers import *
from core.models import User
from core.serializers import LoginSerializer
from .payments import flutterwave_verify_transaction

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import Group
from django.dispatch import receiver
from datetime import datetime

import base64
import uuid
import random
import copy
import string
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError

from django.db.models import Case, CharField, Value, When

"""
||=============================================================||
||=============================================================||
||======= MINIMIZE CODE SIZE AND REDUCE COMPLEXITY ============||
||=============================================================||
||=============================================================||
"""


@receiver(post_save, sender=Subject)
def create_student_subjects(sender, instance, created, **kwargs):
    """
    Signal receiver function to create StudentSubjects instances
    for all students when a new subject is created.
    """
    if created:
        students = instance.cls.students.all()
        sequences = Sequence.objects.all()
        
        for student in students:
            for sequence in sequences:
                student_subject = StudentSubjects.objects.create(student=student, subject=instance, sequence=sequence)
            
                update_grade_instance(student_subject)



def update_grade_instance(student_subject):
    """
    Update Grade instance for the student whenever a StudentSubjects instance is created or updated.
    """
    grade, _ = Grade.objects.get_or_create(
        student=student_subject.student,
        classroom=student_subject.student.student_class,
        term=student_subject.sequence.term
    )

    grade.grade_list.add(student_subject)

    grade.save()


@receiver(pre_save, sender=Grade)
def capture_old_average(sender, instance, **kwargs):
    """
    Get average of grade before it is updated
    """
    if instance.pk:
        instance._old_average = Grade.objects.get(pk=instance.pk).average
    else:
        instance._old_average = None

@receiver(post_save, sender=Grade)
def grade_average_updated(sender, instance, created, **kwargs):
    """
    Get average of grade after update
    Used to update position only when there is change in the averages
    """
    if not created and instance._old_average is not None and instance.average != instance._old_average:
        update_all_class_positions(instance.classroom, instance.term)


def update_all_class_positions(cls, term):
    """
    Update position of all grades in a class for a term
    """
    grades = Grade.objects.filter(classroom=cls, term=term).all()
    
    student_averages = defaultdict(list)

    for grade in grades:
        student_averages[grade.student_id] = grade.average

    sorted_students = sorted(student_averages.items(), key=lambda x: x[1], reverse=True)

    student_positions = {}
    for i, (student_id, _) in enumerate(sorted_students, start=1):
        student_positions[student_id] = i

    for grade in grades:
        grade.position = student_positions.get(grade.student_id, None)
        grade.save()

    print('position and grade updated', student_positions)
    return student_positions
    



# ////////////// DO NOT UNCOMMENT THIS. IT EXIST ALREADY IN SETTINGS ///////////////////////
# @receiver(post_save, sender=Student)
# def create_student_subjects(sender, instance, created, **kwargs):
#     if created:
#         # Get the student's class
#         student_class = instance.student_class

#         # Get all subjects associated with the student's class
#         subjects = student_class.subjects.all()

#         # Get all sequences
#         sequences = Sequence.objects.all()

#         # Create a StudentSubjects instance for each subject and sequence
#         for subject in subjects:
#             for sequence in sequences:
#                 StudentSubjects.objects.create(student=instance, subject=subject, sequence=sequence)


class ProgramView(APIView):
    serializer_class = ProgramSerializer

    def get(self, request):
        programs = Program.objects.filter(is_deleted=False)
        serializer = self.serializer_class(programs, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class ProgramItemView(APIView):
    serializer_class = ProgramSerializer
    def find_program_by_id(self, id):
        return Program.objects.filter(id=id, is_deleted = False).first()
    
    def get(self, request, id):
        program = self.find_program_by_id(id)
        serializer = self.serializer_class(program)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        program = self.find_program_by_id(id)

        if not program:
            return Response({"message": f"program with id {id} was not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if program.is_deleted:
            return Response({"message": f"Level with id {id} was already deleted"}, status=status.HTTP_406_NOT_ACCEPTABLE)
       
        program.is_deleted = True
        program.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, id):
        program = self.find_program_by_id(id)
        serializer = self.serializer_class(program, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id):
        program = self.find_program_by_id(id)
        serializer = self.serializer_class(program, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YearTermView(APIView):
    serializer_class = TermsSerializer

    def get(self, request):
        # Get active program
        active_program = Program.get_active_program()

        if not active_program:
            return Response({'message': 'You have no active program'}, status=status.HTTP_412_PRECONDITION_FAILED)
        
        # Get all program terms and return them
        terms = active_program.terms.all()

        #Get active term and add to the response
        active_term = Terms.get_active_term()

        serializer_all = self.serializer_class(terms, many=True)
        serializer_active = self.serializer_class(active_term)
        return Response({"terms":serializer_all.data, "active_term": serializer_active.data}, status=status.HTTP_200_OK)


class SocialAPIView(APIView):
    serializer_class = SocialSerializer
    def get(self, request):
        socials = Social.objects.all()
        serializer = self.serializer_class(socials, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentAPIView(APIView):
    serializer_class = PaymentDetailSerializer
    def get(self, request):
        payments = Payment.objects.all()
        serializer = self.serializer_class(payments, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SubscriptionAPIView(APIView):
    serializer_class = ProgramSubscriptionSerializer

    def create_subscription(self, request):
        return Subscription.objects.create(**request.data)
    
    def get(self, request):
        subscriptions = Program.objects.all()
        serializer = self.serializer_class(subscriptions, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        active_program = Program.get_active_program()

        if not active_program:
            return Response({'message': 'You have no active program'}, status=status.HTTP_412_PRECONDITION_FAILED)

        subscription = active_program.subscription
        
        if not subscription:
            try:
                subscription_response = self.create_subscription(request)
                active_program.subscription = subscription_response

            except Exception as error:
                return Response(error, status=status.HTTP_400_BAD_REQUEST)

        else:
            transaction_id = subscription.generate_transaction_id()
            subscription.transaction_id = transaction_id
            subscription.save()
        
        active_program.save()

        serializer = self.serializer_class(active_program)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class SchoolEventAPIView(APIView):
    serializer_class = EventSerializer
    def get(self, request):
        events = Event.objects.all()
        serializer = self.serializer_class(events, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SchoolEventUpdateAPIView(APIView):
    serializer_class = EventSerializer

    def get(self, request, id):
        event = Event.objects.filter(id=id).first()
        serializer = self.serializer_class(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, id):
        event = Event.objects.filter(id=id).first()
        if not event:
            return Response({"message": f"event with id {id} was not found"}, status=status.HTTP_404_NOT_FOUND)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, id):
        event = Event.objects.filter(id=id).first()
        if not event:
            return Response({"message": f"event with id {id} was not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassFeeView(APIView):
    serializer_class = ClassFeeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clss = ClassFees.objects.all()
        serializer = self.serializer_class(clss, many=True)
    
        return Response(serializer.data)
    
    def post(self, request):
        serializer = self.serializer_class(data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ClassFeeUpdateView(APIView):
    serializer_class = ClassFeeSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        class_fee = ClassFees.objects.filter(id=id).first()
        if not class_fee:
            return Response({"message": "Invalid request"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.serializer_class(class_fee, data = request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        class_fee = ClassFees.objects.filter(id=id).first()
        if not class_fee:
            return Response({"message": "Invalid request"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.serializer_class(class_fee)
        return Response(serializer.data)
        
    def delete(self, request, id):
        class_fee = ClassFees.objects.filter(id=id).first()
        if not class_fee:
            return Response({"message": "Invalid request"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        class_fee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
class SchoolUpdateView(APIView):
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]

    def find_school_by_id(self, id):
        try:
            return School.objects.get(id=id)
            
        except School.DoesNotExist:
            return Response({'error': 'School not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def get(self, request, id):
        school = self.find_school_by_id(id)
        serializers = self.serializer_class(school)
        return Response(serializers.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        school = self.find_school_by_id(id)

        serializers = self.serializer_class(school, data=request.data, partial=True)
        
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        school = self.find_school_by_id(id)
        return Response({"message": "Your request is being processed"}, status=status.HTTP_202_ACCEPTED)


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
    

# SCHOOL TERMS
class TermManagerAPIView(APIView):
    def post(self):
        pass


class TermAPIView(APIView):
    serializer_class = TermsSerializer

    def get(self, request):
        terms = Terms.objects.all()
        serializer = self.serializer_class(terms, many=True)

        active_term = Terms.get_active_term()
        active_term_data = None
        if active_term:
            active_term_serializer = self.serializer_class(active_term)
            active_term_data = active_term_serializer.data

        response_data = {
            "terms": serializer.data,
            "active_term": active_term_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    def create_school_program(self, start_date, end_date, terms):
        program = Program.objects.create(academic_start=start_date, academic_end=end_date)
        program.terms.set(terms)
        program.save()
        serializer = ProgramSerializer(program)
        return serializer.data

    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of terms"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            created_terms = []
            min_start_date = None
            max_end_date = None
            terms_list = []

            try:
                for term_data in request.data:
                    start_date = term_data.get('start_date')
                    end_date = term_data.get('end_date')

                    if not start_date or not end_date:
                        raise ValueError("Start date and end date are required")

                    try:
                        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValueError("Invalid date format. Use YYYY-MM-DD")

                    overlapping_terms = Terms.objects.filter(
                        Q(start_date__range=[start_date, end_date]) |
                        Q(end_date__range=[start_date, end_date]) |
                        Q(start_date__lte=start_date, end_date__gte=end_date)
                    )

                    if overlapping_terms.exists():
                        raise ValueError("Term overlaps with existing term")

                    school_id = term_data.pop('school', None)
                    if not school_id:
                        raise ValueError("School ID is required")

                    try:
                        school = School.objects.get(id=school_id)
                    except School.DoesNotExist:
                        raise ValueError(f"School with ID '{school_id}' does not exist")

                    if min_start_date is None or start_date < min_start_date:
                        min_start_date = start_date
                    if max_end_date is None or end_date > max_end_date:
                        max_end_date = end_date

                    term_data['school'] = school.id
                    serializer = self.serializer_class(data=term_data)
                    if serializer.is_valid():
                        term = serializer.save()
                        created_terms.append(serializer.data)
                        terms_list.append(term)
                    else:
                        raise ValueError(serializer.errors)

                if min_start_date and max_end_date:
                    year = self.create_school_program(min_start_date, max_end_date, terms_list)
                else:
                    year = None

            except ValueError as e:
                # Rollback the transaction and return the error message
                transaction.set_rollback(True)
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Rollback the transaction and return a generic error message
                transaction.set_rollback(True)
                return Response({"message": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"year": year, "terms": created_terms}, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        term = Terms.objects.get(pk=pk)
        serializer = self.serializer_class(term, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        term = Terms.objects.get(pk=pk)
        term.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



    
class ActiveTermView(APIView):
    def get(self, request):
        active_term = Terms.get_active_term()
        if active_term:
            data = {
                'id': active_term.id,
                'term_name': active_term.term_name,
                'start_date': active_term.start_date,
                'end_date': active_term.end_date
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'There is no active term.'}, status=status.HTTP_404_NOT_FOUND)
        

class SequenceView(APIView):
    serializer_class = SequenceSerializer
    def get(self, request):
        sequences = Sequence.objects.all()
        serializer = self.serializer_class(sequences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of sequence data"}, status=status.HTTP_400_BAD_REQUEST)
        

        serializers = []
        
        for sequence in request.data:
            serializer = self.serializer_class(data=sequence)

            if serializer.is_valid():
                serializer.save()
                serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response([serializer.data for serializer in serializers], status=status.HTTP_201_CREATED)
    

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
    
    def find_department_by_id(self, id):
        return Department.objects.filter(id=id).first()
    
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of class data"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializers = []
        for level in request.data:
            department = level.get('departments') 
            department_id = self.find_department_by_id(department)

            if not department_id:
                return Response({"message": "Invalid department for level"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.serializer_class(data=level)
            if serializer.is_valid():
                serializer.save()
                serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response([serializer.data for serializer in serializers], status=status.HTTP_201_CREATED)
    
        
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

    def find_level_by_id(self, id):
        return Level.objects.filter(id=id).first()
    
    def get(self, request):
        classes = Class.objects.all()
        serializers = ClassFetchSerializer(classes, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


    def post(self, request):

        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of class data"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializers = []
        for class_data in request.data:
            level = class_data.get('level') 
            level_id = self.find_level_by_id(level)
            if not level_id:
                return Response({"message": "Invalid level"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.serializer_class(data=class_data)

            if serializer.is_valid():
                serializer.save()
                serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response([serializer.data for serializer in serializers], status=status.HTTP_201_CREATED)


class UpdateClassView(APIView):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    def find_class_by_id(self, id):
        return Class.objects.filter(id=id).first()
    
    def get(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        serializers = ClassSerializer(cls)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def put(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializers = self.serializer_class(cls, data=request.data, partial=True)

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
    
    

class ClassInstructor(APIView):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    def find_class_by_id(self, id):
        return Class.objects.filter(id=id).first()
    
    def find_staff_by_id(self, id):
        return Staff.objects.filter(id=id).first()
    
    def patch(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        staff_id = request.data.get('instructor')
        staff = self.find_staff_by_id(staff_id)

        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        cls.instructor = staff
        cls.save()
        serializers = ClassSerializer(cls)

        return Response(serializers.data, status=status.HTTP_202_ACCEPTED)



class ClassItemView(APIView):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]

    def find_class_by_id(self, id):
            return Class.objects.filter(id=id).first()

    def get(self, request, class_id):
        cls = self.find_class_by_id(class_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        serializers = ClassItemSerializer(cls)
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
    
    def send_invite_mail(self, data, tenant):
        context = {
            'data': data,
            'school': tenant,
            'code': data['invitation_code'],
            'role': data['role']
        }
        sub={
            'email_subject': 'You have been invited to join our school',
        }
        send_email_with_template.delay( sub, 'staff_invite.html', context, recipient_list=[data['recipient_email']] )
    
    def send_whatsapp_message(self, data, tenant):
        context = {
            'data': data,
            'school': tenant,
            'code': data['invitation_code'],
            'role': data['role']
        }
    
        code = data['invitation_code']
        url = f"https://rankafrica.net/wa-link/accept?school={tenant}&code={code}"
        message= 'You have been invited to join our school. Click on the link to accept the invitation. ' + url
        
        send_whatsapp_message_with_api.delay( message,  recipient_list=[data['recipient_phone']] )


    def get(self, request):
        invitations = Invitation.objects.filter(is_deleted=False)
        serializer = self.serializer_class(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of Invitations"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializers = []

        for invitation in request.data:
            serializer = self.serializer_class(data=invitation)
            if serializer.is_valid():
                serializer.save()
                self.send_invite_mail(serializer.data, request.tenant.schema_name)
                serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        return Response([serializer.data for serializer in serializers], status=status.HTTP_201_CREATED)
        

    

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
        if not invitation:
            return Response({"message": "Not a valid invitation"}, status=status.HTTP_400_BAD_REQUEST)
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
            email = request.data.get('email')
            user_exist = User.objects.filter(email=email).first()

            if user_exist:
                return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
            

            user = User.objects.create_user(**request.data)
            self.assign_user_to_group(user, invite_role)
            staff_created = self.create_staff_membership(user, invite_role)
            self.accept_invitation(invite_id)

            if staff_created:
                user_serializer = LoginSerializer(user)
                return Response( user_serializer.data,  status=status.HTTP_201_CREATED)

        except Exception as error:
            print(error)
            return Response( status=status.HTTP_400_BAD_REQUEST)
        
        return Response("Returning something")


class TeachersView(APIView):
    serializer_class = StaffSerializer
    def get(self, request):
        teachers = Staff.objects.filter(role='teacher', is_deleted=False)
        serializer = self.serializer_class(teachers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
       

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
            return Response({"school_id": "Invalid school ID"}, status=status.HTTP_400_BAD_REQUEST)

        compressed_school_id = self.compress_uuid(school_id)

        if compressed_school_id != school_code:
            return Response({"school_id": "This code is not recognized with associated school."}, status=status.HTTP_400_BAD_REQUEST)
        
        return compressed_school_id
    
    def get(self, request, school_id):
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


class ApplicationReaction(APIView):
    serializer_class = SchoolStaffApplySerializer
    
    def get_application_by_id(self, id):
        application = SchoolStaffApply.objects.filter(id=id).first()
        return application
    
    def get(self, request, school_id, id):
        application = self.get_application_by_id(id)
        serializer = self.serializer_class(application)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, school_id, id):
        application = self.get_application_by_id(id)
        if not application:
            return Response({"message": "Invalid application with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializers = self.serializer_class(application, data=request.data, partial=True)

        if serializers.is_valid():
            serializers.save()
            # TODO: Send confirmation EMAIL
            # SEND POST WITH ACCEPT = TRUE AND TENANT
            return Response(serializers.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, school_id, id):
        application = self.get_application_by_id(id)
        if not application:
            return Response({"message": "No Appliation with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class DeactivateStaff(APIView):
    serializer_class = StaffSerializer
    def get_staff_by_id(self, id):
        staff = Staff.objects.filter(id=id).first()
        return staff
    
    def patch(self, request, id):
        staff = self.get_staff_by_id(id)
        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        staff.user.is_active = False
        staff.user.save()
        staff.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class StaffView(APIView):
    serializer_class = StaffSerializer

    def create_staff_membership(self, user, role):
        staff = Staff.objects.create(user=user, role=role)
        return staff
    
    def assign_user_to_group(self, user, role):
        try:
            group = Group.objects.get(name__iexact=role)
            group.user_set.add(user)
        except Group.DoesNotExist:
            raise ValueError("This is not a valid user role in your school")
        
    def get(self, request):
        teachers = Staff.objects.filter(is_deleted=False)
        serializer = self.serializer_class(teachers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def send_registration_mail(self, user, role, tenant):
        context = {
            'user': user,
            'role': role,
            'tenant': tenant
        }
        send_email_with_template.delay(
            data={
                'email_subject': 'Your account has been created successfully',
            },
            template_name='staff_registration.html',
            context=context,
            recipient_list=[user['email']]
        )

    def send_password_email(self, user, role, password):
        context = {
            'user': user,
            'role': role,
            'password': password
        }
        send_email_with_template.delay(
            data={
                'email_subject': '[IMPORTANT] your account password',
            },
            template_name='staff_password.html',
            context=context,
            recipient_list=[user['email']]
        )

    def generate_random_password(self, length=8):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

    def post(self, request):
        
        with transaction.atomic():
            try:
                staff_role = request.data.get('role')
                email = request.data.get('email')
                user_exist = User.objects.filter(email=email).first()
                
                if user_exist:
                    return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
                
                if not staff_role:
                    return Response({"message": "You must provide a staff role"}, status=status.HTTP_400_BAD_REQUEST)
                
                password = request.data.get('password') or self.generate_random_password()
                user_data = request.data.copy()
                user_data['password'] = password
                user_data['is_active'] = True

                user = User.objects.create_user(**user_data)
                print('generated password is: ', password)

                if not user:
                    return Response( {"message": "Unable to create user. Please fill details correctly"},  status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    self.assign_user_to_group(user, staff_role)
                except ValueError as error:
                    user.delete() 
                    return Response({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)

                staff_created = self.create_staff_membership(user, staff_role)
                
                if staff_created:
                    user_serializer = LoginSerializer(user)

                    tenant = request.tenant.schema_name
                    self.send_registration_mail(user_serializer.data, staff_role, tenant)
                    self.send_password_email(user_serializer.data, staff_role, password)

                    return Response( user_serializer.data,  status=status.HTTP_201_CREATED)
                return Response( "error creating staff",  status=status.HTTP_400_BAD_REQUEST)

            except Exception as error:
                print(f"Error occurred: {error}")
                return Response({"message": "An error occurred while processing your request", "error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
 

class StaffItemView(APIView):
    serializer_class = StaffSerializer
    def get(self, request, staff_id):
        staff = Staff.objects.filter(id=staff_id).first()
        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(staff)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, staff_id):
        staff = Staff.objects.filter(id=staff_id).first()
        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, staff_id):
        staff = Staff.objects.filter(id=staff_id).first()
        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class StaffChangeRole(APIView):
    serializer_class = LoginSerializer
    def find_staff_by_id(self, id):
        staff = Staff.objects.filter(id=id).first()
        return staff

    def send_change_role_email(self, user, role):
        user.role = role
        user.save()
        user = self.serializer_class(user).data

        context = {
            'user': user,
            'role': role
        }
        send_email_with_template.delay(
            data={
                'email_subject': 'Your role has been changed successfully',
            },
            template_name='staff_role_change.html',
            context=context,
            recipient_list=[user['email']]
        )
    
    def send_promotion_email(self, user, role):
        user.role = role
        user.save()
        user = self.serializer_class(user).data
        context = {
            'user': user,
            'role': role
        }
        send_email_with_template.delay(
            data={
                'email_subject': 'Congratulations! You have been promoted',
            },
            template_name='staff_promotion.html',
            context=context,
            recipient_list=[user['email']]
        )

    def change_user_role(self, user, role):
        user.groups.clear()
        group = Group.objects.get(name__iexact=role)
        if group:
            return group.user_set.add(user)
        
    def add_user_role(self, user, role):
        group = Group.objects.get(name__iexact=role)
        if group:
            return group.user_set.add(user)
        
    def patch(self, request, staff_id):
        """----- CHANGE USER ROLE (REMOVE OLD ROLE) -----"""
        role = request.data.get('role')
        staff = self.find_staff_by_id(staff_id)
        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        if not role:
            return Response({"message": "You need to assign the new role"}, status=status.HTTP_404_NOT_FOUND)
        
        self.change_user_role(staff.user, role)
        staff.role = role
        self.send_change_role_email(staff.user, role)

        serializer = StaffSerializer(staff)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def put(self, request, staff_id):
        """----- ADD USER TO NEW GROUP(PROMOTE WITHOUT REMOVING OLD ROLE) -----"""
        role = request.data.get('role')
        staff = self.find_staff_by_id(staff_id)
        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        if not role:
            return Response({"message": "You need to assign the new role"}, status=status.HTTP_404_NOT_FOUND)
        
        self.add_user_role(staff.user, role)
        self.send_promotion_email(staff.user, role)
        staff.role = role
        
        serializer = StaffSerializer(staff)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)



class SubjectLevelView(APIView):
    serializer_class = SubjectSerializer
    def find_class_by_id(self, cls_id):
        cls = Class.objects.filter(id=cls_id).first()
        return cls
    
    def get_subjects_in_class(self, cls):
        subjects = Subject.objects.filter(cls=cls)
        return subjects
    
    def get(self, request, cls_id):
        cls = self.find_class_by_id(cls_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND) 
        
        subjects = self.get_subjects_in_class(cls)
        serializer = SubjectRequestSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, cls_id):
        
        cls = self.find_class_by_id(cls_id)
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of terms"}, status=status.HTTP_400_BAD_REQUEST)
    
        subjects_created = []
        for data in request.data:
            lvl_id = data.get('level')
            instructor_id = data.get('instructor')

            instructor = Staff.objects.filter(id=instructor_id).first()
            level = Level.objects.filter(id=lvl_id).first()

            if not instructor or not level:
                return Response({"message": "Invalid subject request, please verify instructor or level"}, status=status.HTTP_403_FORBIDDEN)
        
            data['instructor'] = instructor
            data['level'] = level
            data['cls'] = cls_id
            serializer = self.serializer_class(data=data)

            if serializer.is_valid():
                serializer.save()
                subjects_created.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(subjects_created, status=status.HTTP_201_CREATED)
           
        

class SubjectChangeInstructor(APIView):     
    def get_subject_by_id(self, id):
        return Subject.objects.filter(id=id).first()
    
    def get_staff_by_id(self, id):
        return Staff.objects.filter(id=id).first()
    
    def patch(self, request, subject_id):
        subject = self.get_subject_by_id(subject_id)
        if not subject:
            return Response({"message": "No subject with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        staff_id = request.data.get('instructor')
        staff = self.get_staff_by_id(staff_id)
        if not staff:
            return Response({"message": "No staff with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        subject.instructor = staff
        subject.save()
        serializer = SubjectSerializer(subject)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)




class StudentsView(APIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def generate_random_password(self):
        return User.objects.make_random_password()
    
    def generate_unique_student_email(self, request):
        prefix = 'student'
        suffix = ''.join(random.choices(string.digits, k=4))
        tenant = request.tenant.schema_name
        return f"{prefix}{suffix}@{tenant}.com"
    
    def assign_user_to_group(self, user, role):
        group = Group.objects.get(name__iexact=role)
        if group:
            return group.user_set.add(user)

    def get(self, request):
        students = Student.objects.all()
        serializer = self.serializer_class(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create_user_with_role(self, data, role, student_email):
        generated_password = self.generate_random_password()
        
        # Remove unwanted fields from request data
        data.pop('status', None)
        data.pop('student_class', None)
        data.pop('department', None)

        # Add email and password to data
        data['email'] = student_email
        data['password'] = generated_password

        user = User.objects.create_user(**data)
        self.assign_user_to_group(user, role)
        return user
    
    def get_class_by_id(self, id):
        return Class.objects.filter(id=id).first()
    
    def post(self, request):
        req = copy.deepcopy(request.data)

        student_email = self.generate_unique_student_email(request)
        user = self.create_user_with_role(req, "student", student_email)
        
        cls_id = request.data.get('student_class')
        
        student_class = self.get_class_by_id(cls_id)

        if not student_class:
            return Response({"message": "Invalid student level"}, status=status.HTTP_400_BAD_REQUEST)

        request.data.pop('password', None)
        request.data.pop('email', None)
        request.data.pop('date_of_birth', None)
        request.data.pop('bio', None)
        request.data.pop('first_name', None)
        request.data.pop('last_name', None)
        request.data.pop('gender', None)
        request.data.pop('student_level', None)
        request.data['student_class'] = student_class

        student = Student(user=user, **request.data)
        student.save(request=request)
        serializer = self.serializer_class(student)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentStatsView(APIView):
    def get(self, request):
        # Count male and female students
        male_students = Student.objects.filter(user__gender='male').count()
        female_students = Student.objects.filter(user__gender='female').count()
        active_program = Program.get_active_program()
        # Count students in each class
        students_in_classes = Class.objects.annotate(num_students=Count('students'))

        class_counts = {
            class_obj.level.name + " " + class_obj.class_name: {
                'class_id': class_obj.id,
                'student_count': class_obj.num_students
            }
            for class_obj in students_in_classes
        }

        partial_registrations = Registration.objects.filter(year=active_program.id, registration_status__in=[
            FeeInstallments.First, FeeInstallments.Second
        ]).count()
        complete_registrations = Registration.objects.filter(registration_status=FeeInstallments.Complete).count()
        not_registered = Student.objects.filter(registration__isnull=True).count()


        data = {
            'male_students': male_students,
            'female_students': female_students,
            'students_in_classes': class_counts,
            'registrations': {
                'partial': partial_registrations,
                'complete': complete_registrations,
                'not_registered': not_registered,
            }
        }

        return Response(data, status=status.HTTP_200_OK)
    
    
class StudentView(APIView):
    serializer_class = StudentSerializer
    def get(self, request, stud_id):
        student = Student.objects.filter(id=stud_id)
        serializer = self.serializer_class(student, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentsInClassView(APIView):
    serializer_class = StudentSerializer
    def get_students_in_class(self, cls_id):
        students = Student.objects.filter(student_class=cls_id)
        return students
    
    def get(self, request, cls_id):
        students = self.get_students_in_class(cls_id)
        serializer = self.serializer_class(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, cls_id):
        pass


class StudentsSubjectsView(APIView):
    serializer_class = StudentSubjectForStudentSerializer
    
    def get(self, request, stud_id):
        """--- GET STUDENT SUBJECTS ---"""
        student = Student.objects.filter(id=stud_id).first()
        if not student:
            return Response({"message": "No student with provided ID"}, status=status.HTTP_404_NOT_FOUND)
        
        subjects = StudentSubjects.objects.filter(student=student)
        serializer = self.serializer_class(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  


class GuardiansView(APIView):
    serializer_class = GuardianSerializer
    
    def get(self, request):
        guardians = Guardian.objects.all()
        serializer = self.serializer_class(guardians, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def generate_random_password(self):
        return User.objects.make_random_password()
    
    def generate_unique_email(self):
        prefix = 'parent'
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}@rankafrica.net"
    

    def assign_user_to_group(self, user, role):
        group = Group.objects.get(name__iexact=role)
        if group:
            return group.user_set.add(user)
        
    def create_user_with_role(self, data, role, generated_email):
        generated_password = self.generate_random_password()
        
        data.pop('type', None)
        data.pop('student', None)
        alt_mail = data.pop('alt_mail', None)
        
        user_exist = User.objects.filter(email=alt_mail).first()
        if user_exist:
            return user_exist
        


        data['email'] = alt_mail if len(alt_mail) > 0 else generated_email
        data['password'] = generated_password

        user = User.objects.create_user(**data)
        self.assign_user_to_group(user, role)
        return user
    

    def find_guardian_by_email(self, email):
        return Guardian.objects.filter(alt_mail=email).first()
    
    def post(self, request):

        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of terms"}, status=status.HTTP_400_BAD_REQUEST)
        
        guardians_data = request.data
        created_guardians = []

        for guardian_data in guardians_data:
            email = guardian_data.get('alt_mail')
            user_exist = self.find_guardian_by_email(email)

            if not user_exist:
                req = copy.deepcopy(guardian_data)
                generated_email = self.generate_unique_email()
                user = self.create_user_with_role(req, "guardian", generated_email)
            else:
                user = User.objects.filter(email=user_exist.user.email).first()

            student_id = guardian_data.get('student')
            student = Student.objects.filter(id=student_id).first()

            if not student:
                return Response({"message": "Student not found"}, status=status.HTTP_400_BAD_REQUEST)

            if not user:
                return Response({'message': 'No user found'}, status=status.HTTP_400_BAD_REQUEST)

            guardian_data.pop('phone', None)
            guardian_data.pop('first_name', None)
            guardian_data.pop('last_name', None)
            guardian_data.pop('student', None)

            guardian = None

            if not user_exist:
                guardian = Guardian.objects.create(user=user, **guardian_data)
                guardian.student.set([student])
           
            else:
                guardian = Guardian.objects.filter(alt_mail=email).first()
                students = list(guardian.student.all())
                students.append(student)
                guardian.student.set(students)

            guardian.save()
            created_guardians.append(guardian)

        serializer = self.serializer_class(created_guardians, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GuardianDetail(APIView):
    serializer_class = GuardianItemSerializer
    
    def get_object(self, id):
        return get_object_or_404(Guardian, id=id)
    
    def get(self, request, id):
        guardian = self.get_object(id)
        serializer = self.serializer_class(guardian)
        return Response( serializer.data , status=status.HTTP_200_OK)
    
    def put(self, request, id):
        guardian = self.get_object(id)
        serializer = self.serializer_class(guardian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        guardian = self.get_object(id)
        guardian.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# TEACHER GRADE API
class GradeStudentView(APIView):
    """ ----- GRADE ALL STUDENTS FOR A PARTCULAR COURSE ----- """

    serializer_class = StudentSubjectSerializer

    def get(self, request, subj_id):
        subject_subjects = StudentSubjects.objects.filter(subject=subj_id)
        
        serializer = self.serializer_class(subject_subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  
    def post(self, request, subj_id):
        marks_data = request.data
        updated_grades = {}
        invalid_students = []

        subject = Subject.objects.filter(id=subj_id).first()
        if not subject:
            return Response({"message": "Invalid subject"}, status=status.HTTP_400_BAD_REQUEST)
        
        active_term = Terms.get_active_term()
        if not active_term:
            return Response({"message": "No active term found"}, status=status.HTTP_404_NOT_FOUND)
        
        for data in marks_data:
            student_id = data.get('student')
            sequence_id = data.get('sequence')
            try:
                student_grade = StudentSubjects.objects.get(subject=subj_id, student=student_id, sequence=sequence_id)
                serializer = self.serializer_class(instance=student_grade, data=data, partial=True)
                
                if serializer.is_valid():
                    serializer.save()
                    updated_grades[student_id] = serializer.data
                
                else:
                    invalid_students.append({"student": student_id, "errors": serializer.errors})
            
            except StudentSubjects.DoesNotExist:
                invalid_students.append({"student": student_id, "message": f"Student {student_id} not found for the given subject in the active term"})

        if invalid_students:
            return Response({"invalid_students": invalid_students, "graded": updated_grades}, status=status.HTTP_400_BAD_REQUEST)
       
        else:
            return Response({"updated_grades": updated_grades}, status=status.HTTP_201_CREATED)

# GRADE API
class GradeStudentForSubjectAPIView(APIView):
    """--- GRADE STUDENTS FOR A PARTICULAR TERM ---"""
    serializer_class = GradeSerializer
    
    def calculate_adjusted_student_average(self, grade_data):
        subject_grades = {}
        
        # Accumulate all grades by subject and sequence
        for grade_item in grade_data["grade_list"]:
            subject_id = grade_item["subject"]["id"]
            if subject_id not in subject_grades:
                subject_grades[subject_id] = {
                    "total": 0.0,
                    "count": 0,
                    "coefficient": grade_item["subject"]["sub_coef"]
                }
            
            subject_grades[subject_id]["total"] += grade_item["grade"]
            subject_grades[subject_id]["count"] += 1

        # Compute the weighted average for each subject and aggregate
        weighted_sum = 0
        coefficient_sum = 0
        for subject_id, details in subject_grades.items():
            if details["count"] > 0:
                subject_average = details["total"] / details["count"]
                weighted_average = subject_average * details["coefficient"]
                weighted_sum += weighted_average
                coefficient_sum += details["coefficient"]

        # Calculate the final average normalized to a scale of 20
        if coefficient_sum > 0:
            final_average = (weighted_sum / coefficient_sum) 

        else:
            final_average = 0

        result = {"avg": final_average, "total": weighted_sum, "coef": coefficient_sum}
        return result
    
    def post(self, request, term_id, subject_id):
        term = Terms.objects.filter(id=term_id).first()

        if not term:
            return Response({"message": "term not found"}, status=status.HTTP_400_BAD_REQUEST)

        # CHECK IF TERM IS VALIDATED OR END DATE LESS THAN TODAY
        # if not term.term_validated and datetime.now().date() < term.end_date:
        #     return Response({"message": "You can not grade a future term "}, status=status.HTTP_400_BAD_REQUEST)
        
        subject = Subject.objects.filter(id=subject_id).first()
        if not term or not subject:
            return Response({"message": "Invalid term or subject"}, status=status.HTTP_400_BAD_REQUEST)
        
        marks_data = request.data
        updated_grades = []
        invalid_students = []

        for data in marks_data:
            student_id = data.get('student')
            sub_id = data.get('subject')
            sequence = data.get('sequence')
            student = Student.objects.filter(id=student_id).first()
            try:
                student_grade = StudentSubjects.objects.filter(subject=sub_id, student=student_id, sequence=sequence).first()
                serializer = StudentSubjectSerializer(instance=student_grade, data=data, partial=True)
         
                if serializer.is_valid():
                    serializer.save()
                    updated_grades.append( serializer.data )
                
                else:
                    invalid_students.append({"student": student_id, "errors": serializer.errors})
            
            except StudentSubjects.DoesNotExist:
                invalid_students.append({"student": student_id, "message": f"Student {student_id} not found for the given subject in the active term"})

            grade = Grade.objects.filter(classroom=student.student_class.id, student=student_id, term=term).first()

            if not grade:
                return Response({"message": "Grades not found"}, status=status.HTTP_404_NOT_FOUND)
        
            grade_data = self.serializer_class(grade)
            response = self.calculate_adjusted_student_average(grade_data.data)
        
            grade.average = response['avg']
            grade.save()

        if invalid_students:
            return Response({"invalid_students": invalid_students, "graded": updated_grades}, status=status.HTTP_206_PARTIAL_CONTENT)
       
        else:
            return Response({"updated_grades": updated_grades}, status=status.HTTP_201_CREATED)


class GradeStudentForAllSubjectAPIView(APIView):
    """ --- GRADE STUDENT FOR ALL SUBJECTS IN A PARTICULAR TERM --- """
    
    serializer_class = GradeSerializer

    def calculate_adjusted_student_average(self, grade_data):
        subject_grades = {}
        
        # Accumulate all grades by subject and sequence
        for grade_item in grade_data["grade_list"]:
            subject_id = grade_item["subject"]["id"]
            if subject_id not in subject_grades:
                subject_grades[subject_id] = {
                    "total": 0.0,
                    "count": 0,
                    "coefficient": grade_item["subject"]["sub_coef"]
                }
            
            subject_grades[subject_id]["total"] += grade_item["grade"]
            subject_grades[subject_id]["count"] += 1

        # Compute the weighted average for each subject and aggregate
        weighted_sum = 0
        coefficient_sum = 0
        for subject_id, details in subject_grades.items():
            if details["count"] > 0:
                subject_average = details["total"] / details["count"]
                weighted_average = subject_average * details["coefficient"]
                weighted_sum += weighted_average
                coefficient_sum += details["coefficient"]

        # Calculate the final average normalized to a scale of 20
        if coefficient_sum > 0:
            final_average = (weighted_sum / coefficient_sum) 

        else:
            final_average = 0

        result = {"avg": final_average, "total": weighted_sum, "coef": coefficient_sum}
        return result

    def get(self, request, cls_id, student_id):
        term = request.GET.get('term')

        if not term:
            return Response({"message": "Please provide the term in the query '?term=term'"}, status=status.HTTP_400_BAD_REQUEST)
        
        student_marks = Grade.objects.filter(classroom=cls_id, student=student_id, term=term).first()

        if not student_marks:
            return Response({"message": "There is a mix up in your request"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(student_marks)
        
        response = self.calculate_adjusted_student_average(serializer.data)

        student_marks.average = response['avg']
        student_marks.save()

        return Response({'grade': serializer.data, **response}, status=status.HTTP_200_OK)
    

    def post(self, request, cls_id, student_id):
        cls = Class.objects.filter(id=cls_id).first()
        term = request.GET.get('term')

        if not cls:
            return Response({"message": "Class not found"}, status=status.HTTP_400_BAD_REQUEST)

        if not term:
            return Response({"message": "Please provide the term in the query '?term=term'"}, status=status.HTTP_400_BAD_REQUEST)
        
        marks_data = request.data
        updated_grades = {}
        invalid_subjects = []

        for data in marks_data:
            stud_id = data.get('student')
            subject_id = data.get('subject')
            sequence = data.get('sequence')

            try:
                student_grade = StudentSubjects.objects.get(sequence=sequence, student=stud_id, subject=subject_id)
                serializer = StudentSubjectSerializer(instance=student_grade, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    updated_grades[subject_id] = serializer.data

                else:
                    invalid_subjects.append({"subject": subject_id, "errors": serializer.errors})

            except StudentSubjects.DoesNotExist:
                invalid_subjects.append({"subject": subject_id, "message": f"Student {stud_id} not found for the given subject and term"})

        grade = Grade.objects.filter(classroom=cls_id, student=student_id, term=term).first()

        if not grade:
            return Response({"message": "Grades not found"}, status=status.HTTP_404_NOT_FOUND)
        
        grade_data = self.serializer_class(grade)
        
        response = self.calculate_adjusted_student_average(grade_data.data)
        grade.average = response['avg']
        grade.save()

        if invalid_subjects:
            return Response({"invalid_subjects": invalid_subjects, "updated_grades": updated_grades}, status=status.HTTP_206_PARTIAL_CONTENT)
        
        else:
            return Response({"updated_grades": updated_grades}, status=status.HTTP_201_CREATED)
        


class TeacherSubjectsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, term_id):
        try:
            term = Terms.objects.filter(id=term_id).first()
            if not term:
                return Response({"message": "No term with provided ID"}, status=status.HTTP_400_BAD_REQUEST)

            user_id = request.user.id

            teacher = Staff.objects.filter(user=user_id).first()
            if not teacher:
                return Response({"message": "No teacher with provided ID"}, status=status.HTTP_400_BAD_REQUEST)

            subjects = Subject.objects.filter(instructor=teacher)

            subject_data = []

            for subject in subjects:
                # Aggregate the total and non-zero grades for the subject in the given term
                aggregates = StudentSubjects.objects.filter(
                    subject=subject, sequence__term=term
                ).aggregate(
                    total_grades=Count('grade'),
                    non_zero_grades=Count('grade', filter=Q(grade__gt=0))
                )

                total_grades = aggregates['total_grades']
                non_zero_grades = aggregates['non_zero_grades']

                print(non_zero_grades)
                print(total_grades)
                # Calculate the percentage of non-zero grades
                non_zero_percentage = (non_zero_grades / total_grades * 100) if total_grades > 0 else 0

                # Serialize the subject data and include the non-zero grade percentage
                serialized_subject = MySubjectSerializer(subject).data
                serialized_subject['non_zero_grade_percentage'] = non_zero_percentage
                subject_data.append(serialized_subject)

            return Response(subject_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "An error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TeacherTimeTableAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        teacher = Staff.objects.filter(user=user_id).first()
        if not teacher:
            return Response({"message": "No teacher with provided ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        term = Terms.get_active_term()
        if not term:
            return Response({"message": "No active term found"}, status=status.HTTP_404_NOT_FOUND)
        
        timetable = Timetable.objects.filter(subject__instructor=teacher, term=term)
      
        serializer = TeacherTimetableSerializer(timetable, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class StudentResultsView(APIView):
    def get(self, request):
        term = request.GET.get('term')
        student = request.GET.get('student')
        cls = request.GET.get('class')

        if not term or not student or not cls:
            return Response({"message": "Term, student, and class parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

        sequences = Sequence.objects.filter(term=term)
        if not sequences.exists():
            return Response({"message": "Unable to find sequences for the given term"}, status=status.HTTP_404_NOT_FOUND)
        
        sequence_list = SequenceSerializer(sequences, many=True).data

        student_grade = Grade.objects.filter(classroom=cls, student=student, term=term).first()
        
        if not student_grade:
            return Response({"message": "Unable to find grades for the given student and class"}, status=status.HTTP_404_NOT_FOUND)

        grades = student_grade.grade_list.filter(sequence__in=sequences).order_by('sequence__id')
        if not grades.exists():
            return Response({"message": "No grades found for the specified sequences"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSubjectsSerializer(grades, many=True)
        data = serializer.data

        subject_data = defaultdict(list)
        for entry in data:
            subject = entry["subject"]["name"]
            sequence = entry["sequence"]
            sequences = {
                "id": entry["sequence"],
                "sequence": entry
            }
            subject_data[subject].append(sequences)
        

        return Response({"sequences": sequence_list, "grades": subject_data}, status=status.HTTP_200_OK)




class SubjectResultsView(APIView):
    def get(self, request):
        term = request.GET.get('term')
        subject_id = request.GET.get('subject')
        cls = request.GET.get('class')

        if not term or not subject_id or not cls:
            return Response({"message": "Term, subject, and class parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

        sequences = Sequence.objects.filter(term=term)
        if not sequences.exists():
            return Response({"message": "Unable to find sequences for the given term"}, status=status.HTTP_404_NOT_FOUND)
        
        sequence_list = SequenceSerializer(sequences, many=True).data

        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"message": f"Subject with ID '{subject_id}' does not exist"}, status=status.HTTP_404_NOT_FOUND)

        grades = Grade.objects.filter(classroom=cls, term=term)
        if not grades.exists():
            return Response({"message": "No grades found for the specified subject, class, and term"}, status=status.HTTP_404_NOT_FOUND)

        subject_data = defaultdict(list)
        for grade in grades:
            filtered_grades = grade.grade_list.filter(subject=subject).order_by('sequence__id')
            if filtered_grades.exists():
                for entry in filtered_grades:
                    student = grade.student
                    subject_data[student.get_full_name()].append({
                        "sequence": entry.sequence.name,
                        "sequence_id": entry.sequence.id,
                        "grade": StudentSubjectsSerializer(entry).data
                    })

        if not subject_data:
            return Response({"message": "No grades found for the specified subject in the given term and class"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"sequences": sequence_list, "grades": subject_data}, status=status.HTTP_200_OK)
        return Response('{"sequences": sequence_list, "grades": student_data}', status=status.HTTP_200_OK)
    


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
    


# class SchoolProgramAPIView(APIView):


# class


class TimeTableFetchView(APIView):
    serializer_class = TimetableFetchSerializer

    def get(self, request, cls_id, term_id):
        term = Terms.objects.filter(id=term_id).first()
        cls = Class.objects.filter(id=cls_id).first()
        if not term:
            return Response({"message": "No term with provided ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not cls:
            return Response({"message": "No class with provided ID"}, status=status.HTTP_400_BAD_REQUEST)

        timetable = Timetable.objects.filter(class_instance=cls, term=term)
        serializer = self.serializer_class(timetable, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TimeTableView(APIView):
    serializer_class = TimetableSerializer

    def get(self, request):
        timetable = Timetable.objects.all()
        serializer = self.serializer_class(timetable, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"message": "Request data should be a list of terms"}, status=status.HTTP_400_BAD_REQUEST)

        timetable_data = request.data
        created_timetable = []
        errors = []

        with transaction.atomic():
            for time_info in timetable_data:
                subject_id = time_info.pop('subject', None)
                cls_id = time_info.pop('class', None)
                term_id = time_info.pop('term', None)

                subject = Subject.objects.filter(id=subject_id).first()
                cls = Class.objects.filter(id=cls_id).first()
                term = Terms.objects.filter(id=term_id).first()

                if not subject:
                    errors.append({"message": f"Invalid subject with id {subject_id}"})
                    continue

                if not cls:
                    errors.append({"message": f"Invalid class with id {cls_id}"})
                    continue

                if not term:
                    errors.append({"message": f"Invalid term with id {term_id}"})
                    continue

                instructor = subject.instructor

                existing_schedules = Timetable.objects.filter(
                    subject__instructor=instructor,
                    day=time_info['day'],
                    startTime__lt=time_info['endTime'],
                    endTime__gt=time_info['startTime']
                ).exists()

                if existing_schedules:
                    errors.append({"message": "The instructor already has a class scheduled during this time."})
                    continue

                overlapping_timetables = Timetable.objects.filter(
                    class_instance=cls,
                    term=term,
                    day=time_info['day'],
                    startTime__lt=time_info['endTime'],
                    endTime__gt=time_info['startTime']
                ).exists()

                if overlapping_timetables:
                    errors.append({
                        "message": f"Overlapping timetable entry exists for class {cls_id} on {time_info['day']} "
                                   f"from {time_info['startTime']} to {time_info['endTime']} during term {term_id}."
                    })
                    continue

                time_info['class_instance'] = cls.id 
                time_info['term'] = term.id 
                time_info['subject'] = subject.id  

                serializer = self.serializer_class(data=time_info)

                if serializer.is_valid():
                    serializer.save()
                    created_timetable.append(serializer.data)
                else:
                    errors.append(serializer.errors)

            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(created_timetable, status=status.HTTP_201_CREATED)

class TimetableUpdateAPIView(APIView):
    serializer_class = TimetableSerializer
    
    def find_timetable_by_id(self, id):
        return Timetable.objects.filter(id=id).first()
        
    def get(self, request, id):
        timetable = self.find_timetable_by_id(id)

        if not timetable:
            return Response({"message": "Timetable item not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(timetable)
        return Response(serializer.data)
    
    def delete(self, request, id):
        timetable = self.find_timetable_by_id(id)

        if not timetable:
            return Response({"message": "Timetable item not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        timetable.delete()
        return Response({"message": "Timetable entry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):
        timetable = self.find_timetable_by_id(id)

        if not timetable:
            return Response({"message": "Timetable item not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(timetable, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def generate_pdf(request):
    return PDFTemplateResponse(request=request,
            template='results/template_one.html',
            context={'students': "Nji kimbi darlington"},
            filename='report_card.pdf')



@api_view(['GET'])
def download_student_result(request, stud_id):
    student_grades = StudentSubjects.objects.filter(student=stud_id)
    
    return PDFTemplateResponse(request=request,
            template='results/template-one.html',
            context={'grades':student_grades, 'student': student_grades[0].student},
            filename='report_card.pdf')
    # print(student_grades)
    # return Response({"hello"})

class RegisterStudentAPIView(APIView):
    serializer_class = StudentRegistrationSerializer

    def get(self, request, stud_id):
        student = Student.objects.filter(id=stud_id).first()
        if not student:
            return Response({"message": "No student found"}, status=status.HTTP_404_NOT_FOUND)
        
        cls_reg = ClassFees.objects.filter(cls=student.student_class).first()
        if not cls_reg:
            return Response({"message": "Fees for this class has not been set"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        active_program = Program.objects.filter(is_active=True).first()

        if not active_program:
            return Response({"message": "No active program found"}, status=status.HTTP_404_NOT_FOUND)

        cls_reg_serializer = ClassFeeSerializer(cls_reg)
        reg_exist = Registration.objects.filter(student=student.id, year=active_program.id).first()
      
        if reg_exist:
            transaction_id = reg_exist.generate_transaction_id()
            reg_exist.transaction_id = transaction_id
            reg_exist.save()
            
            serializer = self.serializer_class(reg_exist)
            return Response({ "registration":serializer.data, "class_fee": cls_reg_serializer.data}, status=status.HTTP_200_OK)

        reg_obj = {
            "student": student,
            "year": active_program,
            "expected_amount": cls_reg.fee_amount,
            "registration_status": "none",
            "registration_expiry_date": active_program.academic_end,
        }

        

        serializer = self.serializer_class(data=reg_obj)
        if serializer.is_valid():
            serializer.save()
            return Response({ "registration": serializer.data, "class_fee": cls_reg_serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response({"message": "Unable to process request for student. Try again later", "errors": serializer.errors}, status=status.HTTP_200_OK)



class RegistrationListCreateAPIView(APIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        registrations = Registration.objects.filter(is_deleted=False)
        serializer = RegistrationFetchSerializer(registrations, many=True)
        return Response(serializer.data)

    def post(self, request):
        active_program = Program.get_active_program()

        if not active_program:
            return Response({"error": "No active program found"}, status=status.HTTP_404_NOT_FOUND)

        student_id = request.data.get('student')

        student = Student.objects.filter(id=student_id).first()

        if not student:
            return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        cls_reg = ClassFees.objects.filter(cls=student.student_class).first()   

        if not cls_reg:
            return Response({"error": "Class fee not set for student's class"}, status=status.HTTP_400_BAD_REQUEST)
        
        cls_reg_serializer = ClassFeeSerializer(cls_reg)

            

        # Check for existing registration for the active program year
        existing_registration = Registration.objects.filter(
            student_id=student_id,
            year=active_program,
            is_deleted=False
        ).first()

        # If registration exists, return the existing registration
        if existing_registration:
            transaction_id = existing_registration.generate_transaction_id()
            existing_registration.transaction_id = transaction_id
            existing_registration.save()

            serializer = self.serializer_class(existing_registration)

            return Response({ "registration":serializer.data, "class_fee": cls_reg_serializer.data}, status=status.HTTP_202_ACCEPTED)
  
        
        # No existing registration, proceed to create a new one
        request.data['year'] = active_program.id  
        request.data['expected_ammount'] = cls_reg.fee_amount
        request.data['registration_expiry_date'] = active_program.academic_end
        request.data['registration_status'] = "none"
        request.data['receiver'] = request.user.id

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "registration":serializer.data, "class_fee": cls_reg_serializer.data}, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RegistrationRetrieveUpdateDestroyAPIView(APIView):
    def get_object(self, pk):
        try:
            return Registration.objects.get(pk=pk)
        except Registration.DoesNotExist:
            raise Response({"message": "No registration found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        registration = self.get_object(pk)
        serializer = RegistrationFetchSerializer(registration)
        return Response(serializer.data)

    def put(self, request, pk):
        registration = self.get_object(pk)
        serializer = RegistrationSerializer(registration, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response("serializer.errors", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        registration = self.get_object(pk)
        registration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FilteredRegistrationsView(APIView):
    def get(self, request):
        # Get the filter parameter from the request
        filter_param = request.query_params.get('status', 'all')

        if filter_param == 'partial':
            # Filter for partial registrations
            registrations = Registration.objects.filter(
                registration_status__in=[FeeInstallments.First, FeeInstallments.Second]
            )
            serializer = RegistrationFilterSerializer(registrations, many=True)
        elif filter_param == 'complete':
            # Filter for complete registrations
            registrations = Registration.objects.filter(registration_status=FeeInstallments.Complete)
            serializer = RegistrationFilterSerializer(registrations, many=True)
        elif filter_param == 'not_registered':
            # Filter for students not registered at all
            # Using Subquery to filter students without any registration
            students = Student.objects.filter(
                ~Q(id__in=Registration.objects.values('student_id'))
            )
            serializer = StudentSerializer(students, many=True)
        else:
            # Fetch all registrations
            registrations = Registration.objects.all()
            serializer = RegistrationFilterSerializer(registrations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FilteredStudentsView(APIView):
    def get(self, request):
        try:
            # Initialize the query
            query = Q()

            # # Retrieve query parameters
            gender = request.query_params.get('gender')
            student_class = request.query_params.get('cls')
            student_status = request.query_params.get('status')

            if gender:
                query &= Q(user__gender=gender)
            if student_class:
                query &= Q(student_class=student_class)
            if student_status:
                query &= Q(status=student_status)

            print(query)
            students = Student.objects.filter(query)

            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PromoteStudentAPIView(APIView):

    def generate_new_student_subjects(self, student, new_class):
        subjects = new_class.subjects.all()
        grade = Grade.objects.create(student=student, classroom=new_class)

        sequences = Sequence.objects.all()
        for sequence in sequences:
            for subject in subjects:
                sts = StudentSubjects.objects.create(student=self, subject=subject, sequence=sequence)
                grade.grade_list.add(sts)
        
        grade.save()
    
    def post(self, request, student_id, new_class_id):
        # Retrieve the student and new class instances
        student = get_object_or_404(Student, id=student_id)
        new_class = get_object_or_404(Class, id=new_class_id)
        
        # Check if the student is already associated with the new class
        if StudentClassRelation.objects.filter(student=student, class_instance=new_class).exists():
            return Response({"message": "Student is already in the target class"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove the student from the current class
        current_class_relation = StudentClassRelation.objects.filter(student=student)
        current_class_relation.delete()
        
        # Create a new association between the student and the new class
        StudentClassRelation.objects.create(student=student, class_instance=new_class)

        student.student_class = new_class
        student.save()
        
        self.generate_new_student_subjects(student, new_class)
        # Optionally, you can perform additional actions here, such as updating the student's grade, position, etc.
        
        return Response({"message": "Student promoted to new class successfully",
                         "student_id": student_id,
                         "new_class_id": new_class_id},
                        status=status.HTTP_200_OK)
    



class RegisterPaymentAPIView(APIView):
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request): 
        payments = Payment.objects.all()
        serializer = self.serializer_class(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        amount = data.get('amount')
        registration = data.get('registration') 
        
        if not (amount and registration):
            return Response({'error': 'Incomplete payment data. Providee registration_id and amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        registration = None
        try:
            registration = Registration.objects.filter(id=registration).first()
        except Registration.DoesNotExist:
            return Response({'error': 'Invalid registration ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        data['depositor'] = request.user.id
        data['created_by'] = request.user.id

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def download_student_result_for_term(request, term_id, stud_id):
#     student_grades = get_object_or_404(Grade, student=stud_id, term=term_id)

#     grade_list = student_grades.grade_list.all()

#     grades_by_sequence = defaultdict(list)
#     for grade in grade_list:
#         sequence_id = grade.sequence.id
#         grades_by_sequence[sequence_id].append(grade)

#     # Group StudentSubjects by subject and sequence
#     grades_by_subject_and_sequence = defaultdict(list)
#     for grade in grade_list:
#         grades_by_subject_and_sequence[(grade.subject.id, grade.sequence_id)].append(grade)

#     grades_for_template = []
#     for (subject_id, sequence_id), grades in grades_by_subject_and_sequence.items():
#         # Calculate average grade for the sequence
#         seq_average = sum(grade.grade for grade in grades) / len(grades)

#         # Get other subject details
#         subject = Subject.objects.get(pk=subject_id)
#         sub_coef = subject.sub_coef

#         # Add data to the list for template
#         grades_for_template.append({
#             'subject_name': subject.name,
#             'grades': [grade.grade for grade in grades],
#             'seq_average': seq_average,
#             'sub_coef': sub_coef,
#         })

#     ctx = {'grades_for_template': grades_for_template, 'student': student_grades.student}
#     print(ctx)
    
#     return PDFTemplateResponse(
#         request=request,
#         template='results/template-one.html',
#         context=ctx,
#         filename='report_card.pdf'
#     )