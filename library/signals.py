from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from  .models import BookCopy
@receiver(post_save, sender=BookCopy)
def update_book_copy_counts_on_save(sender, instance, created, **kwargs):
    """Update the parent book's copy counts when a BookCopy is created or updated"""
    book = instance.book_copy

    # Update total_copies if a new copy was created
    if created:
        book.total_copies = book.copies.count()

    # Always update available_copies when a copy is saved
    book.available_copies = book.copies.filter(is_available=True).count()
    book.save(update_fields=['total_copies', 'available_copies'])

@receiver(post_delete, sender=BookCopy)
def update_book_copy_counts_on_delete(sender, instance, **kwargs):
    """Update the parent book's copy counts when a BookCopy is deleted"""
    book = instance.book_copy
    book.total_copies = book.copies.count()
    book.available_copies = book.copies.filter(is_available=True).count()
    book.save(update_fields=['total_copies', 'available_copies'])