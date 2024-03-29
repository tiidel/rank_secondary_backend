from rest_framework import serializers
from .models import Student, Subject, Department, School, Level, Program, Staff, Registration, Guardian, Class, Invitation

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'
        
class SchoolFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['logo', 'verification_doc']

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'
        
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'
        
class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = '__all__'