from rest_framework.routers import DefaultRouter
from .views import *

from django.urls import path

router = DefaultRouter()
router.register(r'school', SchoolView)
router.register(r'department', DepartmentView)
router.register(r'level', LevelView)
router.register(r'staff', StaffView)
router.register(r'subject', SubjectView)
router.register(r'student', StudentView)
router.register(r'registration', RegistrationView)
router.register(r'guardian', GuardianView)

urlpatterns = [

] + router.urls