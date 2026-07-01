from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
import requests
from .models import CustomUser, UserPlanHistory, UserFavouritePlan
from plans.models import Plan, SIMReplacementRequest
from payments.models import Payment
from .forms import *
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, 
    UpdateView, DeleteView, FormView, View
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, ListView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .forms import CustomUserCreationForm, CustomUserChangeForm, ProfilePictureForm
from .models import CustomUser, UserPlanHistory, UserFavouritePlan
from payments.models import Payment  # Make sure this import exists

# views.py
import json
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from .models import CustomUser, OTP
from .forms import OTPVerificationForm
from twilio.rest import Client
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from django.conf import settings
import logging
import re
import json


logger = logging.getLogger(__name__)

# users/views.py
import json
import re
import logging
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from infobip_channels.sms.channel import SMSChannel

from .models import CustomUser

logger = logging.getLogger(__name__)

# users/views.py
import json
import re
import logging
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from infobip_channels.sms.channel import SMSChannel

from .models import CustomUser

# Set up detailed logging
logger = logging.getLogger(__name__)


# users/views.py
import json
import re
import logging
import random
from datetime import timedelta, datetime
import urllib.parse
import urllib3
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.conf import settings
from django.http import JsonResponse
import threading
from django.contrib.auth import login as auth_login
from .models import CustomUser

logger = logging.getLogger(__name__)

class UnifiedAuthView(View):
    """Authentication view using Fast2SMS for OTP"""
    template_name = 'users/auth.html'
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fast2sms_api_key = getattr(settings, 'FAST2SMS_API_KEY', None)
            self.fast2sms_template_id = getattr(settings, 'FAST2SMS_TEMPLATE_ID', None)
            self.fast2sms_sender_id = getattr(settings, 'FAST2SMS_SENDER_ID', None)
            self.fast2sms_route = getattr(settings, 'FAST2SMS_ROUTE', 'dlt')
            self.simulation_mode = getattr(settings, 'OTP_SIMULATION_MODE', False)
            
            if self.simulation_mode:
                logger.warning("🔧 Running in SIMULATION mode - OTPs will be logged but not sent")
            elif not all([self.fast2sms_api_key, self.fast2sms_template_id, self.fast2sms_sender_id]):
                logger.warning("⚠️ Fast2SMS credentials not configured. Falling back to simulation mode.")
                self.simulation_mode = True
        
    def generate_otp(self):
        return ''.join(random.choices('0123456789', k=6))
    
    def send_otp_in_background(self, phone, otp):
        """Send OTP in background thread for faster response"""
        def send():
            try:
                params = {
                    'authorization': self.fast2sms_api_key,
                    'route': self.fast2sms_route,
                    'sender_id': self.fast2sms_sender_id,
                    'message': self.fast2sms_template_id,
                    'variables_values': f"{otp}|",
                    'numbers': phone
                }
                url = f"https://www.fast2sms.com/dev/bulkV2?{urllib.parse.urlencode(params)}"
                
                logger.info(f"📤 Sending OTP to {phone} in background")
                response = requests.get(url, timeout=30)
                result = response.json()
                
                if result.get('return'):
                    logger.info(f"✅ OTP sent to {phone}")
                else:
                    logger.error(f"❌ Failed to send OTP to {phone}: {result.get('message')}")
            except Exception as e:
                logger.error(f"❌ Error sending OTP to {phone}: {str(e)}")
        
        thread = threading.Thread(target=send)
        thread.daemon = True
        thread.start()
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        # Clear session if requested
        if request.GET.get('clear_session'):
            self.clear_auth_session(request)
            return redirect('auth')
        
        phone = request.session.get('auth_phone', '')
        context = {'phone': phone, 'show_otp': bool(phone)}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', 'send_otp')
        
        if action == 'send_otp':
            return self.handle_send_otp(request)
        elif action == 'verify_otp':
            return self.handle_verify_otp(request)
        elif action == 'resend_otp':
            return self.handle_resend_otp(request)
        else:
            messages.error(request, 'Invalid action')
            return redirect('auth')
    
    def handle_send_otp(self, request):
        """Fast OTP sending - returns immediately"""
        phone = request.POST.get('phone', '').strip()
        
        if not phone or not re.match(r'^\d{10}$', phone):
            messages.error(request, 'Please enter a valid 10-digit mobile number')
            return redirect('auth')
        
        # Rate limiting
        last_otp_time = request.session.get('last_otp_time')
        if last_otp_time:
            last_time = datetime.fromisoformat(last_otp_time)
            time_diff = (timezone.now() - last_time).total_seconds()
            if time_diff < 60:
                wait_time = int(60 - time_diff)
                messages.error(request, f'Please wait {wait_time} seconds')
                return redirect('auth')
        
        # User handling
        try:
            user = CustomUser.objects.get(phone=phone)
            is_new_user = False
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(
                phone=phone,
                username=f'user_{phone}',
                is_active=True,
                phone_verified=False
            )
            is_new_user = True
        
        # Generate OTP
        otp = self.generate_otp()
        print(otp,'otppppppppp')
        # Store session (fast - no API call)
        request.session['auth_phone'] = phone
        request.session['auth_user_id'] = user.id
        request.session['last_otp_time'] = timezone.now().isoformat()
        request.session['otp_code'] = otp
        request.session['otp_expiry'] = (timezone.now() + timedelta(minutes=10)).isoformat()
        
        # Send OTP in background (doesn't block response)
        if not self.simulation_mode:
            self.send_otp_in_background(phone, otp)
        else:
            # Log OTP for debugging in simulation mode
            logger.info(f"🔧 SIMULATION MODE - OTP for {phone}: {otp}")
        
        # ✅ REMOVED: TEST OTP message - no longer shown to user
        messages.success(request, f'OTP sent to {phone}')
        if is_new_user:
            messages.info(request, 'Welcome! Please verify your number.')
        
        return redirect('auth')
    
    def handle_verify_otp(self, request):
        """Verify the OTP entered by user"""
        logger.info("=" * 60)
        logger.info("🔐 VERIFYING OTP")
        logger.info("=" * 60)
        
        phone = request.session.get('auth_phone')
        user_id = request.session.get('auth_user_id')
        otp_code = request.POST.get('otp', '').strip()
        
        if not phone or not user_id:
            messages.error(request, 'Session expired. Please request a new OTP.')
            return redirect('auth')
        
        if not otp_code or len(otp_code) != 6:
            messages.error(request, 'Please enter a valid 6-digit OTP')
            return redirect('auth')
        
        # Check OTP against session-stored value
        stored_otp = request.session.get('otp_code')
        otp_expiry = request.session.get('otp_expiry')
        
        if not stored_otp:
            messages.error(request, 'Session expired. Please request a new OTP.')
            return redirect('auth')
        
        # Check OTP expiry
        if otp_expiry:
            expiry_time = datetime.fromisoformat(otp_expiry)
            if timezone.now() > expiry_time:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
                self.clear_auth_session(request)
                return redirect('auth')
        
        # Verify OTP
        if otp_code == stored_otp:
            logger.info("✅ OTP verified successfully")
            return self.login_user(request, user_id, phone)
        else:
            logger.warning(f"❌ Invalid OTP provided")
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('auth')
    
    def handle_resend_otp(self, request):
        """Handle AJAX resend OTP request"""
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
        
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            
            if not phone:
                return JsonResponse({'success': False, 'error': 'Phone number required'})
            
            # Rate limiting check (30 seconds for resend)
            last_otp_time = request.session.get('last_otp_time')
            if last_otp_time:
                last_time = datetime.fromisoformat(last_otp_time)
                time_diff = (timezone.now() - last_time).total_seconds()
                if time_diff < 30:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Please wait {int(30 - time_diff)} seconds before resending'
                    }, status=429)
            
            # Generate new OTP
            otp = self.generate_otp()
            
            # Update session
            request.session['last_otp_time'] = timezone.now().isoformat()
            request.session['otp_code'] = otp
            request.session['otp_expiry'] = (timezone.now() + timedelta(minutes=10)).isoformat()
            
            # Send OTP
            if self.simulation_mode:
                success = True
                error = None
                logger.info(f"🔧 SIMULATION MODE - New OTP for {phone}: {otp}")
            else:
                success, error, request_id = self.send_otp_via_fast2sms(phone, otp)
                if success and request_id:
                    request.session['otp_request_id'] = request_id
            
            if success:
                # ✅ REMOVED: demo_otp from response
                return JsonResponse({
                    'success': True, 
                    'message': 'OTP resent successfully'
                })
            else:
                return JsonResponse({'success': False, 'error': error}, status=500)
            
        except Exception as e:
            logger.error(f"❌ Resend error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    def login_user(self, request, user_id, phone):
        """Login user after successful verification"""
        try:
            user = CustomUser.objects.get(id=user_id, phone=phone)
            
            user.phone_verified = True
            user.last_login = timezone.now()
            user.save()
            
            auth_login(request, user)
            self.clear_auth_session(request)
            
            is_new_user = user.date_joined > timezone.now() - timedelta(minutes=5)
            if is_new_user:
                messages.success(request, f'Welcome! Your account has been created.')
            else:
                display_name = getattr(user, 'display_name', user.username)
                messages.success(request, f'Welcome back {display_name}!')
            
            return redirect('dashboard')
        
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('auth')
    
    def clear_auth_session(self, request):
        """Clear authentication session data"""
        session_keys = ['auth_phone', 'auth_user_id', 'otp_code', 'otp_expiry', 'last_otp_time', 'otp_request_id']
        for key in session_keys:
            if key in request.session:
                del request.session[key]


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = reverse_lazy('auth')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, View):
    """Dashboard view for authenticated users"""
    template_name = 'users/dashboard.html'
    login_url = reverse_lazy('auth')
    
    def get(self, request, *args, **kwargs):
        context = {
            'user': request.user,
            'is_new_user': not request.user.phone_verified,
        }
        return render(request, self.template_name, context)


# Profile Views
class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add additional context for profile page
        context.update({
            'form': CustomUserChangeForm(instance=user),
            'plan_history_count': UserPlanHistory.objects.filter(user=user).count(),
            'favourite_count': UserFavouritePlan.objects.filter(user=user).count(),
        })
        
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm  # Use the correct form
    template_name = 'users/profile.html'  # Use profile.html template
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add additional context
        context.update({
            'plan_history_count': UserPlanHistory.objects.filter(user=user).count(),
            'favourite_count': UserFavouritePlan.objects.filter(user=user).count(),
        })
        
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

# users/views.py
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's plan history
        context['plan_history'] = UserPlanHistory.objects.filter(
            user=user
        ).order_by('-purchased_on')[:5]
        
        # Get user's favourite plans
        context['favourite_plans'] = UserPlanHistory.objects.filter(
            user=user,
            plan__isnull=False
        ).select_related('plan', 'plan__operator')[:5]
        
        # Get recent payments
        context['recent_payments'] = Payment.objects.filter(
            user=user
        ).order_by('-payment_date')[:5]
        
        # Calculate payment statistics
        completed_payments = Payment.objects.filter(
            user=user, 
            payment_status='completed'
        )
        pending_payments = Payment.objects.filter(
            user=user, 
            payment_status='pending'
        )
        
        context['completed_payments_count'] = completed_payments.count()
        context['pending_payments_count'] = pending_payments.count()
        context['total_spent'] = completed_payments.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Get active plans
        context['active_plans'] = UserPlanHistory.objects.filter(
            user=user,
            status='active'
        )
        
        # Count stats
        context['active_plans_count'] = context['active_plans'].count()
        context['favourite_plans_count'] = UserFavouritePlan.objects.filter(user=user).count()
        
        # Recommended plans (based on user's previous purchases)
        try:
            # Get user's most purchased operator
            user_plans = UserPlanHistory.objects.filter(user=user)
            if user_plans.exists():
                from django.db.models import Count
                from plans.models import Plan
                
                # Get top operator
                top_operator = user_plans.values('plan__operator').annotate(
                    count=Count('plan__operator')
                ).order_by('-count').first()
                
                if top_operator and top_operator['plan__operator']:
                    # Get plans from top operator
                    context['recommended_plans'] = Plan.objects.filter(
                        operator_id=top_operator['plan__operator'],
                        is_active=True
                    )[:4]
                else:
                    # Show popular plans
                    context['recommended_plans'] = Plan.objects.filter(
                        is_active=True
                    ).order_by('-popularity_score')[:4]
            else:
                # Show popular plans for new users
                context['recommended_plans'] = Plan.objects.filter(
                    is_active=True
                ).order_by('-popularity_score')[:4]
        except:
            context['recommended_plans'] = []
        
        return context

from django.db.models import Sum, Q
from datetime import datetime, timedelta

from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Sum
from django.shortcuts import render

class PlanHistoryView(LoginRequiredMixin, ListView):
    model = UserPlanHistory
    template_name = 'users/plan_history.html'
    context_object_name = 'plan_history'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = UserPlanHistory.objects.filter(
            user=self.request.user
        ).select_related('plan', 'plan__operator', 'plan__category').order_by('-purchased_on')
        
        # Apply filters
        status = self.request.GET.get('status')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(purchased_on__date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(purchased_on__date__lte=end_date)
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all plans for stats (unfiltered)
        all_plans = UserPlanHistory.objects.filter(user=user)
        
        # Calculate stats
        active_plans_count = all_plans.filter(status='active').count()
        expired_plans_count = all_plans.filter(status='expired').count()
        
        # Calculate total spent on plans
        total_spent = all_plans.aggregate(
            total=Sum('plan__price')
        )['total'] or 0
        
        # Calculate days remaining and is_expired using different attribute names
        for plan in context['plan_history']:
            if plan.expires_on:
                today = datetime.now().date()
                expires_date = plan.expires_on.date()
                plan._calculated_days_remaining = (expires_date - today).days
                plan._calculated_is_expired = plan._calculated_days_remaining < 0
            else:
                plan._calculated_days_remaining = None
                plan._calculated_is_expired = False
        
        # SIM REPLACEMENT DATA
        # Get all SIM replacement requests for the user
        sim_requests = SIMReplacementRequest.objects.filter(user=user).order_by('-created_at')
        
        # Calculate SIM replacement statistics
        completed_sim_requests = sim_requests.filter(status='delivered')
        pending_sim_requests = sim_requests.filter(status__in=['pending', 'processing', 'approved', 'dispatched'])
        rejected_sim_requests = sim_requests.filter(status='rejected')
        
        # Calculate total spent on SIM replacements
        sim_total_spent = sim_requests.aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        context.update({
            'active_plans_count': active_plans_count,
            'expired_plans_count': expired_plans_count,
            'total_spent': total_spent,
            
            # SIM replacement context
            'sim_requests': sim_requests,
            'completed_sim_requests': completed_sim_requests,
            'pending_sim_requests': pending_sim_requests,
            'rejected_sim_requests': rejected_sim_requests,
            'sim_total_spent': sim_total_spent,
        })
        
        return context
    
    # Optional: You might need this if SIM replacement has its own separate list view
    def get(self, request, *args, **kwargs):
        # Check if we need to show SIM tab by default
        tab_param = request.GET.get('tab')
        if tab_param == 'sim-history':
            # For SIM tab, we don't need pagination for plans
            self.paginate_by = None
        return super().get(request, *args, **kwargs)

class FavouritePlansView(LoginRequiredMixin, ListView):
    model = UserFavouritePlan
    template_name = 'users/favourite_plans.html'
    context_object_name = 'favourite_plans'
    
    def get_queryset(self):
        return UserFavouritePlan.objects.filter(
            user=self.request.user
        ).select_related(
            'plan', 
            'plan__operator', 
            'plan__category'
        ).order_by('-added_on')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get favourite plans
        favourite_plans = self.get_queryset()
        
        # Count plans by type
        mobile_plans_count = favourite_plans.filter(
            plan__operator__operator_type='mobile'
        ).count()
        
        broadband_plans_count = favourite_plans.filter(
            plan__operator__operator_type='broadband'
        ).count()
        
        dth_plans_count = favourite_plans.filter(
            plan__operator__operator_type='dth'
        ).count()
        
        # Get unique operators from favourites
        operators = set()
        categories = set()
        
        for fav in favourite_plans:
            operators.add(fav.plan.operator)
            categories.add(fav.plan.category)
        
        context.update({
            'mobile_plans_count': mobile_plans_count,
            'broadband_plans_count': broadband_plans_count,
            'dth_plans_count': dth_plans_count,
            'operators': operators,
            'categories': categories,
        })
        
        return context

# Function-based views for additional functionality
@login_required
def update_profile_picture(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
        else:
            messages.error(request, 'Error updating profile picture.')
    
    return redirect('profile')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    
    return redirect('profile')