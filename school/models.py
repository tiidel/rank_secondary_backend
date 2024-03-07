from django.db import models
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from core.models import User

from django.utils import timezone, text, crypto
from django.core.validators import FileExtensionValidator
from helper.enum import *
from core.models import BaseModel, SchoolBaseModel
from django.contrib.postgres.fields import ArrayField
#
#


class SchoolPhoto(models.Model):
    
    file = models.ImageField(upload_to="media/", null=False)
    
    school = models.ForeignKey("School", on_delete=models.CASCADE)
    

class School(SchoolBaseModel):
    
    name = models.CharField(_("School Name"), max_length=2560, blank=False, null=False)
    
    country = models.CharField(_("Country"), max_length=100, blank=False, null=False)

    country_code = models.CharField(_("e.g +237 or +1"), max_length=100, blank=True, null=True)
    
    principal_name = models.CharField(_("Dean of School"), max_length=100, blank=True, null=True)
    
    principal_email = models.CharField(max_length=100, blank=True, null=True)
    
    director_name = models.CharField(_("Director of School"), max_length=100, blank=True, null=True)
    
    director_email = models.CharField(max_length=100, blank=True, null=True)
    
    director_phone = models.CharField(max_length=100, blank=True, null=True)

    school_code = models.SlugField(unique=True, editable=False)
    
    city = models.CharField(_("Region of school"), max_length=100, blank=False, null=False) 

    address = models.CharField(_("School Location"), max_length=256)
    
    logo = models.ImageField(upload_to='media/', blank=True, null=True)
    
    type = models.CharField(_("School type e.g Elementary, Primary etc..."), max_length=256, null=True)
    
    report_card = models.CharField(_("String identifying selected report card design"), max_length=100, null=True, blank=True)
    
    billing_method = models.CharField(_("selected payment method e.g paypal or MTN"), max_length=50)
    
    active = models.BooleanField(_("School server is active"), default=False) 
    
    email = models.EmailField(max_length=100, null=False, blank=False)
    
    phone = models.CharField(max_length=20, null=False, blank=False)
    
    plan = models.CharField(_("Plan school is subscribed to e.g Free, standard or premium"),default='Free', choices=ServerPlan.choices, max_length=20, null=False, blank=False )
    
    verification_doc = models.FileField(upload_to="document", null=True, blank=True, validators=[FileExtensionValidator(['pdf', 'txt', 'docx'])])
    
    is_verified = models.BooleanField(_("Sets if school document is valid"), default=False) 

    is_active = models.BooleanField(_("Is this school subscription currently active"), default=True) 

    def generate_school_slug(self):
        if not self.school_code:
            random_string = crypto.get_random_string(length=6)
            slug = text.slugify(random_string)
            self.school_code = slug

    def save(self, *args, **kwargs):
        self.generate_school_slug()
        super().save(*args, **kwargs)
    
    class Meta:
        
        verbose_name = _("School")
        
        verbose_name_plural = _("School")
        
    
    def __str__(self):
        return self.name
    
 
class Terms(models.Model):
    """ --- TERMS OF A SCHOOL ----"""
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    term_name = models.CharField(_("Name of the term e.g first term, second term"), max_length=100, null=False, blank=False)
    
    start_date = models.DateField(_("Date term starts"), auto_now_add=True)
    
    end_date = models.DateField(_("Date term ends"), auto_now=False, auto_now_add=False)

    exams_per_term = models.IntegerField(_("Number of exams per term"), default=2, null=False, blank=False)
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @classmethod
    def get_active_term(cls):
        active_terms = cls.objects.filter(start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date())
        if active_terms.exists():
            return active_terms.first()
        return None
    class Meta:
        
        verbose_name = _("Term")
        
        verbose_name_plural = _("Terms")
        
    
    def __str__(self):
        return self.term_name
 
class Department(models.Model):
    """
    Description:
        Type of department and the language spoken in each department e.g Technical or Commercial and English or French 
    Author:
        kimbidarl@gmail.com        
    """
    
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    name = models.CharField(_("Education type e.g General, Technical"), choices=EducationType.choices, max_length=255, null=False, blank=False)
    
    language_supports = ArrayField(models.CharField(_("List of languages that the school uses"), max_length=100), default=list)
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        
    def __str__(self):
        return self.name
    
    
       
class Level(BaseModel):
    
    name = models.CharField(_("Levels in the school e.g Elementary, primary or secondary "), choices=LevelChoices.choices, max_length=50)  

    departments =  models.ForeignKey(Department, on_delete=models.CASCADE) 
   
    class Meta:
        verbose_name = _("Level")   
        verbose_name_plural = _("Levels")
    
    def __str__(self):
        return self.name


class Invitation(BaseModel):
    INVITATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    recipient_name = models.CharField(_("Full names of user you want to invite"),null=False, blank=False, max_length=300)  

    recipient_email = models.EmailField(_("Email of users to send invititations to"),null=False, blank=False, max_length=50)  

    invite_status = models.CharField(_("State of the invitation"), max_length=20, choices=INVITATION_STATUS_CHOICES, default='pending')

    tenant_name = models.CharField(_("School you are sending invites to"), max_length=50, null=False, blank=False)
    
    school = models.ForeignKey("school.School", on_delete=models.CASCADE)
   
    role = models.CharField(_("This refers to the role you are inviting the member for"), choices=UserRole.choices, max_length=100, blank=False, null=False)

    invitation_code = models.SlugField(unique=True, editable=False)
    
    message = models.TextField(blank=True)
    
    expiration_date = models.DateTimeField(null=True, blank=True)

    # recipient_groups = models.ManyToManyField(UserGroup)

    def is_expired(self):
        if self.expiration_date and self.expiration_date < timezone.now():
            return True
        return False
    
    def set_expiration_date(self):
        if not self.expiration_date:
            if self.created_at:
                self.expiration_date = self.created_at + timezone.timedelta(days=15)
            else:
                self.expiration_date = timezone.now() + timezone.timedelta(days=15)

    def set_invitation_code(self):
        if not self.invitation_code:
            random_string = crypto.get_random_string(length=6)
            slug = text.slugify(random_string)
            self.invitation_code = slug

    def save(self, *args, **kwargs):
        self.set_expiration_date()
        self.set_invitation_code()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Invitation")   
        verbose_name_plural = _("Invitations")
    
    def __str__(self):
        return f"{self.recipient_email} - {self.tenant_name}"

class Job(models.Model):

    applicant = models.ForeignKey(User, on_delete=models.CASCADE)

    search_status = models.CharField(_("Checks whether or not user is actively searching"), choices=JobApplicantStatus.choices, max_length=256, null=False, default=JobApplicantStatus.Active)
    
    role = models.CharField(_("Role he/she is applying for"), max_length=256, null=False)

    cv = models.FileField(upload_to="applicant_cv", validators=[FileExtensionValidator(['pdf', 'txt', 'docx'])])
    
    summary = models.CharField(_("Summary of job application"), max_length=5000, null=False)
    
    tenant = models.CharField(_("School you are applying into"), max_length=50, null=True, blank=True)

    country = models.CharField(_("Country of origin of applicant"), max_length=500, null=True, blank=True)
    
    rejection_count = models.IntegerField(_("Number of times the applicant has been rejected"), default=0)

    application_date = models.DateTimeField(_("Date and time of application"), auto_now_add=True)

    interview_date = models.DateTimeField(_("Date and time of interview"), null=True, blank=True)
    
    years_of_experience = models.IntegerField(_("Years of experience"), null=True, blank=True)

    references = models.TextField(_("References"), null=True, blank=True)

    expected_salary = models.DecimalField(_("Expected Salary"), max_digits=10, decimal_places=2, null=True, blank=True)

    feedback = models.TextField(_("Feedback provided by the interviewer"), null=True, blank=True)
    
    meeting_url = models.URLField(_("URL for the interview meeting"), null=True, blank=True)

    is_hired = models.BooleanField(_("Applicant has been hired for the position"), default=False)
    
    rejected = models.BooleanField(_("If the applicant has been rejected from the school"), default=False)

    def save(self, *args, **kwargs):
        if self.rejection_count >= 100:
            self.search_status = self.JobApplicantStatus.Unqualified
        
        elif self.rejection_count >= 50:
            self.search_status = self.JobApplicantStatus.Low
        
        if self.is_hired:
            self.rejection_count = 0

        super(Job, self).save(*args, **kwargs)

class SchoolStaffApply(models.Model): 
    """--- PEOPLE CAN APPLY TO JOIN A PARTICULAR SCHOOL ----"""

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    
    email = models.EmailField(_("email address"), blank=False, unique=True)
    
    avatar = models.ImageField(upload_to='images', null=True, blank=True)
    
    phone = models.CharField(_("Mobile contact number"), max_length=20, null=True, blank=False)

    role = models.CharField(_("Role he/she is applying for"), max_length=256, null=False)

    tenant = models.CharField(_("School you are applying into"), max_length=50)
    
    is_accepted = models.BooleanField(_("Displays whether or not user is accepted into school"), default=False)
    
    hidden = models.BooleanField(_("Whether or not admin wants this to display"), default=False)

    def __str__(self):
        return f'{self.role} - {self.tenant}'
    
class Event(models.Model):
    
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    name = models.CharField(_("Event Name"), max_length=50)
    
    start_date = models.DateField(_("Date event is expected to start"),auto_now_add=True)
    
    end_date = models.DateField(_("Date event ends"), auto_now=False, auto_now_add=False)

    class Meta:
        
        verbose_name = _("Event")
        
        verbose_name_plural = _("Events")
        
    
    def __str__(self):
        return self.name
    
class Program(models.Model):
    
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    
    event = models.ManyToManyField("Event", verbose_name=_("name"))
    
    academic_start = models.DateField(_("Date school starts"), default=timezone.now)
    
    academic_end = models.DateField(_("Date school closes"))
    
    is_active = models.BooleanField(_("Date program should terminate"), default=True)

    class Meta:
        
        verbose_name = _("Program")
        
        verbose_name_plural = _("Programs")
        
    
    def __str__(self):
        return f"{self.academic_start.year} - {self.academic_end.year} "

class PaymentDetail(models.Model):
    
    paypal_email = models.EmailField(_("Paypal email address"), max_length=256, null=True, blank=True)
    
    bank = models.CharField(_("Bank account"), max_length=256, null=True, blank=True)
    
    swift = models.CharField(_("Swift code for bank"), max_length=50, blank=True, null=True)
    
    account_number = models.CharField(_("Account number in bank"), max_length=50, blank=True, null=True)
    
    mtn_momo = models.CharField(_("Mobile money number"), blank=True, null=True, max_length=20)
    


class Social(models.Model):
    
    facebook = models.CharField(_("facebook profile link"),  default="https://fb.com/tiidel", max_length=150)
    
    twitter = models.CharField(_("twitter profile link"), default="https://x.com/tiidel", max_length=150)
    
    instagram = models.CharField(_("instagram profile link"), default="https://instagram.com/tiidel", max_length=150)
    
    linkedin = models.CharField(_("linkedin profile link"), default="https://linkedin.com/tiidel", max_length=150)
 



class Class(models.Model):
    """
    Description: Describes the class where student belongs
    Author: kimbidarl@gmail.com
    """
    
    class_name = models.CharField(_("e.g form one or lower sixth"), max_length=100)
    
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    
    enrolment = models.IntegerField(default=0)
    
    class_range = models.CharField(_("Approximate number of students in class"), max_length=50)
    
    instructor = models.ForeignKey("school.Staff", on_delete=models.CASCADE, null=True)
    
    h_o_d = models.CharField(max_length=100, null=True, blank=True)

    students = models.ManyToManyField('school.Student', through='StudentClassRelation')

class StudentClassRelation(models.Model):
    """ --- Describes the relationship between a student and a class ---"""
    student = models.ForeignKey('school.Student', on_delete=models.CASCADE)

    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)

    position = models.CharField(max_length=100, null=True, blank=True)

    enrollment_date = models.DateField(null=True, blank=True)

    grade = models.CharField(_("Grade of student"), max_length=10, null=True, blank=True)

class Staff(BaseModel):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    role = models.CharField(_("type e.g Teacher, Administrator"), max_length=256, choices=UserRole.choices, blank=False, null=False)
    
    expirience = models.IntegerField(_("Years of expirience in post"), default=0)
    
    city = models.CharField(_('City/town of residence of guardian'), max_length=256, null=False, blank=False)
    
    billing_method = models.CharField(_("Prefered payment method e.g paypal or MTN"), max_length=50)
    
    payment_method = models.ForeignKey(PaymentDetail, verbose_name=_(""), on_delete=models.CASCADE, null=True)
    
    bio = models.CharField(max_length=3000, null=False, blank=True)
    
    salary = models.IntegerField(_("salary"), default=0)
    
    is_active = models.BooleanField(_("If staff member is currently active in their role"), default=True)
    
    recruit_date = models.DateField(_("When they commenced work at the role "), null=True, blank=True)
    
    days_without_pay = models.IntegerField(_("Number of days since staff was payed"), default=0)


    @property
    def age(self):
        
        today = date.today()
        
        age = today.year - self.date_of_birth.year
        
        if today.month < self.date_of_birth.month or (
                today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            
            age -= 1
            
            return age


class Teacher(models.Model):
    """ --- Designnates a teacher as a staff --- """
    id = models.BigAutoField(primary_key=True) 

    staff_id = models.OneToOneField(Staff, on_delete=models.CASCADE)

    subject = models.ManyToManyField("school.Subject", related_name='subjects', verbose_name=_("subject"), default=None)

    class Meta:
        verbose_name = _("Teacher"),
        verbose_name_plural = _("Teachers")
    
    def __str__(self):
        return self.subject




class Subject(models.Model):
    
    name = models.CharField(max_length=100, blank=False, null=False)
    
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    
    sub_coef = models.IntegerField(_("Value of the subject (coefficient)"), default=1, null=False, blank=False)
    
    instructor = models.ForeignKey("school.Staff", on_delete=models.CASCADE, related_name='staff')
    
    course_duration = models.IntegerField(_("number of hours"), null=True, blank=True)

    cls = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        
    def __str__(self):
        return self.name



class Student(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    status = models.CharField(_("Marital status"), max_length=50, null=False, blank=False)
    
    student_class = models.ForeignKey(Level, on_delete=models.CASCADE)
    
    bio = models.CharField(max_length=3000, null=False, blank=True)

    subject_terms = models.ManyToManyField(Terms, verbose_name=_("name"))
    
    adm_status = models.BooleanField(default=True)
    
    department = models.CharField(max_length=256, null=False, blank=False)
    
    guardians = models.ForeignKey('Guardian', on_delete=models.SET_NULL, null=True, related_name="student_guardians")
    
    admission_date = models.DateField(_("Date person was admitted as a student"), auto_now_add=True)
    
    place_of_birth = models.CharField(_("Location where student was borne"), max_length=256, null=True, blank=True)
    
    is_repeater = models.BooleanField(_("Student has repeated this class"), default=False)
    
    is_new_student = models.BooleanField(_("Is this a transfer or new student in this school"), default=True)


    class Meta:
        
        verbose_name = _("Student")
        
        verbose_name_plural = _("Students")
        
    def __str__(self):
        return f" {self.user.first_name} {self.user.last_name}"
    
    def save(self, *args, **kwargs):
        created = not self.pk  
        super().save(*args, **kwargs)
        
        if created or 'student_class_id' in kwargs.get('update_fields', []):
            subjects = self.student_class.subjects.all()

            for subject in subjects:
                StudentSubjects.objects.create(student=self, subject=subject)
    

class StudentSubjects(models.Model):
    """ --- subjects that a student is enrolled in with sequence grades --- """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    first_seq = models.IntegerField(_("First sequence grade"), default=0, null=True, blank=True)

    second_seq = models.IntegerField(_("Second sequence grade"), default=0, null=True, blank=True)

    seq_average = models.FloatField(_("Average of sequence grades"), default=0, null=True, blank=True)
    
    class Meta:
        
        verbose_name = _("Student Subject")
        
        verbose_name_plural = _("Student Subjects")
        
    def __str__(self):
        return f" {self.student.user.first_name} {self.student.user.last_name} - {self.subject.name}"
    
    def save(self, *args, **kwargs):
        if self.first_seq is not None and self.second_seq is not None:
            self.seq_average = (self.first_seq + self.second_seq) / 2.0
        else:
            self.seq_average = None
        super().save(*args, **kwargs)

class Registration(BaseModel):
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    fee_type = models.CharField(max_length=15,blank=True, null=True)
    
    amount = models.IntegerField()
    
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    
    depositor = models.CharField(_("Names of user paying the fees"), max_length=20, blank=True, null=True)
    
    is_complete = models.BooleanField(default=False)
    
    installment = models.CharField(_("fee installment. partial or complete"), choices=FeeInstallments.choices, max_length=50)
    
    is_registered = models.BooleanField(_("Given a school calendar, the date registration expires"), default=False)



class Guardian(BaseModel):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    type = models.CharField(_("guardian type e.g Mother, Aunty, cousin"), max_length=256,  choices=GuardianType.choices, blank=False, null=False)
    
    alt_mail = models.EmailField(max_length=256, null=False, blank=False)
    
    city = models.CharField(_('City/town of residence of guardian'), max_length=256, null=False, blank=False)
    
    class Meta:
        
        verbose_name = _("Guardian")
        
        verbose_name_plural = _("Guardians")
        
    def __str__(self):
        return f" {self.user.first_name} {self.user.last_name}"