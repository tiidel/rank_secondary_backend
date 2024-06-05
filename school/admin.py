from django.contrib import admin

# Register your models here.
from .models import *

models = [
    Level,
    Program,
    Event,
    Social,
    PaymentDetail,
    Guardian,
    Student,
    Staff,
    Class,
    StudentClassRelation,
    Terms,
    Sequence,
    Department,
    School,
    ClassFees,
    Subject,
    Grade,
    Registration,
    Subscription,
    ServiceCharge,
    Payment,
    Timetable,
    Attendance

]

admin.site.register( models )