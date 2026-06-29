from django.shortcuts import render

# Create your views here.
# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from payments.models import Payment
from users.models import CustomUser, UserPlanHistory, UserFavouritePlan
from plans.models import (Plan, TelecomOperator, PlanCategory,
                          PortRequest, NewConnectionRequest, SIMReplacementRequest, 
                           PlanComparison)
from .models import AdminLog, AdminNotification, AdminSetting

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

def admin_login(request):
    if request.user.is_authenticated and request.user.user_type == 'admin':
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.user_type == 'admin':
            login(request, user)
            
            # Log admin login
            AdminLog.objects.create(
                admin=user,
                action_type='login',
                model_name='User',
                object_id=str(user.id),
                details='Admin logged in',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return redirect('admin_panel:dashboard')
        else:
            return render(request, 'admin_panel/login.html', {'error': 'Invalid credentials or not authorized'})
    
    return render(request, 'admin_panel/login.html')

@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    logout(request)
    return redirect('admin_panel:admin_login')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get counts
    total_users = CustomUser.objects.count()
    total_plans = Plan.objects.filter(is_active=True).count()
    total_operators = TelecomOperator.objects.filter(is_active=True).count()
    total_payments = Payment.objects.filter(payment_status='completed').count()
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Recent activities
    recent_activities = AdminLog.objects.all()[:10]
    
    # Pending requests
    pending_port_requests = PortRequest.objects.filter(status__in=['pending', 'upc_sent']).count()
    pending_new_connections = NewConnectionRequest.objects.filter(status='pending').count()
    pending_sim_replacements = SIMReplacementRequest.objects.filter(status='pending').count()
    
    # Revenue by month (last 6 months)
    today = timezone.now().date()
    revenue_data = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=31)).replace(day=1)
        
        monthly_revenue = Payment.objects.filter(
            payment_status='completed',
            payment_date__gte=month_start,
            payment_date__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        revenue_data.append({
            'month': month_start.strftime('%b'),
            'revenue': float(monthly_revenue)
        })
    
    context = {
        'total_users': total_users,
        'total_plans': total_plans,
        'total_operators': total_operators,
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'recent_activities': recent_activities,
        'pending_port_requests': pending_port_requests,
        'pending_new_connections': pending_new_connections,
        'pending_sim_replacements': pending_sim_replacements,
        'revenue_data': json.dumps(revenue_data),
        'page_title': 'Dashboard',
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def users_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Filters
    user_type = request.GET.get('user_type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # User stats
    user_stats = {
        'total': users.count(),
        'customers': users.filter(user_type='customer').count(),
        'agents': users.filter(user_type='agent').count(),
        'admins': users.filter(user_type='admin').count(),
    }
    
    context = {
        'users': users,
        'user_stats': user_stats,
        'page_title': 'Users Management',
        'current_filter': user_type,
        'search_query': search,
    }
    return render(request, 'admin_panel/users/list.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Get user's plans
    user_plans = UserPlanHistory.objects.filter(user=user)
    
    # Get user's payments
    payments = Payment.objects.filter(user=user)
    
    # Get user's requests
    port_requests = PortRequest.objects.filter(user=user)
    new_connections = NewConnectionRequest.objects.filter(user=user)
    sim_replacements = SIMReplacementRequest.objects.filter(user=user)
    
    context = {
        'user': user,
        'user_plans': user_plans,
        'payments': payments,
        'port_requests': port_requests,
        'new_connections': new_connections,
        'sim_replacements': sim_replacements,
        'page_title': f'User: {user.display_name}',
    }
    return render(request, 'admin_panel/users/detail.html', context)

@login_required
@user_passes_test(is_admin)
def plans_list(request):
    plans = Plan.objects.all().select_related('operator', 'category')
    
    # Filters
    operator = request.GET.get('operator')
    if operator:
        plans = plans.filter(operator_id=operator)
    
    plan_type = request.GET.get('plan_type')
    if plan_type:
        plans = plans.filter(plan_type=plan_type)
    
    is_active = request.GET.get('is_active')
    if is_active:
        plans = plans.filter(is_active=is_active == 'true')
    
    search = request.GET.get('search')
    if search:
        plans = plans.filter(name__icontains=search)
    
    operators = TelecomOperator.objects.filter(is_active=True)
    
    context = {
        'plans': plans,
        'operators': operators,
        'plan_types': Plan.PLAN_TYPE_CHOICES,
        'page_title': 'Plans Management',
        'search_query': search,
    }
    return render(request, 'admin_panel/plans/list.html', context)

@login_required
@user_passes_test(is_admin)
def plan_create(request):
    if request.method == 'POST':
        operator_id = request.POST.get('operator')
        category_id = request.POST.get('category')
        plan_type = request.POST.get('plan_type')
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        featured_price = request.POST.get('featured_price')
        validity = request.POST.get('validity')
        validity_unit = request.POST.get('validity_unit')
        data_allowance = request.POST.get('data_allowance')
        voice_calls = request.POST.get('voice_calls')
        sms = request.POST.get('sms')
        ott_benefits = request.POST.get('ott_benefits')
        other_benefits = request.POST.get('other_benefits')
        is_popular = request.POST.get('is_popular') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        plan = Plan.objects.create(
            operator_id=operator_id,
            category_id=category_id or None,
            plan_type=plan_type,
            name=name,
            description=description,
            price=price,
            featured_price=featured_price,
            validity=validity,
            validity_unit=validity_unit,
            data_allowance=data_allowance,
            voice_calls=voice_calls,
            sms=sms,
            ott_benefits=ott_benefits,
            other_benefits=other_benefits,
            is_popular=is_popular,
            is_featured=is_featured,
            is_active=is_active,
        )
        
        # Log action
        AdminLog.objects.create(
            admin=request.user,
            action_type='create',
            model_name='Plan',
            object_id=str(plan.id),
            details=f'Created plan: {plan.name}',
        )
        
        return redirect('plan_detail', plan_id=plan.id)
    
    operators = TelecomOperator.objects.filter(is_active=True)
    categories = PlanCategory.objects.all()
    
    context = {
        'operators': operators,
        'categories': categories,
        'plan_types': Plan.PLAN_TYPE_CHOICES,
        'validity_units': Plan.VALIDITY_UNITS,
        'page_title': 'Create New Plan',
    }
    return render(request, 'admin_panel/plans/create.html', context)

@login_required
@user_passes_test(is_admin)
def plan_detail(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        # Update plan
        plan.name = request.POST.get('name')
        plan.description = request.POST.get('description')
        plan.price = request.POST.get('price')
        plan.featured_price = request.POST.get('featured_price')
        plan.validity = request.POST.get('validity')
        plan.validity_unit = request.POST.get('validity_unit')
        plan.data_allowance = request.POST.get('data_allowance')
        plan.voice_calls = request.POST.get('voice_calls')
        plan.sms = request.POST.get('sms')
        plan.ott_benefits = request.POST.get('ott_benefits')
        plan.other_benefits = request.POST.get('other_benefits')
        plan.is_popular = request.POST.get('is_popular') == 'on'
        plan.is_featured = request.POST.get('is_featured') == 'on'
        plan.is_active = request.POST.get('is_active') == 'on'
        plan.save()
        
        # Log action
        AdminLog.objects.create(
            admin=request.user,
            action_type='update',
            model_name='Plan',
            object_id=str(plan.id),
            details=f'Updated plan: {plan.name}',
        )
        
        return redirect('plan_detail', plan_id=plan.id)
    
    context = {
        'plan': plan,
        'validity_units': Plan.VALIDITY_UNITS,
        'page_title': f'Plan: {plan.name}',
    }
    return render(request, 'admin_panel/plans/detail.html', context)

@login_required
@user_passes_test(is_admin)
def payments_list(request):
    payments = Payment.objects.all().select_related('user', 'plan')
    
    # Filters
    status = request.GET.get('status')
    if status:
        payments = payments.filter(payment_status=status)
    
    payment_type = request.GET.get('payment_type')
    if payment_type:
        payments = payments.filter(payment_type=payment_type)
    
    search = request.GET.get('search')
    if search:
        payments = payments.filter(
            Q(transaction_id__icontains=search) |
            Q(bill_number__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Payment stats
    payment_stats = {
        'total': payments.count(),
        'completed': payments.filter(payment_status='completed').count(),
        'pending': payments.filter(payment_status='pending').count(),
        'failed': payments.filter(payment_status='failed').count(),
        'refunded': payments.filter(payment_status='refunded').count(),
        'total_revenue': payments.filter(payment_status='completed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0'),
    }
    
    context = {
        'payments': payments,
        'payment_stats': payment_stats,
        'payment_statuses': Payment.PAYMENT_STATUS,
        'payment_types': Payment.PAYMENT_TYPES,
        'page_title': 'Payments Management',
        'search_query': search,
    }
    return render(request, 'admin_panel/payments/list.html', context)

@login_required
@user_passes_test(is_admin)
def pending_requests(request):
    # Port Requests
    port_requests = PortRequest.objects.filter(
        status__in=['pending', 'upc_sent', 'documents_uploaded']
    ).select_related('user', 'current_operator', 'new_operator', 'selected_plan')
    
    # New Connection Requests
    new_connections = NewConnectionRequest.objects.filter(
        status__in=['pending', 'document_verification']
    ).select_related('user', 'operator', 'selected_plan')
    
    # SIM Replacement Requests
    sim_replacements = SIMReplacementRequest.objects.filter(
        status='pending'
    ).select_related('user')
    
    context = {
        'port_requests': port_requests,
        'new_connections': new_connections,
        'sim_replacements': sim_replacements,
        'page_title': 'Pending Requests',
    }
    return render(request, 'admin_panel/requests/pending.html', context)

@login_required
@user_passes_test(is_admin)
def request_action(request, request_type, request_id):
    if request_type == 'port':
        req = get_object_or_404(PortRequest, id=request_id)
    elif request_type == 'new_connection':
        req = get_object_or_404(NewConnectionRequest, id=request_id)
    elif request_type == 'sim':
        req = get_object_or_404(SIMReplacementRequest, id=request_id)
    else:
        return JsonResponse({'error': 'Invalid request type'}, status=400)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            if request_type == 'port':
                req.status = 'documents_uploaded'
            elif request_type == 'new_connection':
                req.status = 'document_verification'
            elif request_type == 'sim':
                req.status = 'approved'
        elif action == 'reject':
            req.status = 'rejected'
        elif action == 'process':
            if request_type == 'port':
                req.status = 'processing'
            elif request_type == 'new_connection':
                req.status = 'sim_dispatch'
        elif action == 'complete':
            if request_type == 'port':
                req.status = 'completed'
            elif request_type == 'new_connection':
                req.status = 'activated'
            elif request_type == 'sim':
                req.status = 'dispatched'
        
        req.notes = notes
        req.save()
        
        # Log action
        AdminLog.objects.create(
            admin=request.user,
            action_type=action,
            model_name=request_type.capitalize(),
            object_id=str(req.id),
            details=f'{action.capitalize()} {request_type} request: {req}',
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
@user_passes_test(is_admin)
def reports_view(request):
    from decimal import Decimal
    
    # Get date range
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today.replace(day=1)
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
    else:
        start_date = None
    
    # Base queryset for payments
    payments = Payment.objects.filter(payment_status='completed')
    if start_date:
        payments = payments.filter(payment_date__date__gte=start_date)
    
    # Revenue by operator
    revenue_by_operator = {}
    for operator in TelecomOperator.objects.filter(is_active=True):
        revenue = payments.filter(plan__operator=operator).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        if revenue > 0:
            revenue_by_operator[operator.name] = float(revenue)
    
    # Revenue by plan type
    revenue_by_plan_type = {}
    for plan_type, label in Plan.PLAN_TYPE_CHOICES:
        revenue = payments.filter(plan__plan_type=plan_type).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        if revenue > 0:
            revenue_by_plan_type[label] = float(revenue)
    
    # User registrations by month
    user_registrations = []
    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=31)).replace(day=1)
        
        count = CustomUser.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        
        user_registrations.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    context = {
        'period': period,
        'revenue_by_operator': json.dumps(revenue_by_operator),
        'revenue_by_plan_type': json.dumps(revenue_by_plan_type),
        'user_registrations': json.dumps(user_registrations),
        'page_title': 'Reports',
    }
    return render(request, 'admin_panel/reports/index.html', context)

@login_required
@user_passes_test(is_admin)
def settings_view(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                setting, created = AdminSetting.objects.get_or_create(
                    setting_key=setting_key,
                    defaults={'setting_value': value}
                )
                if not created:
                    setting.setting_value = value
                    setting.save()
        
        return redirect('admin_panel:settings')
    
    # Get all settings grouped by type
    settings = AdminSetting.objects.all().order_by('setting_type')
    settings_by_type = {}
    for setting in settings:
        if setting.setting_type not in settings_by_type:
            settings_by_type[setting.setting_type] = []
        settings_by_type[setting.setting_type].append(setting)
    
    context = {
        'settings_by_type': settings_by_type,
        'setting_types': AdminSetting.SETTING_TYPES,
        'page_title': 'Settings',
    }
    return render(request, 'admin_panel/settings/index.html', context)