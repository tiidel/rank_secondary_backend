from rest_framework import serializers
from .models import Book, LibraryMember, BookLoan

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class LibraryMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryMember
        fields = '__all__'

class BookLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLoan
        fields = '__all__'