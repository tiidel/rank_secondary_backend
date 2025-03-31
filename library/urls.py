from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookListView, BookDetailView,
    LibraryMemberListView, LibraryMemberDetailView,
    BookLoanListView, BookLoanDetailView, FineViewSet, BookCopyViewSet, CategoryAPIView, ReservationViewSet,
    DashboardView
)
router = DefaultRouter()
router.register(r'fine', FineViewSet)
router.register(r'bookcopy', BookCopyViewSet)
router.register(r'reservation', ReservationViewSet)
urlpatterns = [
    path('library/', include(router.urls)),
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<uuid:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('members/', LibraryMemberListView.as_view(), name='member-list'),
    path('members/<uuid:pk>/', LibraryMemberDetailView.as_view(), name='member-detail'),
    path('categories/', CategoryAPIView.as_view(), name='category'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('loans/', BookLoanListView.as_view(), name='loan-list'),
    path('loans/<uuid:pk>/', BookLoanDetailView.as_view(), name='loan-detail'),
]