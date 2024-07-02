from django.contrib import admin

# Register your models here.
from .models import *

models = [
    Book,
    Category,
    LibraryMember,
    Librarian,
    BookCopy,
    BookLoan,
    Reservation,
    Fine,
    LibraryCard
]

admin.site.register( models )