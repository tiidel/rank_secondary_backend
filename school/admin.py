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
    Terms
]

admin.site.register( models )