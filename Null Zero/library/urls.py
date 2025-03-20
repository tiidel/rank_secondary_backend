from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookListView, BookDetailView,
    LibraryMemberListView, LibraryMemberDetailView,
    BookLoanListView, BookLoanDetailView, FineViewSet, BookCopyViewSet, CategoryAPIView, ReservationViewSet,
    DashboardView
)
router = DefaultRouter()
router.register(r'fines', FineViewSet)
router.register(r'book-copy', BookCopyViewSet)
router.register(r'library-member', ReservationViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('members/', LibraryMemberListView.as_view(), name='member-list'),
    path('members/<int:pk>/', LibraryMemberDetailView.as_view(), name='member-detail'),
    path('categories/', CategoryAPIView.as_view(), name='category'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('loans/', BookLoanListView.as_view(), name='loan-list'),
    path('loans/<int:pk>/', BookLoanDetailView.as_view(), name='loan-detail'),
]