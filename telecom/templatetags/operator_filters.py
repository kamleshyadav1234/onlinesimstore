from django import template

register = template.Library()

@register.filter
def filterby(queryset, arg):
    """
    Filter queryset by field=value
    Usage: {{ operators|filterby:"is_active,True" }}
    """
    try:
        field, value = arg.split(',')
        value = value.strip()
        
        # Convert string values to appropriate types
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        
        # Apply filter
        return queryset.filter(**{field: value})
    except:
        return queryset.none()