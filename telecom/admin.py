from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TelecomOperator, ServiceArea

@admin.register(TelecomOperator)
class TelecomOperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'operator_type', 'customer_care', 'is_active']
    list_filter = ['operator_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {}
    list_editable = ['is_active']

@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ['operator', 'state', 'city', 'availability']
    list_filter = ['state', 'availability', 'operator']
    search_fields = ['city', 'pincodes']
    list_editable = ['availability']