from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

@register.filter
def direct_image_url(relative_path):
    return settings.BASE_URL + static(relative_path)
