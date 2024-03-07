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
    path('classes/<int:class_id>/instructor/', ClassInstructor.as_view(), name="class_instructor"),

    #STAFF INVITE
    path('invitation/', InvitationView.as_view(), name='staff_invitation'),
    path('invitation/<str:invite_id>/', InviteConfirmationView.as_view(), name='confirm_invitation'),
    
    #STAFF
    path('staffs/', StaffView.as_view(), name='staff_invitation'),
    path('staffs/<str:staff_id>/', StaffItemView.as_view(), name='staff_invitation'),
    path('staffs/<str:staff_id>/change-role/', StaffChangeRole.as_view(), name='staff_invitation'),
    
    # TEACHER(S)
    path('teachers/', TeachersView.as_view(), name='teachers'),

    #REQUEST ACCESS
    path('join-school/<str:school_id>/', RequestAccessToSchool.as_view(), name='staff_invitation'),
    path('join-school/<str:school_id>/<int:id>/', ApplicationReaction.as_view(), name='invitation_reaction'),

    # JOBS
    path('jobs/', JobApplicantsView.as_view(), name='job_portal'),
    
    # TODO: CREATE STAFF MEMBER //https://rank-secondary.vercel.app/staffs/create
    
    # SUBJECTS
    path('subjects/<str:cls_id>/', SubjectLevelView.as_view(), name='school_subjects'),

    
]