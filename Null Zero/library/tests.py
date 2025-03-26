import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from .models import (
    Book, LibraryMember, BookLoan,
    BookCopy, Fine, Reservation, LibraryStatistics
)


@pytest.fixture
def api_client():
    """Fixture to create an API client for testing"""
    return APIClient()


@pytest.fixture
def create_book():
    """Fixture to create a sample book"""
    book = Book.objects.create(
        title="Test Book",
        author="Test Author",
        isbn="1234567890",
        description="A test book for library system"
    )
    return book


@pytest.fixture
def create_library_member(django_user_model):
    """Fixture to create a library member"""
    user = django_user_model.objects.create_user(
        username="testuser",
        password="testpass"
    )
    member = LibraryMember.objects.create(user=user)
    return member


@pytest.mark.django_db
class TestBookViews:
    def test_book_list_view(self, api_client, create_book):
        """Test retrieving list of books"""
        url = reverse('book-list')
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) > 0
        assert response.data[0]['title'] == "Test Book"

    def test_book_create_view(self, api_client):
        """Test creating a new book"""
        url = reverse('book-list')
        book_data = {
            "title": "New Test Book",
            "author": "New Test Author",
            "isbn": "0987654321",
            "description": "Another test book"
        }
        response = api_client.post(url, book_data)

        assert response.status_code == 201
        assert response.data['title'] == "New Test Book"

    def test_book_detail_view(self, api_client, create_book):
        """Test retrieving a single book by ID"""
        url = reverse('book-detail', kwargs={'pk': create_book.id})
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data['title'] == "Test Book"


@pytest.mark.django_db
class TestBookCopyViewSet:
    def test_book_copy_checkout(self, api_client, create_book, create_library_member):
        """Test checking out a book copy"""
        book_copy = BookCopy.objects.create(book=create_book, status='available')

        url = reverse('bookcopy-checkout', kwargs={'pk': book_copy.id})
        checkout_data = {
            'member': create_library_member.id,
            'loan_date': timezone.now()
        }

        response = api_client.post(url, checkout_data)

        assert response.status_code == 200
        book_copy.refresh_from_db()
        assert book_copy.status == 'checked_out'

    def test_book_copy_return(self, api_client, create_book, create_library_member):
        """Test returning a book copy"""
        book_copy = BookCopy.objects.create(book=create_book, status='checked_out')

        url = reverse('bookcopy-return-book', kwargs={'pk': book_copy.id})
        return_data = {
            'return_date': timezone.now()
        }

        response = api_client.post(url, return_data)

        assert response.status_code == 200
        book_copy.refresh_from_db()
        assert book_copy.status == 'available'


@pytest.mark.django_db
class TestFineViewSet:
    def test_fine_payment(self, api_client, create_library_member):
        """Test paying a fine"""
        loan = BookLoan.objects.create(
            member=create_library_member,
            due_date=timezone.now() - timedelta(days=5)
        )
        fine = Fine.objects.create(
            loan=loan,
            amount=10.00,
            is_paid=False
        )

        url = reverse('fine-pay', kwargs={'pk': fine.id})
        payment_data = {'payment_date': timezone.now()}

        response = api_client.post(url, payment_data)

        assert response.status_code == 200
        fine.refresh_from_db()
        assert fine.is_paid is True

    def test_unpaid_fines_list(self, api_client, create_library_member):
        """Test retrieving list of unpaid fines"""
        loan = BookLoan.objects.create(
            member=create_library_member,
            due_date=timezone.now() - timedelta(days=5)
        )
        Fine.objects.create(loan=loan, amount=10.00, is_paid=False)
        Fine.objects.create(loan=loan, amount=15.00, is_paid=False)

        url = reverse('fine-unpaid')
        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2


@pytest.mark.django_db
class TestDashboardView:
    @patch('library.models.LibraryStatistics.generate_daily_stats')
    def test_dashboard_stats_generation(self, mock_generate_stats, api_client):
        """Test dashboard view generates stats if not existing"""
        mock_stats = LibraryStatistics(
            date=timezone.now().date(),
            total_books=100,
            total_members=50
        )
        mock_generate_stats.return_value = mock_stats

        url = reverse('dashboard')
        response = api_client.get(url)

        assert response.status_code == 200
        assert 'current_stats' in response.data
        assert 'most_borrowed_books' in response.data
        assert 'members_with_overdue' in response.data
        assert 'top_categories' in response.data


@pytest.mark.django_db
class TestReservationViewSet:
    def test_reservation_cancel(self, api_client, create_book, create_library_member):
        """Test cancelling a reservation"""
        reservation = Reservation.objects.create(
            book=create_book,
            member=create_library_member,
            reservation_date=timezone.now()
        )

        url = reverse('reservation-cancel', kwargs={'pk': reservation.id})
        response = api_client.post(url)

        assert response.status_code == 200
        reservation.refresh_from_db()
        assert reservation.status == 'cancelled'

    def test_reservation_fulfill(self, api_client, create_book, create_library_member):
        """Test fulfilling a reservation"""
        reservation = Reservation.objects.create(
            book=create_book,
            member=create_library_member,
            reservation_date=timezone.now()
        )

        url = reverse('reservation-fulfill', kwargs={'pk': reservation.id})
        response = api_client.post(url)

        assert response.status_code == 200
        reservation.refresh_from_db()
        assert reservation.status == 'fulfilled'
