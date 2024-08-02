from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Book, LibraryMember, BookLoan
from .serializers import BookSerializer, LibraryMemberSerializer, BookLoanSerializer

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