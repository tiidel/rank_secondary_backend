
from django import template

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
    """Attempts to divide the first argument by the second."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return None  # or return an appropriate value or error message

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # handle the case where conversion to float fails