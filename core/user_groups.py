
from rest_framework.views import Response, status
from django.contrib.auth.models import Group, Permission
from core.models import User
from school.models import *
from django.contrib.contenttypes.models import ContentType

GROUP_TEACHER = 'Teacher'
GROUP_ACCOUNTANT = 'Accountant'
GROUP_SECRETARY = 'Secretary'
GROUP_STUDENT = 'Student'
GROUP_GUARDIAN = 'Guardian'

def create_groups():
    Group.objects.get_or_create(name=GROUP_TEACHER)
    Group.objects.get_or_create(name=GROUP_ACCOUNTANT)
    Group.objects.get_or_create(name=GROUP_SECRETARY)
    Group.objects.get_or_create(name=GROUP_STUDENT)
    Group.objects.get_or_create(name=GROUP_GUARDIAN)

    admin_content = ContentType.objects.get_for_model(model=School)
