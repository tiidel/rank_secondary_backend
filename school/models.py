from django.db import models
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from core.models import User

from django.utils import timezone
#
#

class Event(models.Model):
    name = models.CharField(_("Event Name"), max_length=50)
    start_date = models.DateField(_("Date event is expected to start"),auto_now_add=True)
    end_date = models.DateField(_("Date event ends"), auto_now=False, auto_now_add=False)

class Program(models.Model):
    event = models.ManyToManyField("Event", verbose_name=_("name"))
    academic_start = models.DateField(_("Date school starts"), default=timezone.now)
    academic_end = models.DateField(_("Date school closes"))
    is_active = models.BooleanField(_("Date program should terminate"), default=True)


class PaymentDetail(models.Model):
    paypal_email = models.EmailField(_("Paypal email address"), max_length=256, null=True, blank=True)
    bank = models.CharField(_("Bank account"), max_length=256, null=True, blank=True)
    swift = models.CharField(_("Swift code for bank"), max_length=50, blank=True, null=True)
    account_number = models.CharField(_("Account number in bank"), max_length=50, blank=True, null=True)
    mtn_momo = models.CharField(_("Mobile money number"), blank=True, null=True, max_length=20)

class School(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, null=False, blank=False)
    phone = models.CharField(max_length=20, null=False, blank=False)
    billing_method = models.CharField(_("selected payment method e.g paypal or MTN"), max_length=50)
    payment_method = models.ForeignKey(PaymentDetail, verbose_name=_(""), on_delete=models.CASCADE)
    server_type = models.CharField(_("Type of server registered"), default='free', max_length=50)
    active = models.BooleanField(_("School server is active"), default=False) 


class Department(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(_("Education type e.g General, Technical"), max_length=100, null=False, blank=False)
    is_bilingual = models.CharField(_("Does this school support multiple languages"), default=False)
    h_o_d = models.CharField(max_length=100)


class Level(models.Model):
    form = models.CharField(_("e.g form one or lower sixth"), max_length=100)
    section = models.CharField(_("e.g A, B, C..."), null=False, blank=False, max_length=5)    
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    enrolment = models.IntegerField(default=0)



class Staff(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ManyToManyField("school.Subject", related_name='subjects', verbose_name=_("subject"), default=None)
    first_names = models.CharField(max_length=256, null=False, blank=False)
    last_names = models.CharField(max_length=256, null=False, blank=False)
    email = models.EmailField(max_length=256, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    image = models.ImageField(upload_to='images', null=True, blank=True)
    phone = models.CharField(max_length=20, null=False, blank=False)
    job = models.CharField(_("type e.g Teacher, Administrator"), blank=False, null=False)
    expirience = models.IntegerField(_("Years of expirience in post"), default=0)
    city = models.CharField(_('City/town of residence of guardian'), max_length=256, null=False, blank=False)
    address = models.CharField(_('location of residence of guardian/parent'), max_length=256, null=False, blank=False)    
    billing_method = models.CharField(_("selected payment method e.g paypal or MTN"), max_length=50)
    payment_method = models.ForeignKey(PaymentDetail, verbose_name=_(""), on_delete=models.CASCADE)
    bio = models.CharField(max_length=3000, null=False, blank=True)


    created_at = models.DateTimeField(_("registration date"), auto_now_add=True)
    update_at = models.DateTimeField(_("modification to profile"), auto_now=True)

    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
                today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
            return age


class Subject(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    department = models.ForeignKey(Level,on_delete=models.CASCADE)
    sub_coef = models.IntegerField(_("Value of the subject (coefficient)"), default=1, null=False, blank=False)
    instructor = models.ManyToManyField("school.Staff", related_name='teacher')



class Student(models.Model):
    first_name = models.CharField(max_length=256, null=False, blank=False)
    last_name = models.CharField(max_length=256, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    gender = models.CharField(max_length=50, null=False, blank=False)
    status = models.CharField(_("Marital status"), max_length=50, null=False, blank=False)
    student_class = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    bio = models.CharField(max_length=3000, null=False, blank=True)
    image = models.ImageField(upload_to='images', null=True, blank=True)

    adm_status = models.BooleanField(default=True)
    department = models.CharField(max_length=256, null=False, blank=False)
    address = models.CharField(max_length=256, null=False, blank=False)
    guad_name = models.CharField(max_length=256, null=False, blank=False)
    admission_date = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(_("registration date"), auto_now_add=True)
    update_at = models.DateTimeField(_("modification to profile"), auto_now=True)


    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
                today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
            return age




class Registration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    fee_type = models.CharField(max_length=15,blank=True, null=True)
    amount = models.IntegerField()
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    depositor = models.CharField(max_length=20, blank=True, null=True)
    is_complete = models.BooleanField(default=False)
    installment = models.CharField(_("fee installment. partial or complete"), max_length=50)
    is_registered = models.BooleanField(_("Given a school calendar, the date registration expires"), default=False)

    created_at = models.DateTimeField(_("registration date"), auto_now_add=True)
    update_at = models.DateTimeField(_("installment update"), auto_now=True)


class Guardian(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    first_names = models.CharField(max_length=256, null=False, blank=False)
    last_names = models.CharField(max_length=256, null=False, blank=False)
    type = models.CharField(_("guardian type e.g Mother, Aunty, cousin"), blank=False, null=False)
    email = models.EmailField(max_length=256, null=False, blank=False)
    phone = models.CharField(max_length=20, null=False, blank=False)
    city = models.CharField(_('City/town of residence of guardian'), max_length=256, null=False, blank=False)
    address = models.CharField(_('location of residence of guardian/parent'), max_length=256, null=False, blank=False)
    address_two = models.CharField(_('location of residence of guardian/parent'), max_length=256, null=True, blank=True)

    update_at = models.DateTimeField(_("modification to profile"), auto_now=True)
