from django.db import models
from datetime import date, datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from core.models import User


from django.utils import timezone, text, crypto
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from helper.enum import *
from core.models import BaseModel, SchoolBaseModel
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
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
    
    start_date = models.DateField(_("Date term starts"), auto_now_add=False)
    
    end_date = models.DateField(_("Date term ends"), auto_now=False, auto_now_add=False)

    exams_per_term = models.IntegerField(_("Number of exams per term"), default=2, null=False, blank=False)

    term_validated = models.BooleanField(_("If the term has been validated"), default=False)
    
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
    
    def save(self, *args, **kwargs):
        # if self.start_date > self.end_date:
        #     raise ValidationError("Start date must be before end date.")
        
        if self.end_date < timezone.now().date():
            self.term_validated = True
        super().save(*args, **kwargs)
 
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
    
    programs = models.ForeignKey('school.Program', on_delete=models.CASCADE)
    
    name = models.CharField(_("Event Name"), max_length=50)
    
    start_date = models.DateField(_("Date event is expected to start"),auto_now_add=True)
    
    end_date = models.DateField(_("Date event ends"), auto_now=False, auto_now_add=False)

    class Meta:
        
        verbose_name = _("Event")
        
        verbose_name_plural = _("Events")
        
    
    def __str__(self):
        return self.name
    
class Program(BaseModel):
    
    terms = models.ManyToManyField("Terms", verbose_name=_("program_terms"))
    
    events = models.ManyToManyField("Event", verbose_name=_("name"), null=True)
    
    academic_start = models.DateField(_("Date school starts"))
    
    academic_end = models.DateField(_("Date school closes"))
    
    is_active = models.BooleanField(_("Date program should terminate"), default=True)

    class Meta:
        
        verbose_name = _("Program")
        
        verbose_name_plural = _("Programs")

        ordering = ['-academic_end']
        
    
    def clean(self):
        if self.academic_start >= self.academic_end:
            raise ValidationError("Start date must be before end date.")
        
        existing_programs = Program.objects.exclude(pk=self.pk) 

        if existing_programs.filter(academic_start__lt=self.academic_end, academic_end__gt=self.academic_start).exists():
            raise ValidationError("Programs cannot overlap with each other.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.academic_start.year} - {self.academic_end.year} "

    def update_fields(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def deactivate_if_expired(self):
        if self.academic_end < timezone.now().date():
            self.is_active = False
            self.save()
    
    def is_currently_active(self):
        today = timezone.now().date()
        return self.academic_start <= today <= self.academic_end
    
    def get_active_program():
        return Program.objects.filter(academic_start__lte=timezone.now().date(), academic_end__gte=timezone.now().date()).first()

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
    level = models.ForeignKey('school.Level', on_delete=models.CASCADE, null=True)

    class_name = models.CharField(_("e.g form one or lower sixth"), max_length=100)
    
    enrolment = models.IntegerField(default=0)
    
    class_range = models.CharField(_("Approximate number of students in class"), max_length=50)
    
    instructor = models.ForeignKey("school.Staff", on_delete=models.CASCADE, null=True, blank=True)
    
    h_o_d = models.CharField(max_length=100, null=True, blank=True)

    students = models.ManyToManyField('school.Student', through='StudentClassRelation')

    subjects = models.ManyToManyField('Subject', related_name='classes', null=True)


class StudentClassRelation(models.Model):
    """ --- Describes the relationship between a student and a class ---"""
    student = models.ForeignKey('school.Student', on_delete=models.CASCADE)

    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)

    position = models.CharField(max_length=100, null=True, blank=True)

    enrollment_date = models.DateField(null=True, blank=True)

    grade = models.CharField(_("Grade of student"), max_length=10, null=True, blank=True)


class ClassFees(models.Model):
    cls =  models.ForeignKey(Class, on_delete=models.CASCADE)

    fee_amount = models.IntegerField(_("Total amount of money to be payed by students in this class"))

    first_installment = models.IntegerField(_("First installment of this fee"))

    second_installment = models.IntegerField(_("Second installment of this fee"), null=True, blank=True)

    third_installment = models.IntegerField(_("Third installment of this fee"), null=True, blank=True)

    class Meta:
        verbose_name = _("class Fee"),
        verbose_name_plural = _("class Fees")

    def __str__(self):
        return f"Class {self.cls.class_name} - {self.fee_amount}"

    

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
    
    cls = models.ForeignKey(Class, on_delete=models.CASCADE)
    
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    
    sub_coef = models.IntegerField(_("Value of the subject (coefficient)"), default=1, null=False, blank=False)
    
    instructor = models.ForeignKey("school.Staff", on_delete=models.CASCADE, related_name='staff')
    
    course_duration = models.IntegerField(_("number of hours"), null=True, blank=True)


    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        self.cls.subjects.add(self)



class Student(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    status = models.CharField(_("Marital status"), max_length=50, null=False, blank=False)
    
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    
    bio = models.CharField(max_length=3000, null=False, blank=True)
    
    adm_status = models.BooleanField(default=True)
    
    department = models.CharField(max_length=256, null=False, blank=False)

    guardians = models.ForeignKey('Guardian', on_delete=models.SET_NULL, null=True, related_name="student_guardians")
    
    admission_date = models.DateField(_("Date person was admitted as a student"), auto_now_add=True)
    
    place_of_birth = models.CharField(_("Location where student was borne"), max_length=256, null=True, blank=True)
    
    is_repeater = models.BooleanField(_("Student has repeated this class"), default=False)
    
    is_new_student = models.BooleanField(_("Is this a transfer or new student in this school"), default=True)

    qualification = models.CharField(_("Qualification of student"), max_length=256, null=True, blank=True)

    academic_year = models.CharField(_("Academic year of student"), max_length=256, null=True, blank=True)

    medical_condition = models.CharField(_("Medical condition of student"), max_length=256, null=True, blank=True)

    emergency_contact = models.CharField(_("Emergency contact of student"), max_length=256, null=True, blank=True)
    


    class Meta:
        
        verbose_name = _("Student")
        
        verbose_name_plural = _("Students")
        
    def __str__(self):
        return f" {self.user.first_name} {self.user.last_name}"
    

    def save(self, *args, **kwargs):

        created = not self.pk  
        super().save(*args, **kwargs)
        
        if created or 'student_class' in kwargs.get('update_fields', []):
            class_instance = self.student_class

            existing_subjects = set(self.studentsubjects_set.values_list('subject_id', flat=True))

            terms = Terms.objects.all()
            for term in terms:
                sequences = Sequence.objects.filter(term=term)
                grade, _ = Grade.objects.get_or_create(student=self, classroom=class_instance, term=term)
                for sequence in sequences:
                    for subject in class_instance.subjects.all():
                        sts, _ = StudentSubjects.objects.get_or_create(student=self, subject=subject, sequence=sequence)
                        if sts.subject.id not in existing_subjects:
                            sts.save()
                        grade.grade_list.add(sts)
                
                if not grade.position:
                    grade.position = self.student_class.studentclassrelation_set.filter(class_instance=class_instance).count()
                

                grade.save()
                            
            subjects = class_instance.subjects.all()
            
            # Remove subjects that are no longer in the class
            if not self.studentclassrelation_set.filter(class_instance=class_instance).exists():
                StudentClassRelation.objects.create(student=self, class_instance=class_instance)

            


    

class StudentSubjects(models.Model):
    """ --- subjects that a student is enrolled in with sequence grades --- """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    grade = models.FloatField(_("Grade"), default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    sequence = models.ForeignKey('school.Sequence', on_delete=models.CASCADE, null=True, blank=True)

    seq_average = models.FloatField(_("Average of sequence grades"), default=0, null=True, blank=True)
    
    class Meta:
        
        verbose_name = _("Student Subject")
        
        verbose_name_plural = _("Student Subjects")

     
    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.subject.name} - {self.sequence.name}"

    def save(self, *args, **kwargs):
        """Calculate the average grade for the sequence"""
        super().save(*args, **kwargs)
        

    

        # # Calculate average grade only if there's a sequence associated
        # if self.sequence:
        #     # Get all grades for the same student, subject, and sequence
        #     grades = StudentSubjects.objects.filter(student=self.student, subject=self.subject, sequence=self.sequence)
        #     num_grades = grades.count()
            
        #     # Calculate sum of grades
        #     total_grade = sum(grade.grade for grade in grades)
            
        #     # Calculate average grade
        #     self.seq_average = total_grade / num_grades if num_grades > 0 else 0
        #     self.save(update_fields=['seq_average'])  # Save the average grade


class Sequence(models.Model):
    """ --- Describes the sequence of the school year --- """
    name = models.CharField(_("Name of the sequence e.g first sequence, second sequence"), max_length=100, null=False, blank=False)
    
    start_date = models.DateField(_("Date sequence starts"), auto_now_add=False, null=True, blank=True)
    
    end_date = models.DateField(_("Date sequence ends"), auto_now=False, auto_now_add=False, null=True, blank=True)

    term = models.ForeignKey(Terms, on_delete=models.CASCADE, related_name='sequences')
    
    class Meta:
        
        verbose_name = _("Sequence")
        
        verbose_name_plural = _("Sequences")
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date.")
        super().save(*args, **kwargs)


class Grade(models.Model):
    """ --- Student Grade for Term --- """
    id = models.BigAutoField(primary_key=True)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    classroom = models.ForeignKey(Class, on_delete=models.CASCADE)

    term  = models.ForeignKey(Terms, on_delete=models.CASCADE, null=True, blank=True)

    average = models.FloatField(_("Student average for the term"), default=0)

    position = models.IntegerField(_("Student position in class"), null=True)

    grade_list = models.ManyToManyField(StudentSubjects, related_name='student_rank_grades' )

    def calculate_average(self):
        """Calculate the average grade for the student for the term"""
        total_grades = sum(subject.seq_average for subject in self.grade_list.all())
        num_subjects = self.grade_list.count()
        self.average = total_grades / num_subjects if num_subjects > 0 else 0

    def save(self, *args, **kwargs):
        """Save and update average grade"""
        super().save(*args, **kwargs)

        # self.calculate_average()

    class Meta:
        ordering = ['-average']



class Registration(BaseModel):
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    fee_type = models.CharField(max_length=15,blank=True, null=True)

    transaction_count = models.IntegerField(default=0)
    
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    is_complete = models.BooleanField(default=False)

    expected_ammount = models.IntegerField(_("The amount student is expected to pay for the class"))

    payed_ammount = models.IntegerField(_("Money student has actually paid for the school year"), default=0)
    
    registration_status = models.CharField(_("fee installment. partial or complete"), choices=FeeInstallments.choices, max_length=50)

    payments = models.ManyToManyField('Payment', related_name='registrationPayment', null=True)
    
    is_registered = models.BooleanField(_("Given a school calendar, the date registration expires"), default=False)

    year = models.ForeignKey(Program, on_delete=models.CASCADE, null=False)

    registration_date = models.DateField( auto_now=True)

    registration_expiry_date = models.DateField()

    notes = models.TextField(blank=True, null=True)

    class Meta:
        
        verbose_name = _("Registration")
        
        verbose_name_plural = _("Registrations")

    def __str__(self):
        return f"{self.student.user.email} {self.registration_status}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        current_date = timezone.now().date()

        self.transaction_count += 1

        transaction_id = f'Rank{current_date.strftime("%Y%m%d")}{self.transaction_count + 1:09d}'
        
        return transaction_id


class Payment(models.Model):

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    installment_number = models.IntegerField()

    amount = models.IntegerField()

    payment_date = models.DateField()

    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    payment_status = models.CharField(max_length=20, blank=True, null=True)

    is_complete = models.BooleanField(default=False)

    ### NULLABLES ###
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    depositor = models.CharField(max_length=20, blank=True, null=True)
    
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    payment_gateway = models.CharField(max_length=50, blank=True, null=True)

    currency = models.CharField(max_length=3, blank=True, null=True)

    reference_number = models.CharField(max_length=50, blank=True, null=True)

    payment_confirmation_date = models.DateField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        
        verbose_name = _("Fee")
        
        verbose_name_plural = _("Fees")

    def __str__(self):
        return f"{self.transaction_id} {self.amount}"



class Guardian(BaseModel):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    student = models.ManyToManyField(Student, related_name='guardian_student_list' )
    
    type = models.CharField(_("guardian type e.g Mother, Aunty, cousin"), max_length=256,  choices=GuardianType.choices, blank=False, null=False)
    
    alt_mail = models.EmailField(max_length=256, null=True, blank=True)
    
    city = models.CharField(_('City/town of residence of guardian'), max_length=256, null=True, blank=True)
    
    class Meta:
        
        verbose_name = _("Guardian")
        
        verbose_name_plural = _("Guardians")
        
    def __str__(self):
        return f" {self.user.first_name} {self.user.last_name}"




class Timetable(models.Model):
        """--- Describes the timetable of a class ---"""

        DAY_CHOICES = [
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'),
        ]
            
        term = models.ForeignKey(Terms, on_delete=models.CASCADE)

        class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
        
        day = models.CharField(_("Day of the week"), max_length=50, choices=DAY_CHOICES)
        
        start_time = models.TimeField(_("Time the class starts"), auto_now=False, auto_now_add=False)
        
        end_time = models.TimeField(_("Time the class ends"), auto_now=False, auto_now_add=False)
        
        subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
        
        class Meta:
            
            verbose_name = _("TimeTable")
            
            verbose_name_plural = _("TimeTables")
            
        def __str__(self):
            return f"{self.day} - {self.start_time} - {self.end_time}"


class Attendance(models.Model):
    """--- Manage Attendance of students in class ---"""

    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)

    date = models.DateField()

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.timetable} - {self.date}"
