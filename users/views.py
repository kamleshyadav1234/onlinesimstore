from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
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

class UnifiedAuthView(View):
    """Unified authentication view - single screen for OTP login/registration"""
    template_name = 'users/auth.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        # Check if phone is in session (coming back after OTP failure)
        phone = request.session.get('auth_phone', '')
        
        context = {
            'phone': phone,
            'show_otp': bool(phone),  # Show OTP section if phone exists
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """Handle both OTP sending and verification"""
        action = request.POST.get('action', 'send_otp')
        
        if action == 'send_otp':
            return self.handle_send_otp(request)
        elif action == 'verify_otp':
            return self.handle_verify_otp(request)
        else:
            messages.error(request, 'Invalid action')
            return redirect('auth')
    
    def handle_send_otp(self, request):
        """Handle OTP sending"""
        phone = request.POST.get('phone', '').strip()
        
        if not phone or len(phone) != 10:
            messages.error(request, 'Please enter a valid 10-digit mobile number')
            return redirect('auth')
        
        # Check if user exists or create new one
        try:
            user = CustomUser.objects.get(phone=phone)
            is_new_user = False
        except CustomUser.DoesNotExist:
            # Create new user automatically
            user = CustomUser.objects.create(
                phone=phone,
                username=f'user_{phone}',
                is_active=True  # Auto-activate for OTP login
            )
            is_new_user = True
        
        # Generate and send OTP
        otp_obj = OTP.create_otp(
            phone=phone,
            otp_type='auth',
            user=user
        )
        
        # Store in session
        request.session['auth_phone'] = phone
        request.session['auth_user_id'] = user.id
        
        # In production: Send OTP via SMS
        # For demo, show OTP in message
        if is_new_user:
            messages.info(request, f'Welcome! New account created. OTP sent to {phone}: {otp_obj.otp}')
        else:
            messages.info(request, f'OTP sent to {phone}: {otp_obj.otp}')
        
        # Redirect back to same page (now showing OTP section)
        return redirect('auth')
    
    def handle_verify_otp(self, request):
        """Handle OTP verification"""
        phone = request.session.get('auth_phone')
        user_id = request.session.get('auth_user_id')
        otp = request.POST.get('otp', '').strip()
        
        if not phone or not user_id:
            messages.error(request, 'Session expired. Please try again.')
            return redirect('auth')
        
        if not otp or len(otp) != 6:
            messages.error(request, 'Please enter a valid 6-digit OTP')
            return redirect('auth')
        
        # Verify OTP
        try:
            otp_obj = OTP.objects.get(
                phone=phone,
                otp=otp,
                otp_type='auth',
                is_used=False
            )
            
            # Check if OTP is expired (10 minutes)
            from django.utils import timezone
            from datetime import timedelta
            
            if otp_obj.created_at < timezone.now() - timedelta(minutes=10):
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('auth')
            
            # Mark OTP as verified
            otp_obj.is_used = True
            otp_obj.save()
            
            # Get user
            try:
                user = CustomUser.objects.get(id=user_id, phone=phone)
                
                # Update user verification status
                user.phone_verified = True
                user.save()
                
                # Login user
                login(request, user)
                
                # Clear session
                self.clear_auth_session(request)
                
                # Welcome message
                if user.date_joined > timezone.now() - timedelta(minutes=5):
                    messages.success(request, f'Welcome to TelecomPedia! Your account has been created.')
                else:
                    messages.success(request, f'Welcome back {user.display_name}!')
                
                return redirect('dashboard')
                
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('auth')
                
        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('auth')
    
    def clear_auth_session(self, request):
        """Clear authentication session data"""
        session_keys = ['auth_phone', 'auth_user_id']
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