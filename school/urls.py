from rest_framework.routers import DefaultRouter
from .views import *

from django.urls import path, include

router = DefaultRouter()
router.register(r'social', SocialViewSet)
router.register(r'payment-detail', PaymentDetailViewset)

urlpatterns = [
    path('', include(router.urls)),

    #SCHOOL
    path('schools/', SchoolView.as_view(), name="school"),
    path('school-files/<str:id>/', SchoolFilesView.as_view(), name="school-form-view"),

    #SCHOOL PROGRAM
    path('school-programs/', ProgramView.as_view(), name="school_progam"),
    path('school-programs/<str:id>/', ProgramItemView.as_view(), name="school_progam"),
    
    #SCHOOL EVENTS
    path('school-year-events/', SchoolEventAPIView.as_view(), name="events_in_program"),
    path('school-year-events/<int:id>/', SchoolEventUpdateAPIView.as_view(), name="event"),


    #TERMS
    path('terms/', TermAPIView.as_view(), name="terms"),
    path('terms/<int:id>/', TermAPIView.as_view(), name='term_detail'),
    path('active-term/', ActiveTermView.as_view(), name='active_term'),
    
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
    path('subjects/grade/<str:subj_id>/', GradeStudentView.as_view(), name='grade_student'),
    
    # GRADES
    path('grades/<str:term>/<str:subject>/', GradeStudentForSubjectAPIView.as_view(), name='grade_student'),
    path('grades/student/<str:term_id>/<str:student_id>/', GradeStudentForAllSubjectAPIView.as_view(), name='grade_student_for_all_subjects'),

    #STUDENTS
    path('students/', StudentView.as_view(), name='students'),
    path('students/<str:cls_id>/', StudentsInClassView.as_view(), name='students'),
    path('students/<str:stud_id>/', StudentsInClassView.as_view(), name='students'),
    path('students/<str:stud_id>/profile/', StudentsInClassView.as_view(), name='students'),
    path('students/<str:stud_id>/performance/', StudentsInClassView.as_view(), name='students'),
    
]