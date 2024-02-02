from datetime import timedelta
from django.utils import timezone
from school.models import *


def delete_expired_items():
    expiry_date = timezone.now() - timedelta(days=60)
    expired_items = Class.objects.filter(is_delete=True, created_at__lte=expiry_date)
    expired_items.delete()