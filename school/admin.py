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
]

admin.site.register( models )