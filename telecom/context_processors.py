from .models import TelecomOperator
from plans.models import PlanCategory

def global_data(request):
    """Add global data to all templates"""
    try:
        return {
            'all_operators': TelecomOperator.objects.filter(is_active=True),
            'all_categories': PlanCategory.objects.all(),
        }
    except:
        # Return empty dict if models aren't ready yet (during initial setup)
        return {
            'all_operators': [],
            'all_categories': [],
        }