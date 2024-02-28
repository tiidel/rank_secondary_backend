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
GROUP_PARENT = 'Parent'
GROUP_GENERAL = 'Staff'

def create_groups():
    teacher_group, _ = Group.objects.get_or_create(name=GROUP_TEACHER)
    accountant_group, _ = Group.objects.get_or_create(name=GROUP_ACCOUNTANT)
    secretary_group, _ = Group.objects.get_or_create(name=GROUP_SECRETARY)
    student_group, _ = Group.objects.get_or_create(name=GROUP_STUDENT)
    guardian_group, _ = Group.objects.get_or_create(name=GROUP_GUARDIAN)
    parent_group, _ = Group.objects.get_or_create(name=GROUP_PARENT)
    general_group, _ = Group.objects.get_or_create(name=GROUP_GENERAL)

    # Assign permissions to groups
    content_type = ContentType.objects.get_for_model(Program)

    # Teacher group permissions
    teacher_permissions = [
        # Add permissions for the teacher group as needed
    ]
    teacher_group.permissions.set(teacher_permissions)

    # Accountant group permissions
    accountant_permissions = [
        # Add permissions for the accountant group as needed
    ]
    accountant_group.permissions.set(accountant_permissions)

    # Secretary group permissions
    secretary_permissions = [
        get_permission('add_program', 'Can add program', content_type),
        get_permission('change_program', 'Can change program', content_type),   
        get_permission('delete_program', 'Can delete program', content_type),
        get_permission('view_program', 'Can view program', content_type),
    ]
    secretary_group.permissions.set(secretary_permissions)

    # Student group permissions
    student_permissions = [
        # Add permissions for the student group as needed
    ]
    student_group.permissions.set(student_permissions)

    # Guardian group permissions
    guardian_permissions = [
        # Add permissions for the guardian group as needed
    ]
    guardian_group.permissions.set(guardian_permissions)

    # Parent group permissions
    parent_permissions = [
        # Add permissions for the parent group as needed
    ]
    parent_group.permissions.set(parent_permissions)

    # General group permissions
    general_permissions = [
        # Add permissions for the general group as needed
    ]
    general_group.permissions.set(general_permissions)


def get_permission(codename, name, content_type):
    try:
        return Permission.objects.get(codename=codename, content_type=content_type)
    except Permission.DoesNotExist:
        return Permission.objects.create(codename=codename, name=name, content_type=content_type)