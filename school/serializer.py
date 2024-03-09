from rest_framework import serializers
from .models import Student, Subject, Department, School, Level, Program, Staff, Registration, Guardian, Class, Invitation, Job, SchoolStaffApply, Teacher, Terms, StudentSubjects
from core.serializers import LoginSerializer

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    user = LoginSerializer()
    class Meta:
        model = Staff
        fields = '__all__'

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'
        
class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms
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
class ClassFetchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        depth = 1
        fields = '__all__'
class ClassInstructorSerializer(serializers.ModelSerializer):
    instructor = serializers.CharField() 
    class Meta:
        model = Class
        fields = ['instructor']

class StudentSerializer(serializers.ModelSerializer):
    user = LoginSerializer()
    class Meta:
        model = Student
        depth = 0
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
class StudentSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubjects
        fields = '__all__'
    

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class SchoolStaffApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolStaffApply
        fields = '__all__'