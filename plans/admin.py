from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import  PlanCategory, Plan, PlanComparison, PortRequest,NewConnectionRequest,SIMReplacementRequest

admin.site.register(PortRequest)
admin.site.register(NewConnectionRequest)
admin.site.register(SIMReplacementRequest)






@admin.register(PlanCategory)
class PlanCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type']
    list_filter = ['category_type']
    search_fields = ['name', 'description']

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'operator', 'category', 'plan_type', 'price', 'validity', 'is_popular', 'is_active']
    list_filter = ['is_active', 'is_popular', 'category', 'operator', 'plan_type']  # Added plan_type here
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_popular', 'is_active', 'plan_type']  # Added plan_type here
    filter_horizontal = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('operator', 'category', 'plan_type', 'name', 'description', 'price')  # Added plan_type here
        }),
        ('Validity', {
            'fields': ('validity', 'validity_unit')
        }),
        ('Special Benefits', {
            'fields': ('port_in_bonus', 'new_connection_bonus'),  # Added special benefits
            'classes': ('collapse',),  # Makes this section collapsible
        }),
        ('Plan Features', {
            'fields': ('data_allowance', 'voice_calls', 'sms', 'ott_benefits', 'other_benefits')
        }),
        ('Status', {
            'fields': ('is_popular', 'is_featured', 'is_active')
        }),
    )
    
    # You can also add custom methods to display the plan type
    def get_plan_type_display(self, obj):
        return obj.get_plan_type_display()
    get_plan_type_display.short_description = 'Plan Type'
    
    # Optional: Add actions for bulk operations
    actions = ['make_new_connection_plans', 'make_port_in_plans']
    
    def make_new_connection_plans(self, request, queryset):
        updated = queryset.update(plan_type='new_connection')
        self.message_user(request, f'{updated} plans marked as New Connection plans.')
    make_new_connection_plans.short_description = "Mark selected as New Connection plans"
    
    def make_port_in_plans(self, request, queryset):
        updated = queryset.update(plan_type='port_in')
        self.message_user(request, f'{updated} plans marked as Port-in plans.')
    make_port_in_plans.short_description = "Mark selected as Port-in plans"

@admin.register(PlanComparison)
class PlanComparisonAdmin(admin.ModelAdmin):
    list_display = ['plan1', 'plan2', 'created_at']
    list_filter = ['created_at']
    search_fields = ['plan1__name', 'plan2__name', 'comparison_points']