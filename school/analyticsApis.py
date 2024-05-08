
from .serializer import *
from django.shortcuts import render
from rest_framework_simplejwt import tokens
from rest_framework.views import APIView, status, Response
from rest_framework.pagination import PageNumberPagination
from wkhtmltopdf.views import PDFTemplateResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from collections import defaultdict

    
from .models import *
from .serializer import *
from core.permissions import *
from helper.enum import JobApplicantStatus
from django.db.models import Q
from helper.workers import *
from core.models import User
from core.serializers import LoginSerializer

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import Group
from django.dispatch import receiver
from datetime import datetime, timedelta

from django.db.models import Sum, Count

from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError

from django.db.models import Case, CharField, Value, When




class RegistrationAnalyticsAPIView(APIView):
    def get(self, request):
        month = request.GET.get('month')
        year = request.GET.get('year')

        registrations = Registration.objects.filter(created__month=month, created__year=year)

        total_amount = sum(registration.amount for registration in registrations)

        data = {
            'registrations': registrations.count(),  # Total number of registrations
            'total_amount': total_amount  # Total amount for the month
        }

        return Response(data, status=status.HTTP_200_OK)


class DeepRegistrationAnalytics(APIView):
    def get(self, request):
        # Get current date in the current timezone
        current_date = timezone.localdate()

        # Get sales and number of students for today
        today_sales = self.get_sales(current_date)
        today_students = self.get_students(current_date)

        # Get sales and number of students for yesterday
        yesterday = current_date - timedelta(days=1)
        yesterday_sales = self.get_sales(yesterday)
        yesterday_students = self.get_students(yesterday)

        # Get sales and number of students for the last 7 days
        last_7_days_sales = self.get_sales_range(current_date - timedelta(days=6), current_date)
        last_7_days_students = self.get_students_range(current_date - timedelta(days=6), current_date)

        # Get sales and number of students for the last 30 days
        last_30_days_sales = self.get_sales_range(current_date - timedelta(days=29), current_date)
        last_30_days_students = self.get_students_range(current_date - timedelta(days=29), current_date)

        data = {
            'today': {
                'sales': today_sales,
                'students': today_students
            },
            'yesterday': {
                'sales': yesterday_sales,
                'students': yesterday_students
            },
            'last_7_days': {
                'sales': last_7_days_sales,
                'students': last_7_days_students
            },
            'last_30_days': {
                'sales': last_30_days_sales,
                'students': last_30_days_students
            }
        }

        return Response(data, status=status.HTTP_200_OK)

    def get_sales(self, date):
        return Registration.objects.filter(created__date=date).aggregate(total_sales=Sum('amount'))['total_sales'] or 0

    def get_students(self, date):
        return Registration.objects.filter(created__date=date).count()

    def get_sales_range(self, start_date, end_date):
        return Registration.objects.filter(created__date__range=[start_date, end_date]).aggregate(total_sales=Sum('amount'))['total_sales'] or 0

    def get_students_range(self, start_date, end_date):
        return Registration.objects.filter(created__date__range=[start_date, end_date]).count()
    


class GraphDataAPIView(APIView):
    def get(self, request):
        # Get current date in the current timezone
        current_date = timezone.localdate()

        # Initialize data list to hold daily sales data
        graph_data = []

        # Get daily sales data for the last 30 days
        for i in range(30):
            date = current_date - timedelta(days=i)
            sales = Registration.objects.filter(created__date=date).aggregate(total_sales=Sum('amount'))['total_sales'] or 0
            graph_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sales': sales
            })

        return Response(graph_data, status=status.HTTP_200_OK)
    

class NumbersAnalyticsView(APIView):

    def get(self, request):
        classes = Class.objects.all().count()
        guardians = Guardian.objects.all().count()
        staffs = Staff.objects.all().count()
        students = Student.objects.all().count()
        applications = Job.objects.all().count()

        data = {
            "classes": classes,
            "guardians": guardians,
            "staffs": staffs,
            "applications": applications,
            "students": students
        }
        return Response(data, status=status.HTTP_200_OK)