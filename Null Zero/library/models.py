from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from school.models import Student, Staff, Class, School, Program
from django.db.models import Max

class Book(BaseModel):

    title = models.CharField(max_length=200)

    authors = models.CharField(max_length=200)

    isbn = models.CharField(max_length=13, unique=True)

    publication_date = models.DateField()

    publisher = models.CharField(max_length=100)

    edition = models.CharField(max_length=50, blank=True)

    description = models.TextField(blank=True)

    call_number = models.CharField(max_length=50, unique=True)

    total_copies = models.IntegerField(default=1)

    available_copies = models.IntegerField(default=1)

    language = models.CharField(max_length=50)

    page_count = models.IntegerField(null=True, blank=True)

    categories = models.ManyToManyField('Category', related_name='books')

    def __str__(self):
        return self.title
    


class Category(BaseModel):

    name = models.CharField(max_length=50)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    


class LibraryMember(BaseModel):

    user = models.OneToOneField(Student, on_delete=models.CASCADE)

    member_id = models.CharField(max_length=10, unique=True)

    is_active = models.BooleanField(default=True)

    expiry_date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.member_id:
            self.member_id = self.generate_member_id()
        super().save(*args, **kwargs)

    def generate_member_id(self):
        # Get the tenant name (school code)
        tenant = School.objects.get(id=self.user.student.student_class.level.departments.school_id)
        tenant_code = tenant.school_code

        # Get the start year of the current program
        current_program = Program.objects.filter(is_active=True).first()
        year = str(current_program.academic_start.year)[-2:]

        # Get the level code
        level_code = self.user.student.student_class.level.name[0].upper()

        # Set the role code (SU for Student)
        role_code = 'SU'

        # Generate the index
        last_member = LibraryMember.objects.filter(
            member_id__startswith=f"{tenant_code}{year}{level_code}{role_code}"
        ).aggregate(Max('member_id'))['member_id__max']

        if last_member:
            index = int(last_member[-4:]) + 1
        else:
            index = 1

        # Combine all parts
        member_id = f"{tenant_code}{year}{level_code}{role_code}{index:04d}"
        return member_id

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.member_id}"

    class Meta:
        verbose_name = "Library Member"
        verbose_name_plural = "Library Members"



class Librarian(BaseModel):

    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)

    librarian_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.librarian_id}"



class BookCopy(BaseModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    accession_number = models.CharField(max_length=20, unique=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book.title} - {self.accession_number}"


    def checkout(self):
        """Mark this copy as checked out """
        if not self.is_available:
            raise ValueError("Book is not available")
        self.is_available = False
        self.save()

    def return_book(self):
        """Mark this copy as returned """
        if self.is_available:
            raise ValueError("Book is available")
        self.is_available = True
        self.save()


class BookLoan(BaseModel):

    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='loans')

    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE)

    librarian = models.ForeignKey(Librarian, on_delete=models.CASCADE)

    loan_date = models.DateField(auto_now_add=True)

    due_date = models.DateField()

    return_date = models.DateField(null=True, blank=True)

    is_returned = models.BooleanField(default=False)

    renewed_count = models.IntegerField(default=0)

    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.book_copy.book.title} - {self.member.user.get_full_name()}"


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.is_returned:
            if not self.book_copy.is_available:
                raise ValidationError("This book copy is not available for loan")
            self.book_copy.checkout()

        if not is_new and self.is_returned and self.return_date:
            original = BookLoan.objects.get(pk=self.pk)
            if not original.is_returned:
                self.book_copy.return_book()

        super().save(*args, **kwargs)


class Reservation(BaseModel):

    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE)

    reservation_date = models.DateTimeField(auto_now_add=True)

    expiry_date = models.DateField()

    res_status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled')
    ], default='PENDING')

    def __str__(self):
        return f"{self.book.title} - {self.member.user.get_full_name()}"



class Fine(BaseModel):

    loan = models.ForeignKey(BookLoan, on_delete=models.CASCADE, related_name='fine')

    amount = models.DecimalField(max_digits=6, decimal_places=2)

    reason = models.CharField(max_length=100)

    date_issued = models.DateTimeField(auto_now_add=True)

    is_paid = models.BooleanField(default=False)

    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.loan.book_copy.book.title} - {self.loan.member.user.get_full_name()} - {self.amount}"

    def mark_as_paid(self):
        if self.is_paid:
            raise ValueError("Fine is already paid")
        self.is_paid = True
        self.save()

class LibraryCard(BaseModel):

    member = models.OneToOneField(LibraryMember, on_delete=models.CASCADE)

    card_number = models.CharField(max_length=20, unique=True)

    issue_date = models.DateField(auto_now_add=True)

    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.card_number}"