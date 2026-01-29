# your_app/templatetags/custom_filters.py
from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by arg."""
    try:
        # Handle string, int, float, Decimal
        if isinstance(value, str):
            value = float(value)
        if isinstance(arg, str):
            arg = float(arg)
        return value * arg
    except (ValueError, TypeError, AttributeError):
        try:
            return float(value) * float(arg)
        except (ValueError, TypeError):
            return 0

@register.filter(name='add')
def add(value, arg):
    """Add arg to value."""
    try:
        if isinstance(value, str):
            value = float(value)
        if isinstance(arg, str):
            arg = float(arg)
        return value + arg
    except (ValueError, TypeError, AttributeError):
        try:
            return float(value) + float(arg)
        except (ValueError, TypeError):
            return value

@register.filter(name='calculate_tax')
def calculate_tax(value, rate=0.18):
    """Calculate tax on the value."""
    try:
        if isinstance(value, str):
            value = float(value)
        tax_amount = value * float(rate)
        return round(tax_amount, 2)
    except (ValueError, TypeError):
        return 0

@register.filter(name='calculate_total_with_tax')
def calculate_total_with_tax(value, rate=0.18):
    """Calculate total with tax."""
    try:
        if isinstance(value, str):
            value = float(value)
        total = value * (1 + float(rate))
        return round(total, 2)
    except (ValueError, TypeError):
        return value

@register.filter(name='rupee_format')
def rupee_format(value):
    """Format value as Indian Rupee."""
    try:
        if isinstance(value, str):
            value = float(value)
        if value >= 10000000:  # 1 Crore
            return f"₹{value/10000000:.2f} Cr"
        elif value >= 100000:  # 1 Lakh
            return f"₹{value/100000:.2f} L"
        elif value >= 1000:  # 1 Thousand
            return f"₹{value/1000:.1f}K"
        else:
            return f"₹{value:.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"
    

# templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def filter_by_status(queryset, status):
    """Filter queryset by status"""
    return [item for item in queryset if item.status == status]

@register.filter
def get_status_class(status):
    """Get CSS class for status"""
    status_classes = {
        'completed': 'bg-success',
        'failed': 'bg-danger',
        'processing': 'bg-info',
        'pending': 'bg-warning',
        'cancelled': 'bg-secondary',
    }
    return status_classes.get(status, 'bg-secondary')


# templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def filter_by_status(queryset, status):
    """Filter queryset by status"""
    return queryset.filter(status=status)

# telecompedia/plans/templatetags/port_filters.py
from django import template
from django.db.models import Count

register = template.Library()

@register.filter
def count_by_status(queryset, status):
    """Count items with specific status in queryset"""
    try:
        # If queryset is already evaluated (like a list), filter in Python
        if hasattr(queryset, '_result_cache') or isinstance(queryset, list):
            return len([item for item in queryset if item.status == status])
        # Otherwise, filter at database level
        else:
            return queryset.filter(status=status).count()
    except:
        # Fallback to Python filtering
        return len([item for item in queryset if item.status == status])

@register.filter
def get_status_class(status):
    """Get CSS class for status"""
    status_classes = {
        'completed': 'bg-success',
        'failed': 'bg-danger',
        'processing': 'bg-info',
        'pending': 'bg-warning',
        'cancelled': 'bg-secondary',
        'draft': 'bg-secondary',
        'upc_sent': 'bg-primary',
    }
    return status_classes.get(status, 'bg-secondary')



@register.filter
def split(value, arg=','):
    """Split a string by the given argument"""
    return value.split(arg)



@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def gst_amount(value):
    """Calculate GST amount (18% of value)"""
    try:
        return float(value) * 0.18
    except (ValueError, TypeError):
        return 0

@register.filter
def total_with_gst(value):
    """Calculate total with GST (value + 18%)"""
    try:
        return float(value) * 1.18
    except (ValueError, TypeError):
        return 0