from django.urls import path
from .views import (
    BookListView, BookDetailView,
    LibraryMemberListView, LibraryMemberDetailView,
    BookLoanListView, BookLoanDetailView
)

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('members/', LibraryMemberListView.as_view(), name='member-list'),
    path('members/<int:pk>/', LibraryMemberDetailView.as_view(), name='member-detail'),
    path('loans/', BookLoanListView.as_view(), name='loan-list'),
    path('loans/<int:pk>/', BookLoanDetailView.as_view(), name='loan-detail'),
]