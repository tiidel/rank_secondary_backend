from rest_framework.routers import DefaultRouter
from .views import *
from wkhtmltopdf.views import PDFTemplateView
from .downloads import *
from .analyticsApis import *
from .transactions import verify_payment, verify_subscription
from django.urls import path, include

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    # SUBSCRIPTION SYSTEM
    path('subscribe/', SubscriptionAPIView.as_view(), name="subscription"),
    path('verify-subscription/', verify_subscription, name="verify_subscription"),

    #SOCIAL AND PAYMENT
    path('socials/', SocialAPIView.as_view(), name="socials"),
    path('payments/', PaymentAPIView.as_view(), name="payments"),
    #SCHOOL
    path('schools/', SchoolView.as_view(), name="school"),
    path('schools/<str:id>/', SchoolUpdateView.as_view(), name="school"),
    path('school-files/<str:id>/', SchoolFilesView.as_view(), name="school-form-view"),

    #SCHOOL PROGRAM
    path('school-programs/', ProgramView.as_view(), name="school_progam"),
    path('school-programs/<str:id>/', ProgramItemView.as_view(), name="school_progam"),
    path('school-programs/current/terms/', YearTermView.as_view(), name="school_progam"),
    
    #SCHOOL EVENTS
    path('school-year-events/', SchoolEventAPIView.as_view(), name="events_in_program"),
    path('school-year-events/<int:id>/', SchoolEventUpdateAPIView.as_view(), name="event"),


    #TERMS
    path('terms/', TermAPIView.as_view(), name="terms"),
    path('terms/<int:id>/', TermAPIView.as_view(), name='term_detail'),
    path('terms/active/', ActiveTermView.as_view(), name='active_term'),


    #SEQUENCES
    path('sequences/', SequenceView.as_view(), name="seq"),

    
    # DEPARTMENT
    path('departments/', DepartementView.as_view(), name="department"),
    path('departments/<int:department_id>/', DepartmentItemView.as_view(), name="department_detail"),
    
    # LEVELS
    path('levels/', LevelView.as_view(), name="levels"),
    
    #CLASSES
    path('classes/', ClassView.as_view(), name="classes"),
    path('classes/fees/', ClassFeeView.as_view(), name="classes"),
    path('classes/fees/<str:id>/', ClassFeeUpdateView.as_view(), name="classes"),
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
    path('results/', StudentResultsView.as_view(), name='grade_student'),
    path('subject/results/', SubjectResultsView.as_view(), name='grade_student'),
    path('grades/subject/<str:term_id>/<str:subject_id>/', GradeStudentForSubjectAPIView.as_view(), name='grade_student'),
    path('grades/student/<str:cls_id>/<str:student_id>/', GradeStudentForAllSubjectAPIView.as_view(), name='grade_student_for_all_subjects'),

    #TEACHER REQUESTS
    path('me/subjects/<str:term_id>/', TeacherSubjectsAPIView.as_view(), name='fetch_my_subjects'),

    # GUARDIANS
    path('guardians/', GuardiansView.as_view(), name="guardian_view"),
    path('guardians/<str:id>/', GuardianDetail.as_view(), name="guardian_view"),

    #STUDENTS
    path('students/', StudentsView.as_view(), name='students'),
    path('students/<str:stud_id>/', StudentView.as_view(), name='students'),
    path('students/subjects/<str:stud_id>/', StudentsSubjectsView.as_view(), name='students_subjects'),
    path('students/class/<str:cls_id>/', StudentsInClassView.as_view(), name='students'),
    path('students/<str:stud_id>/profile/', StudentsInClassView.as_view(), name='students'),
    path('students/<str:stud_id>/performance/', StudentsInClassView.as_view(), name='students'),

    #TIMETABLE
    path('timetables/', TimeTableView.as_view(), name='timetable'),
    path('timetables/<str:cls_id>/<str:term_id>/', TimeTableFetchView.as_view(), name='timetable'),
    path('timetables/<int:id>/', TimetableUpdateAPIView.as_view(), name='timetable-update'),
    

    # DOWNLOAD 
    # path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('student_result/<str:stud_id>/download', download_student_result, name='download_student_result'),
    path('student_result/<str:cls_id>/<str:term_id>/<str:stud_id>/download', download_student_result_for_term, name='download_student_result'),
    path('class_result/<str:cls_id>/<str:term_id>/download', download_all_students_results_for_term, name='download_class_result'),
    path('zip/<str:cls>/<str:term>/', download_zip, name='download_zip'),
    path('pdf/', PDFTemplateView.as_view(template_name='results/template_one.html',
        filename='my_pdf.pdf'), name='pdf'),
    
    path('student_profile/<str:stud_id>/download/', download_student_profile, name='download_student_profile'),
    path('staff_profile/<str:staff_id>/download/', download_staff_profile, name='download_staff_profile'),

    #PAYMENTS
    path('fee-payments/', RegisterPaymentAPIView.as_view(), name='register_payment'),
    path('verify-payment/', verify_payment, name='verify-payment'),

    # REGISTRATION AND PROMOTION 
    path('promote_student/<int:student_id>/<int:new_class_id>/', PromoteStudentAPIView.as_view(), name='promote_student'),
    path('register/', RegistrationListCreateAPIView.as_view(), name='promote_student'),
    path('student/register/<str:stud_id>/', RegisterStudentAPIView.as_view(), name='promote_student'),
    path('register/<str:pk>/', RegistrationRetrieveUpdateDestroyAPIView.as_view(), name='promote_student'),
    
    path('analytics/registrations/', RegistrationAnalyticsAPIView.as_view(), name='analytics for registration'),
    path('analytics/registrations/deep/', DeepRegistrationAnalytics.as_view(), name='deep analytics for registration'),
    path('analytics/draw/', GraphDataAPIView.as_view(), name='deep analytics for registration'),
    path('analytics/numbers/', NumbersAnalyticsView.as_view(), name='Dashboad numbers analytics'),
    
    # DOWNLOAD CSVs
    path('download-users-csv/', download_users_as_csv, name='download_users_csv'),
    path('class_list/<str:class_id>/download/', download_class_list, name='download_class_list'),


]