import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from rest_framework import status
import json

from school.models import Student, Class, Level, Department, School, Staff, PaymentDetail

User = get_user_model()

from .models import Book, LibraryMember, BookLoan, LibraryCategory, BookCopy, Fine, Reservation, Librarian


def uuid_converted(value):
    """
    Convert uuid to string
    """
    if isinstance(value, uuid.UUID):
        return str(value)
    raise TypeError(f'Object of type {value.__class__.__name__} is not JSON serializable')



class LibraryViewsTest(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.c = TenantClient(self.tenant)

        # Create test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        # create school
        self.test_school = School.objects.create(
            name='test school',
            country='test country',
            address='test address',
            phone='0987654321',
            logo='test.png',
            school_code='TSCH'
        )
        # create department
        self.test_department = Department.objects.create(
            name='general',
            school= self.test_school,
            language_supports=['english']
        )
        # create level
        self.test_level = Level.objects.create(
            name='nursery',
            departments=self.test_department
        )

        # create student class
        self.student_class = Class.objects.create(
            class_name='6',
            class_range='1 to 4',
            level=self.test_level,
        )
        # create payment
        self.test_payment = PaymentDetail.objects.create(
            paypal_email='test@paypal.com',
            bank='test bank',
            account_number='1234567890',
            swift='test account'
        )

        # create a staff
        self.test_staff = Staff.objects.create(
            user=self.test_user,
            role='teacher',
            bio="test staff bio",
            payment_method=self.test_payment,
            billing_method="momo"
        )

        # create a student

        self.test_student = Student.objects.create(
            user=self.test_user,
            matricule='STU123',
            bio="test student bio",
            student_class=self.student_class,
        )



        # Create test member
        self.test_member = LibraryMember.objects.create(
            user=self.test_student,
            member_id='MEM113',
            expiry_date=timezone.now() + timedelta(days=365)
        )

        # Create test category
        self.test_category = LibraryCategory.objects.create(
            name='Fiction',
            description='Fiction books'
        )

        # Create test book
        self.test_book = Book.objects.create(
            title='Test Book 1',
            authors='Test Author',
            isbn='9781234567897',
            publication_date='2023-01-01',
            publisher='Test Publisher',
            call_number='12342424',
            language='english',
            total_copies=1,
            available_copies=0
        )
        self.test_book.categories.add(self.test_category)

        # create a librarian
        self.test_librarian = Librarian.objects.create(
          library_staff=self.test_staff,
            librarian_id='LIB123'
        )
        # Create test book copy
        self.test_book_copy = BookCopy.objects.create(
            book_copy=self.test_book,
            accession_number='COPY001',
        )

        # Create test book loan
        self.test_loan = BookLoan.objects.create(
            member=self.test_member,
            school_librarian=self.test_librarian,
            book_copy=self.test_book_copy,
            fine_amount='100.00',
            due_date='2023-01-29',
            is_returned=False
        )



        # Create test fine
        self.test_fine = Fine.objects.create(
            loan=self.test_loan,
            amount=10.50,
            reason='Late return',
            is_paid=False,
            payment_date='2024-01-23'
        )

        # Create test reservation
        self.test_reservation = Reservation.objects.create(
            member=self.test_member,
            reserver_book=self.test_book,
            expiry_date='2023-02-01',
            status=0
        )



    # Book endpoint tests
    def test_book_list(self):
        response = self.c.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_book_detail(self):
        response = self.c.get(reverse('book-detail', args=[self.test_book.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book 1')

    def test_book_create(self):
        book_data = {
            'title': 'Test Book',
            'authors': 'Test Author',
            'isbn': '9781234167817',
            'publication_date': '2023-02-12',
            'publisher': 'Test Publisher',
            'call_number': '11342124',
            'language': 'english',
            'categories': [uuid_converted(self.test_category.id)]
        }
        response = self.c.post(
            reverse('book-list'),
            data=json.dumps(book_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Book')

    def test_book_update(self):
        updated_data = {
            'title': 'Updated Test Book',
            'authors': 'Test Author',
            'isbn': '9781234567897',
            'publication_year': 2023,
            'publisher': 'Test Publisher',
            'call_number': '12342424',
            'language': 'english',
            'publication_date': '2023-01-01',
            'categories': [uuid_converted(self.test_category.id)]
        }
        response = self.c.put(
            reverse('book-detail', args=[self.test_book.id]),
            data=json.dumps(updated_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Test Book')

    def test_book_delete(self):
        response = self.c.delete(reverse('book-detail', args=[self.test_book.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Library Member endpoint tests
    def test_member_list(self):
        response = self.c.get(reverse('member-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_member_detail(self):
        response = self.c.get(reverse('member-detail', args=[self.test_member.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['member_id'], 'MEM113')

    def test_member_create(self):
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpassword'
        )
        test_student = Student.objects.create(
            user=new_user,
            matricule='STU123',
            bio="test student bio",
            student_class=self.student_class,
        )
        member_data = {
            'user': test_student.id,
            'member_id': 'MEM456',
            'expiry_date': '2024-01-01',
        }
        response = self.c.post(
            reverse('member-list'),
            data=json.dumps(member_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['member_id'], 'MEM456')

    def test_member_update(self):
        updated_data = {
            'user': self.test_user.id,
            'member_id': 'MEM123',
            'expiry_date': '2024-01-08',
        }
        response = self.c.put(
            reverse('member-detail', args=[self.test_member.id]),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['member_id'], 'MEM123')

    def test_member_delete(self):
        response = self.c.delete(reverse('member-detail', args=[self.test_member.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Book Loan endpoint tests
    def test_loan_list(self):
        response = self.c.get(reverse('loan-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_loan_detail(self):
        response = self.c.get(reverse('loan-detail', args=[self.test_loan.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_returned'], False)

    def test_loan_create(self):
        # Create a new book copy for this test
        new_book_copy = BookCopy.objects.create(
            book_copy=self.test_book,
            accession_number='COPY002',

        )

        loan_data = {
            'member': uuid_converted(self.test_member.id),
            'book_copy':uuid_converted(new_book_copy.id),
            'school_librarian':uuid_converted(self.test_librarian.id),
            'loan_date': '2023-03-01',
            'due_date': '2025-05-15',
            'is_available': False
        }
        response = self.c.post(
            reverse('loan-list'),
            data=json.dumps(loan_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['due_date'], '2025-05-15')

    def test_loan_update(self):
        updated_data = {
            'member': uuid_converted(self.test_member.id),
            'book': uuid_converted(self.test_book.id),
            'book_copy': uuid_converted(self.test_book_copy.id),
            'school_librarian': uuid_converted(self.test_librarian.id),
            'loan_date': '2023-01-15',
            'due_date': '2025-06-05',  # Extended due date
            'is_returned': False
        }
        response = self.c.put(
            reverse('loan-detail', args=[self.test_loan.id]),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['due_date'], '2025-06-05')

    def test_loan_delete(self):
        response = self.c.delete(reverse('loan-detail', args=[self.test_loan.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Category endpoint test
    def test_category_list(self):
        response = self.c.get(reverse('category'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_category_create(self):
        category_data = {
            'name': 'Non-Fiction',
            'description': 'Non-fiction books'
        }
        response = self.c.post(
            reverse('category'),
            data=json.dumps(category_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Non-Fiction')

    # Dashboard view test
    def test_dashboard(self):
        response = self.c.get(reverse('dashboard'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('current_stats', response.data)
        self.assertIn('most_borrowed_books', response.data)
        self.assertIn('members_with_overdue', response.data)
        self.assertIn('top_categories', response.data)

    # BookCopy viewset tests
    def test_bookcopy_list(self):
        response = self.c.get('/api/bookcopy/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bookcopy_detail(self):
        response = self.c.get(f'/api/bookcopy/{self.test_book_copy.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bookcopy_checkout(self):
        self.test_book_copy.status = 0
        self.test_book_copy.save()

        checkout_data = {
            'member': uuid_converted(self.test_member.id),
            'due_date': '2023-04-15'
        }
        response = self.c.post(
            f'/api/bookcopy/{self.test_book_copy.id}/checkout/',
            data=json.dumps(checkout_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bookcopy_return(self):
        return_data = {
            'condition_notes': 'Returned in good condition'
        }
        response = self.c.post(
            f'/api/bookcopy/{self.test_book_copy.id}/return_book/',
            data=json.dumps(return_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Fine viewset tests
    def test_fine_list(self):
        response = self.c.get('/api/fine/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fine_detail(self):
        response = self.c.get(f'/api/fine/{self.test_fine.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fine_pay(self):
        payment_data = {
            'payment_method': 'CARD',
            'payment_date': '2023-03-01'
        }
        response = self.c.post(
            f'/api/fine/{self.test_fine.id}/pay/',
            data=json.dumps(payment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fine_unpaid(self):
        response = self.c.get('/api/fine/unpaid/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fine_member_summary(self):
        response = self.c.get('/api/fine/member_summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    # Reservation viewset tests
    def test_reservation_list(self):
        response = self.c.get('/api/reservation/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reservation_detail(self):
        response = self.c.get(f'/api/reservation/{self.test_reservation.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reservation_cancel(self):
        response = self.c.post(
            f'/api/reservation/{self.test_reservation.id}/cancel/',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

