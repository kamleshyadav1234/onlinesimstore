from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Plan, PlanCategory, PlanComparison
from users.models import UserFavouritePlan
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, 
    UpdateView, DeleteView, FormView, View
)
# class PlanListView(ListView):
#     model = Plan
#     template_name = 'plans/plan_list.html'
#     context_object_name = 'plans'
#     paginate_by = 12
    
#     def get_queryset(self):
#         queryset = Plan.objects.filter(is_active=True)
        
#         # Filter by operator
#         operator_id = self.request.GET.get('operator')
#         if operator_id:
#             queryset = queryset.filter(operator_id=operator_id)
        
#         # Filter by category
#         category_id = self.request.GET.get('category')
#         if category_id:
#             queryset = queryset.filter(category_id=category_id)
        
#         # Filter by price range
#         min_price = self.request.GET.get('min_price')
#         max_price = self.request.GET.get('max_price')
#         if min_price:
#             queryset = queryset.filter(price__gte=min_price)
#         if max_price:
#             queryset = queryset.filter(price__lte=max_price)
        
#         # Filter by validity
#         validity = self.request.GET.get('validity')
#         if validity:
#             queryset = queryset.filter(validity__gte=validity)
        
#         # Sorting
#         sort_by = self.request.GET.get('sort_by', 'price')
#         if sort_by == 'price_desc':
#             queryset = queryset.order_by('-price')
#         elif sort_by == 'validity':
#             queryset = queryset.order_by('-validity')
#         elif sort_by == 'popularity':
#             queryset = queryset.filter(is_popular=True)
#         else:
#             queryset = queryset.order_by('price')
        
#         return queryset
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         from telecom.models import TelecomOperator
#         context['operators'] = TelecomOperator.objects.filter(is_active=True)
#         context['categories'] = PlanCategory.objects.all()
#         return context



# class PlanListView(ListView):
#     model = Plan
#     template_name = 'plans/plan_list.html'
#     context_object_name = 'plans'
#     paginate_by = 12
    
#     def get_queryset(self):
#         queryset = Plan.objects.filter(is_active=True)
        
#         # DEBUG: Print initial count
#         print(f"DEBUG: Initial queryset count: {queryset.count()}")
        
#         # Filter by operator
#         operator_id = self.request.GET.get('operator')
#         if operator_id:
#             print(f"DEBUG: Filtering by operator_id: {operator_id}")
#             queryset = queryset.filter(operator_id=operator_id)
        
#         # Filter by category
#         category_id = self.request.GET.get('category')
#         if category_id:
#             print(f"DEBUG: Filtering by category_id: {category_id}")
#             # Check if category exists
#             try:
#                 category = PlanCategory.objects.get(id=category_id)
#                 print(f"DEBUG: Category found: {category.name}")
#             except PlanCategory.DoesNotExist:
#                 print(f"DEBUG: Category ID {category_id} does not exist!")
            
#             queryset = queryset.filter(category_id=category_id)
#             print(f"DEBUG: After category filter, count: {queryset.count()}")
            
#             # If no results, let's check what's wrong
#             if queryset.count() == 0:
#                 print(f"DEBUG: Checking why no plans in category {category_id}:")
#                 # Check if any plans have this category
#                 all_plans_in_category = Plan.objects.filter(category_id=category_id)
#                 print(f"  Total plans with category_id={category_id}: {all_plans_in_category.count()}")
                
#                 # Check if they're active
#                 active_plans_in_category = Plan.objects.filter(category_id=category_id, is_active=True)
#                 print(f"  Active plans with category_id={category_id}: {active_plans_in_category.count()}")
                
#                 # List a few plans to see
#                 for plan in active_plans_in_category[:3]:
#                     print(f"  - {plan.name} (Active: {plan.is_active})")
        
#         # Filter by price range
#         min_price = self.request.GET.get('min_price')
#         max_price = self.request.GET.get('max_price')
#         if min_price:
#             queryset = queryset.filter(price__gte=min_price)
#         if max_price:
#             queryset = queryset.filter(price__lte=max_price)
        
#         # Filter by validity
#         validity = self.request.GET.get('validity')
#         if validity:
#             queryset = queryset.filter(validity__gte=validity)
        
#         # Sorting
#         sort_by = self.request.GET.get('sort_by', 'price')
#         if sort_by == 'price_desc':
#             queryset = queryset.order_by('-price')
#         elif sort_by == 'validity':
#             queryset = queryset.order_by('-validity')
#         elif sort_by == 'popularity':
#             queryset = queryset.filter(is_popular=True)
#         else:
#             queryset = queryset.order_by('price')
        
#         print(f"DEBUG: Final queryset count: {queryset.count()}")
#         return queryset
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         from telecom.models import TelecomOperator
#         context['operators'] = TelecomOperator.objects.filter(is_active=True)
#         context['categories'] = PlanCategory.objects.all()
        
#         # Add category counts for display
#         for category in context['categories']:
#             category.plan_count = Plan.objects.filter(category=category, is_active=True).count()
        
#         return context




class PlanListView(ListView):
    model = Plan
    template_name = 'plans/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Plan.objects.filter(is_active=True)
        
        # DEBUG: Print initial count
        print(f"DEBUG: Initial queryset count: {queryset.count()}")
        
        # Filter by operator
        operator_id = self.request.GET.get('operator')
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Handle price_range parameter (from URL: price_range=100-300)
        price_range = self.request.GET.get('price_range')
        if price_range:
            try:
                # Split the price range like "100-300"
                parts = price_range.split('-')
                if len(parts) == 2:
                    min_price_str, max_price_str = parts
                    # Convert to integers, handle empty strings
                    if min_price_str and min_price_str.isdigit():
                        queryset = queryset.filter(price__gte=int(min_price_str))
                    if max_price_str and max_price_str.isdigit():
                        queryset = queryset.filter(price__lte=int(max_price_str))
                elif len(parts) == 1 and parts[0].isdigit():
                    # If only one price is provided, treat it as minimum price
                    queryset = queryset.filter(price__gte=int(parts[0]))
            except (ValueError, AttributeError, IndexError) as e:
                print(f"DEBUG: Error parsing price_range {price_range}: {e}")
        
        # ALSO handle min_price and max_price separately (for form submissions)
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price and min_price.isdigit():
            queryset = queryset.filter(price__gte=int(min_price))
        if max_price and max_price.isdigit():
            queryset = queryset.filter(price__lte=int(max_price))
        
        # Filter by plan_type (if exists in your form)
        plan_type = self.request.GET.get('plan_type')
        if plan_type:
            # Assuming plan_type is stored somewhere or you need to filter differently
            # You might need to adjust this based on your model structure
            pass
        
        # Filter by data allowance
        data = self.request.GET.get('data')
        if data:
            # You might need custom filtering for data allowance
            # For example: "2GB", "Unlimited", etc.
            queryset = queryset.filter(data_allowance__icontains=data)
        
        # Filter by validity
        validity = self.request.GET.get('validity')
        if validity:
            queryset = queryset.filter(validity__gte=validity)
        
        # Filter by calls
        calls = self.request.GET.get('calls')
        if calls:
            queryset = queryset.filter(voice_calls__icontains=calls)
        
        # Sorting
        sort_param = self.request.GET.get('sort', 'price')  # Changed from 'sort_by' to 'sort' to match URL
        if sort_param == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_param == 'validity':
            queryset = queryset.order_by('-validity')
        elif sort_param == 'popularity':
            queryset = queryset.filter(is_popular=True)
        else:
            queryset = queryset.order_by('price')
        
        print(f"DEBUG: Final queryset count: {queryset.count()}")
        print(f"DEBUG: Applied filters - price_range: {price_range}, min_price: {min_price}, max_price: {max_price}")
        
        # Debug: Check some plan prices
        if price_range or min_price or max_price:
            sample_plans = queryset[:5]
            for plan in sample_plans:
                print(f"DEBUG: Sample plan - {plan.name}: ₹{plan.price}")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from telecom.models import TelecomOperator
        context['operators'] = TelecomOperator.objects.filter(is_active=True)
        context['categories'] = PlanCategory.objects.all()
        
        # Pass current filter values back to template
        context['current_operator'] = self.request.GET.get('operator', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_price_range'] = self.request.GET.get('price_range', '')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_sort'] = self.request.GET.get('sort', 'price')
        
        # Add category counts for display
        for category in context['categories']:
            category.plan_count = Plan.objects.filter(category=category, is_active=True).count()
        
        return context








class PlanDetailView(DetailView):
    model = Plan
    template_name = 'plans/plan_detail.html'
    context_object_name = 'plan'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get similar plans
        context['similar_plans'] = Plan.objects.filter(
            operator=self.object.operator,
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        
        # Check if user has this in favourites
        if self.request.user.is_authenticated:
            context['is_favourite'] = UserFavouritePlan.objects.filter(
                user=self.request.user,
                plan=self.object
            ).exists()
        
        return context

class CategoryPlansView(ListView):
    template_name = 'plans/category_plans.html'
    context_object_name = 'plans'
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(PlanCategory, name__iexact=category_slug.replace('-', ' '))
        return Plan.objects.filter(category=category, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        context['category'] = get_object_or_404(PlanCategory, name__iexact=category_slug.replace('-', ' '))
        return context

# views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Plan

class ComparePlansView(ListView):
    template_name = 'plans/compare.html'
    context_object_name = 'plans'
    
    def get_queryset(self):
        # Get plan IDs from query parameters
        plan_ids = self.request.GET.get('plans', '').split(',')
        plan_ids = [int(pid) for pid in plan_ids if pid.isdigit()]
        
        if 2 <= len(plan_ids) <= 4:
            # Get the plans to compare
            plans = Plan.objects.filter(
                id__in=plan_ids, 
                is_active=True
            ).select_related('operator', 'category')
            
            # Calculate price per day for each plan
            for plan in plans:
                plan.price_per_day = plan.price / plan.validity
            
            return plans
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context here
        return context

class ToggleFavouriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        plan_id = request.POST.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id)
        
        favourite, created = UserFavouritePlan.objects.get_or_create(
            user=request.user,
            plan=plan
        )
        
        if not created:
            favourite.delete()
            is_favourite = False
        else:
            is_favourite = True
        
        return JsonResponse({
            'success': True,
            'is_favourite': is_favourite,
            'message': 'Added to favourites' if is_favourite else 'Removed from favourites'
        })
    

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Plan, PlanComparison

class PlanComparisonView(ListView):
    template_name = 'plans/plan_comparison.html'
    context_object_name = 'comparisons'
    
    def get_queryset(self):
        # Get plan IDs from query parameters
        plan_ids = self.request.GET.get('plans', '').split(',')
        plan_ids = [int(pid) for pid in plan_ids if pid.isdigit()]
        
        if len(plan_ids) >= 2:
            # Get the plans to compare
            self.plans_to_compare = Plan.objects.filter(id__in=plan_ids)
            
            # Get existing comparisons or create new context
            comparisons = []
            for i in range(len(plan_ids)):
                for j in range(i+1, len(plan_ids)):
                    try:
                        comparison = PlanComparison.objects.get(
                            plan1_id=plan_ids[i],
                            plan2_id=plan_ids[j]
                        )
                        comparisons.append(comparison)
                    except PlanComparison.DoesNotExist:
                        # Create a placeholder comparison
                        plan1 = get_object_or_404(Plan, id=plan_ids[i])
                        plan2 = get_object_or_404(Plan, id=plan_ids[j])
                        comparisons.append({
                            'plan1': plan1,
                            'plan2': plan2,
                            'comparison_points': 'No comparison data available yet.'
                        })
            return comparisons
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = getattr(self, 'plans_to_compare', [])
        return context


# Or a simpler version if you don't have PlanComparison model:
def plan_comparison_simple(request):
    plan_ids = request.GET.get('plans', '').split(',')
    plan_ids = [int(pid) for pid in plan_ids if pid.isdigit()]
    
    plans = Plan.objects.filter(id__in=plan_ids).select_related('operator', 'category')
    
    context = {
        'plans': plans,
        'selected_plan_ids': plan_ids,
    }
    return render(request, 'plans/plan_comparison.html', context)


# plans/views.py (add these views)
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.db import transaction
from io import BytesIO
from .models import Plan, PlanCategory, TelecomOperator

@login_required
@permission_required('plans.add_plan', raise_exception=True)
def export_plans_excel(request):
    """Export all plans to Excel"""
    plans = Plan.objects.all().select_related('operator', 'category')
    
    # Create DataFrame
    data = []
    for plan in plans:
        data.append({
            'Operator': plan.operator.name,
            'Operator ID': plan.operator.id,
            'Category': plan.category.name if plan.category else '',
            'Category ID': plan.category.id if plan.category else '',
            'Plan Name': plan.name,
            'Description': plan.description,
            'Price': float(plan.price),
            'Validity': plan.validity,
            'Validity Unit': plan.validity_unit,
            'Data Allowance': plan.data_allowance,
            'Voice Calls': plan.voice_calls,
            'SMS': plan.sms,
            'OTT Benefits': plan.ott_benefits,
            'Other Benefits': plan.other_benefits,
            'Popular': plan.is_popular,
            'Featured': plan.is_featured,
            'Active': plan.is_active,
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Plans', index=False)
        
        # Add operators sheet
        operators = TelecomOperator.objects.all()
        operators_data = []
        for op in operators:
            operators_data.append({
                'ID': op.id,
                'Name': op.name,
                'Type': op.operator_type,
                'Website': op.website,
                'Customer Care': op.customer_care,
                'Active': op.is_active,
            })
        
        op_df = pd.DataFrame(operators_data)
        op_df.to_excel(writer, sheet_name='Operators', index=False)
        
        # Add categories sheet
        categories = PlanCategory.objects.all()
        categories_data = []
        for cat in categories:
            categories_data.append({
                'ID': cat.id,
                'Name': cat.name,
                'Type': cat.category_type,
                'Icon': cat.icon,
            })
        
        cat_df = pd.DataFrame(categories_data)
        cat_df.to_excel(writer, sheet_name='Categories', index=False)
    
    output.seek(0)
    
    # Create HTTP response
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=telecom_plans.xlsx'
    return response


@login_required
@permission_required('plans.add_plan', raise_exception=True)
def import_plans_excel(request):
    """Import plans from Excel file"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            excel_file = request.FILES['excel_file']
            
            # Read Excel file
            xls = pd.ExcelFile(excel_file)
            
            # Read operators sheet if exists
            operators_df = pd.read_excel(xls, sheet_name='Operators') if 'Operators' in xls.sheet_names else None
            
            # Read categories sheet if exists
            categories_df = pd.read_excel(xls, sheet_name='Categories') if 'Categories' in xls.sheet_names else None
            
            # Read plans sheet
            plans_df = pd.read_excel(xls, sheet_name='Plans')
            
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                # Process operators if sheet exists
                if operators_df is not None:
                    for _, row in operators_df.iterrows():
                        try:
                            operator, created = TelecomOperator.objects.update_or_create(
                                id=row['ID'],
                                defaults={
                                    'name': row['Name'],
                                    'operator_type': row['Type'],
                                    'website': row['Website'],
                                    'customer_care': row['Customer Care'],
                                    'is_active': bool(row['Active']) if pd.notna(row.get('Active')) else True,
                                }
                            )
                        except Exception as e:
                            errors.append(f"Operator {row.get('Name', 'Unknown')}: {str(e)}")
                            error_count += 1
                
                # Process categories if sheet exists
                if categories_df is not None:
                    for _, row in categories_df.iterrows():
                        try:
                            category, created = PlanCategory.objects.update_or_create(
                                id=row['ID'],
                                defaults={
                                    'name': row['Name'],
                                    'category_type': row['Type'],
                                    'icon': row.get('Icon', 'fas fa-tag'),
                                }
                            )
                        except Exception as e:
                            errors.append(f"Category {row.get('Name', 'Unknown')}: {str(e)}")
                            error_count += 1
                
                # Process plans
                for _, row in plans_df.iterrows():
                    try:
                        # Get operator
                        operator_id = row.get('Operator ID')
                        if pd.isna(operator_id):
                            # Try to get by name
                            operator = TelecomOperator.objects.filter(name=row['Operator']).first()
                        else:
                            operator = TelecomOperator.objects.filter(id=int(operator_id)).first()
                        
                        if not operator:
                            errors.append(f"Plan {row.get('Plan Name')}: Operator not found")
                            error_count += 1
                            continue
                        
                        # Get category
                        category = None
                        category_id = row.get('Category ID')
                        if pd.notna(category_id):
                            category = PlanCategory.objects.filter(id=int(category_id)).first()
                        elif pd.notna(row.get('Category')):
                            category = PlanCategory.objects.filter(name=row['Category']).first()
                        
                        # Create or update plan
                        plan, created = Plan.objects.update_or_create(
                            operator=operator,
                            name=row['Plan Name'],
                            defaults={
                                'category': category,
                                'description': row['Description'] if pd.notna(row.get('Description')) else '',
                                'price': row['Price'],
                                'validity': int(row['Validity']) if pd.notna(row.get('Validity')) else 30,
                                'validity_unit': row.get('Validity Unit', 'days'),
                                'data_allowance': row['Data Allowance'] if pd.notna(row.get('Data Allowance')) else '',
                                'voice_calls': row['Voice Calls'] if pd.notna(row.get('Voice Calls')) else '',
                                'sms': row['SMS'] if pd.notna(row.get('SMS')) else '',
                                'ott_benefits': row['OTT Benefits'] if pd.notna(row.get('OTT Benefits')) else '',
                                'other_benefits': row['Other Benefits'] if pd.notna(row.get('Other Benefits')) else '',
                                'is_popular': bool(row['Popular']) if pd.notna(row.get('Popular')) else False,
                                'is_featured': bool(row['Featured']) if pd.notna(row.get('Featured')) else False,
                                'is_active': bool(row['Active']) if pd.notna(row.get('Active')) else True,
                            }
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Plan {row.get('Plan Name', 'Unknown')}: {str(e)}")
                        error_count += 1
            
            # Show success/error messages
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} plans!')
            if error_count > 0:
                messages.error(request, f'Failed to import {error_count} records. Check errors below.')
                for error in errors[:10]:  # Show first 10 errors
                    messages.warning(request, error)
            
            return redirect('plan_list')
            
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
    
    return render(request, 'plans/import_excel.html')


@login_required
@permission_required('plans.add_plan', raise_exception=True)
def download_template(request):
    """Download Excel template for plan import"""
    # Create sample data for template
    template_data = [
        {
            'Operator': 'Jio',
            'Operator ID': 1,
            'Category': 'Prepaid',
            'Category ID': 1,
            'Plan Name': 'Sample Plan ₹299',
            'Description': 'Unlimited calls + 1.5GB/day data',
            'Price': 299.00,
            'Validity': 28,
            'Validity Unit': 'days',
            'Data Allowance': '1.5GB per day',
            'Voice Calls': 'Unlimited',
            'SMS': '100 SMS per day',
            'OTT Benefits': 'JioTV, JioCinema',
            'Other Benefits': 'Free hello tunes',
            'Popular': True,
            'Featured': True,
            'Active': True,
        }
    ]
    
    df = pd.DataFrame(template_data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Plans', index=False)
        
        # Add instructions sheet
        instructions = [
            ['INSTRUCTIONS:', ''],
            ['1. Fill data in the "Plans" sheet', ''],
            ['2. Operator ID or Operator name is required', ''],
            ['3. Category ID or Category name is optional', ''],
            ['4. Validity Unit can be: days, months, year', ''],
            ['5. For boolean fields (Popular, Featured, Active):', 'Use TRUE or FALSE'],
            ['6. Do not change column headers', ''],
            ['7. Save file as .xlsx format before uploading', ''],
        ]
        
        instr_df = pd.DataFrame(instructions)
        instr_df.to_excel(writer, sheet_name='Instructions', index=False, header=False)
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=plan_import_template.xlsx'
    return response


