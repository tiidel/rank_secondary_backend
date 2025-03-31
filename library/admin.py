from django.contrib import admin

# Register your models here.
from .models import *

models = [
    Book,
    LibraryCategory,
    LibraryMember,
    Librarian,
    BookCopy,
    BookLoan,
    Reservation,
    Fine,
    LibraryCard
]

admin.site.register( models )