from rest_framework import serializers
from .models import *
from core.serializers import LoginSerializer


class StaffSerializer(serializers.ModelSerializer):
    user = LoginSerializer()
    class Meta:
        model = Staff
        fields = '__all__'

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = '__all__'


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = '__all__'
 
class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'
        
class ClassFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassFees
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        
               
class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms
        fields = '__all__'
class SequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequence
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
        
class LevelClassSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer()
    class Meta:
        model = Level
        fields = '__all__'
        
class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'

class ClassFetchSerializer(serializers.ModelSerializer):
    level = LevelClassSerializer()
    class Meta:
        model = Class
        fields = '__all__'

class ClassItemSerializer(serializers.ModelSerializer):
    level = LevelClassSerializer()

    class Meta:
        model = Class
        depth = 2
        fields = '__all__'
class ClassInstructorSerializer(serializers.ModelSerializer):
    instructor = serializers.CharField() 
    class Meta:
        model = Class
        fields = ['instructor']

class StudentSerializer(serializers.ModelSerializer):
    user = LoginSerializer()
    student_class = ClassSerializer()
    class Meta:
        model = Student
        depth = 0
        fields = '__all__'
        
class StudentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class MySubjectSerializer(serializers.ModelSerializer):
    instructor = StaffSerializer()
    class Meta:
        model = Subject
        depth = 1
        fields = '__all__'

class SubjectRequestSerializer(serializers.ModelSerializer):
    instructor = StaffSerializer()
    class Meta:
        model = Subject
        fields = '__all__'
class StudentSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubjects
        fields = '__all__'
      

class StudentSubjectsSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    class Meta:
        model = StudentSubjects
        fields = '__all__'


class GuardianSerializer(serializers.ModelSerializer):
    subject = LoginSerializer()
    class Meta:
        model = Guardian
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    grade_list = StudentSubjectsSerializer(many=True, read_only=True)
    class Meta:
        model = Grade
        fields = '__all__'    

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'    

class ProgramSubscriptionSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer()
    class Meta:
        model = Program
        fields = '__all__'    


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'
        
class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class RegistrationFetchSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    year = ProgramSerializer()
    class Meta:
        model = Registration
        fields = '__all__'



class StudentRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'


class GuardianSerializer(serializers.ModelSerializer):
    user = LoginSerializer()
    class Meta:
        model = Guardian
        fields = '__all__'
class GuardianItemSerializer(serializers.ModelSerializer):
    user = LoginSerializer()
    student = StudentSerializer(many=True, read_only=True)
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


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'

# =========== STUDENT SUBJECT SERIALIZER =================
class SubjectWithInstructorSerializer(serializers.ModelSerializer):
    instructor = StaffSerializer()
    class Meta:
        model = Subject
        fields = '__all__'
class StudentSubjectForStudentSerializer(serializers.ModelSerializer):
    subject = SubjectWithInstructorSerializer()
    class Meta:
        model = StudentSubjects
        fields = '__all__'

class TimetableFetchSerializer(serializers.ModelSerializer):
    subject = SubjectWithInstructorSerializer()
    class Meta:
        model = Timetable
        fields = '__all__'