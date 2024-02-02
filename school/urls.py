from rest_framework.routers import DefaultRouter
from .views import *

from django.urls import path

urlpatterns = [
    
    #SCHOOL
    path('schools/', SchoolView.as_view(), name="school"),
    path('school-files/<str:id>/', SchoolFilesView.as_view(), name="school-form-view"),
    
    # DEPARTMENT
    path('departments/', DepartementView.as_view(), name="department"),
    path('departments/<int:department_id>/', DepartmentItemView.as_view(), name="department_detail"),
    
    # LEVELS
    path('levels/', LevelView.as_view(), name="levels"),
    
    #CLASSES
    path('classes/', ClassView.as_view(), name="classes"),
    path('classes/<int:class_id>/', ClassItemView.as_view(), name="classes"),

    #STAFF INVITE
    path('invitation/', InvitationView.as_view(), name='staff_invitation')
    
]