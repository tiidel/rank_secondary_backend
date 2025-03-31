import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from .models import Book, LibraryMember, BookLoan, LibraryCategory, BookCopy, Fine, Reservation, LibraryStatistics


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def create(self, validated_data):
        categories = validated_data.pop('categories')
        book = Book.objects.create(**validated_data)
        if categories:
            book.categories.add(*categories)

        return book


class LibraryMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryMember
        fields = '__all__'


class BookLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLoan
        fields = '__all__'
        read_only_fields = ['fine_amount']

    def validate(self, data):
        # Check if the book copy is available (if creating a new loan)
        if self.instance is None and 'book_copy' in data:
            book_copy = data['book_copy']
            if not book_copy.is_available:
                raise serializers.ValidationError(
                    {"book_copy": "This book copy is not available for loan"}
                )

        # Validate due date is in the future for new loans
        if self.instance is None and 'due_date' in data:
            if data['due_date'] < datetime.date.today():
                raise serializers.ValidationError(
                    {"due_date": "Due date cannot be in the past"}
                )

        return data


class BookCopySerializer(serializers.ModelSerializer):
    book = PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = BookCopy
        fields = ['id', 'accession_number', 'is_available', 'book']


class BookCopyCheckoutSerializer(serializers.Serializer):
    book = PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = BookCopy
        fields = ['id', 'accession_number', 'book']

    def update(self, instance, validated_data):
        try:
            instance.checkout()
            return instance
        except ValueError as e:
            raise ValidationError(str(e))


class BookCopyReturnSerializer(serializers.ModelSerializer):
    book = PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = BookCopy
        fields = ['id', 'accession_number', 'book']

    def update(self, instance, validated_data):
        try:
            instance.return_book()
            return instance
        except ValueError as e:
            raise ValidationError(str(e))


class FineSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    book_title = serializers.SerializerMethodField()

    class Meta:
        model = Fine
        fields = ['id', 'loan', 'amount', 'reason', 'date_issued','is_paid', 'payment_date', 'member_name', 'book_title']


    def get_member_name(self, obj):

        return obj.loan.member.user.get_full_name()

    def get_book_title(self, obj):
        return obj.loan.book_copy.book_copy.title

    def validate(self, data):
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError({"amount": "Fine amount must be greater than zero"})

        if self.instance and not self.instance.is_paid and data.get('is_paid', False):
            data['payment_date'] = timezone.now()

        return data


class FinePaymentSerializer(serializers.Serializer):
    class Meta:
        model = Fine
        fields = ['id', 'amount', 'reason']
    def update(self, instance, validated_data):
        try:
            instance.mark_as_paid()
            return instance
        except ValueError as e:
            raise serializers.ValidationError(str(e))


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryCategory
        fields = ['id', 'name', 'description']


class ReservationSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    book_title = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            'id', 'reserver_book', 'member', 'reservation_date', 'expiry_date',
            'status', 'member_name', 'book_title'
        ]
        read_only_fields = ['reservation_date', 'status']

    def get_member_name(self, obj):
        return obj.member.user.get_full_name()

    def get_book_title(self, obj):
        return obj.book_copy.title

    def validate(self, data):
        book = data.get('book')
        if book and book.available_copies > 0:
            raise serializers.ValidationError(
                {"book": "Cannot reserve a book that is currently available"}
            )

        # Check if member has too many pending reservations
        member = data.get('member')
        if member:
            pending_count = Reservation.objects.filter(
                member=member,
                status='PENDING'
            ).count()

            if pending_count >= 5:
                raise serializers.ValidationError(
                    {"member": "Member cannot have more than 5 pending reservations"}
                )

        return data


class LibraryStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryStatistics
        fields = '__all__'