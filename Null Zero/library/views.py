from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from .models import Book, LibraryMember, BookLoan, Category, BookCopy, Fine, Reservation, LibraryStatistics
from .serializers import BookSerializer, LibraryMemberSerializer, BookLoanSerializer, CategorySerializer, \
    BookCopySerializer, BookCopyCheckoutSerializer, BookCopyReturnSerializer, FineSerializer, FinePaymentSerializer, \
    ReservationSerializer, LibraryStatisticsSerializer


class CategoryAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer





class BookListView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BookDetailView(APIView):
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class LibraryMemberListView(APIView):
    def get(self, request):
        members = LibraryMember.objects.all()
        serializer = LibraryMemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LibraryMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LibraryMemberDetailView(APIView):
    def get(self, request, pk):
        member = get_object_or_404(LibraryMember, pk=pk)
        serializer = LibraryMemberSerializer(member)
        return Response(serializer.data)

    def put(self, request, pk):
        member = get_object_or_404(LibraryMember, pk=pk)
        serializer = LibraryMemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        member = get_object_or_404(LibraryMember, pk=pk)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookLoanListView(APIView):
    def get(self, request):
        loans = BookLoan.objects.all()
        serializer = BookLoanSerializer(loans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookLoanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BookLoanDetailView(APIView):
    def get(self, request, pk):
        loan = get_object_or_404(BookLoan, pk=pk)
        serializer = BookLoanSerializer(loan)
        return Response(serializer.data)

    def put(self, request, pk):
        loan = get_object_or_404(BookLoan, pk=pk)
        serializer = BookLoanSerializer(loan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        loan = get_object_or_404(BookLoan, pk=pk)
        loan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookCopyViewSet(viewsets.ModelViewSet):
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Checkout a book copy"""
        book_copy = self.get_object()
        serializer = BookCopyCheckoutSerializer(book_copy, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Book copy checked out'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Return a book copy"""
        book_copy = self.get_object()
        serializer = BookCopyReturnSerializer(book_copy, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Book copy returned'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """Mark a fine as paid"""
        fine = self.get_object()
        serializer = FinePaymentSerializer(fine, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Fine marked as paid'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def unpaid(self, request):
        """List all unpaid fines"""
        fines = Fine.objects.filter(is_paid=False)
        serializer = self.get_serializer(fines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def member_summary(self, request):
        """Get summary of fines by member"""
        from django.db.models import Sum, Count

        summaries = (
            Fine.objects
            .values('loan__member')
            .annotate(
                total_fines=Count('id'),
                total_amount=Sum('amount'),
                unpaid_amount=Sum('amount', filter=models.Q(is_paid=False))
            )
            .order_by('-total_amount')
        )

        return Response(summaries)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()
        try:
            reservation.cancel()
            return Response({'status': 'Reservation cancelled'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        """Mark a reservation as fulfilled"""
        reservation = self.get_object()
        try:
            reservation.fulfill()
            return Response({'status': 'Reservation fulfilled'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class DashboardView(APIView):
    """API view providing dashboard statistics"""

    def get(self, request):
        today = timezone.now().date()

        # Get latest statistics or generate if not available for today
        try:
            latest_stats = LibraryStatistics.objects.get(date=today)
        except LibraryStatistics.DoesNotExist:
            latest_stats = LibraryStatistics.generate_daily_stats()

        current_month = timezone.now().month
        current_year = timezone.now().year

        # Most borrowed books this month
        most_borrowed = (
            BookLoan.objects.filter(
                loan_date__month=current_month,
                loan_date__year=current_year
            )
            .values('book__title')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # Members with most overdue books
        members_with_overdue = (
            BookLoan.objects.filter(
                is_returned=False,
                due_date__lt=today
            )
            .values('member__user__username', 'member__user__first_name', 'member__user__last_name')
            .annotate(overdue_count=Count('id'))
            .order_by('-overdue_count')[:5]
        )

        # Top categories by loans
        top_categories = (
            BookLoan.objects.filter(
                loan_date__month=current_month,
                loan_date__year=current_year
            )
            .values('book__categories__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        return Response({
            'current_stats': LibraryStatisticsSerializer(latest_stats).data,
            'most_borrowed_books': most_borrowed,
            'members_with_overdue': members_with_overdue,
            'top_categories': top_categories
        })