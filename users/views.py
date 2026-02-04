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
from plans.models import Plan
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

# Authentication Views
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')






class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        print("=" * 50)
        print("DEBUG: Form is VALID")
        print("DEBUG: Form cleaned data:", form.cleaned_data)
        
        try:
            # Save the user
            user = form.save()
            print(f"DEBUG: User created - ID: {user.id}, Username: {user.username}")
            print(f"DEBUG: User email: {user.email}, phone: {user.phone}")
            
            # Log the user in
            login(self.request, user)
            print("DEBUG: User logged in successfully")
            
            # Add success message
            messages.success(self.request, 'Registration successful! Welcome to TelecomPedia.')
            print("DEBUG: Success message added")
            
        except Exception as e:
            print(f"DEBUG: ERROR during user creation: {str(e)}")
            messages.error(self.request, f'Error creating account: {str(e)}')
            return self.form_invalid(form)
        
        print("=" * 50)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("=" * 50)
        print("DEBUG: Form is INVALID")
        print("DEBUG: Form errors:", form.errors)
        print("DEBUG: Form non-field errors:", form.non_field_errors())
        print("DEBUG: POST data:", self.request.POST)
        
        # Add error messages for each field
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        
        print("=" * 50)
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        print("DEBUG: GET request to register page")
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        print("DEBUG: POST request to register page")
        print("DEBUG: Raw POST data:", dict(request.POST))
        return super().post(request, *args, **kwargs)



# Add these imports
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate
from .forms import MobileLoginForm, OTPVerificationForm, PhoneRegistrationForm, OTPResendForm

# OTP Login Views
class MobileLoginView(View):
    template_name = 'users/mobile_login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = MobileLoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = MobileLoginForm(request.POST)
        
        if form.is_valid():
            phone = form.cleaned_data['phone']
            
            # Get user
            try:
                user = CustomUser.objects.get(phone=phone)
            except CustomUser.DoesNotExist:
                messages.error(request, 'No account found with this mobile number.')
                return render(request, self.template_name, {'form': form})
            
            # Generate OTP (simulate sending)
            otp_obj = OTP.create_otp(phone=phone, otp_type='login', user=user)
            
            # In production, you would send OTP via SMS here
            # For now, we'll just show it in messages (remove in production)
            messages.info(request, f'Demo OTP sent to {phone}: {otp_obj.otp}')
            
            # Store phone in session for verification
            request.session['login_phone'] = phone
            request.session['login_user_id'] = user.id
            
            return redirect('verify_otp')
        
        return render(request, self.template_name, {'form': form})

class OTPVerificationView(View):
    template_name = 'users/otp_verification.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        phone = request.session.get('login_phone')
        user_id = request.session.get('login_user_id')
        
        if not phone or not user_id:
            messages.error(request, 'Session expired. Please login again.')
            return redirect('mobile_login')
        
        form = OTPVerificationForm(initial={'phone': phone})
        context = {
            'form': form,
            'phone': phone,
            'masked_phone': self.mask_phone(phone)
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        phone = request.session.get('login_phone')
        user_id = request.session.get('login_user_id')
        
        if not phone or not user_id:
            messages.error(request, 'Session expired. Please login again.')
            return redirect('mobile_login')
        
        form = OTPVerificationForm(request.POST, phone=phone, otp_type='login')
        
        if form.is_valid():
            # Get user
            try:
                user = CustomUser.objects.get(id=user_id, phone=phone)
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('mobile_login')
            
            # Login the user
            login(request, user)
            
            # Clear session data
            if 'login_phone' in request.session:
                del request.session['login_phone']
            if 'login_user_id' in request.session:
                del request.session['login_user_id']
            
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        
        context = {
            'form': form,
            'phone': phone,
            'masked_phone': self.mask_phone(phone)
        }
        return render(request, self.template_name, context)
    
    def mask_phone(self, phone):
        """Mask phone number for display"""
        if len(phone) > 6:
            return f"{phone[:3]}****{phone[-3:]}"
        return phone

class OTPResendView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        phone = data.get('phone')
        otp_type = data.get('otp_type', 'login')
        
        if not phone:
            return JsonResponse({'success': False, 'error': 'Phone number required'})
        
        # Get user if exists
        user = None
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            pass
        
        # Generate new OTP
        otp_obj = OTP.create_otp(phone=phone, otp_type=otp_type, user=user)
        
        # In production: Send OTP via SMS
        # For demo, return OTP in response (remove in production)
        return JsonResponse({
            'success': True,
            'message': f'OTP resent to {phone}',
            'demo_otp': otp_obj.otp  # Remove this in production
        })

# Update your existing RegisterView to use phone OTP
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        
        # Generate and send OTP for phone verification
        otp_obj = OTP.create_otp(phone=user.phone, otp_type='phone_verification', user=user)
        
        # Store user info in session for verification
        self.request.session['verify_phone'] = user.phone
        self.request.session['verify_user_id'] = user.id
        
        messages.info(self.request, f'Account created! Verification OTP sent to {user.phone}: {otp_obj.otp}')
        
        # Don't login automatically, redirect to OTP verification
        return redirect('verify_phone_otp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add phone registration form as alternative
        context['phone_form'] = PhoneRegistrationForm()
        return context

class PhoneVerificationView(View):
    template_name = 'users/phone_verification.html'
    
    def get(self, request, *args, **kwargs):
        phone = request.session.get('verify_phone')
        user_id = request.session.get('verify_user_id')
        
        if not phone or not user_id:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')
        
        form = OTPVerificationForm(initial={'phone': phone})
        context = {
            'form': form,
            'phone': phone,
            'masked_phone': self.mask_phone(phone),
            'verification_type': 'phone_verification'
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        phone = request.session.get('verify_phone')
        user_id = request.session.get('verify_user_id')
        
        if not phone or not user_id:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')
        
        form = OTPVerificationForm(request.POST, phone=phone, otp_type='phone_verification')
        
        if form.is_valid():
            # Get and update user
            try:
                user = CustomUser.objects.get(id=user_id, phone=phone)
                user.phone_verified = True
                user.save()
                
                # Clear session
                if 'verify_phone' in request.session:
                    del request.session['verify_phone']
                if 'verify_user_id' in request.session:
                    del request.session['verify_user_id']
                
                # Login user
                login(request, user)
                messages.success(request, 'Phone verified successfully! Account is now active.')
                return redirect('dashboard')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('register')
        
        context = {
            'form': form,
            'phone': phone,
            'masked_phone': self.mask_phone(phone),
            'verification_type': 'phone_verification'
        }
        return render(request, self.template_name, context)
    
    def mask_phone(self, phone):
        if len(phone) > 6:
            return f"{phone[:3]}****{phone[-3:]}"
        return phone

# Update CustomLoginView to redirect to mobile login
class CustomLoginView(View):
    def get(self, request, *args, **kwargs):
        # Redirect to mobile login by default
        return redirect('mobile_login')


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

# Dashboard Views
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
        
        # Get recent payments (if Payment model exists)
        try:
            context['recent_payments'] = Payment.objects.filter(
                user=user
            ).order_by('-payment_date')[:5]
        except:
            context['recent_payments'] = []
        
        # Get active plans
        context['active_plans'] = UserPlanHistory.objects.filter(
            user=user,
            status='active'
        )
        
        # Count stats
        context['active_plans_count'] = context['active_plans'].count()
        context['favourite_plans_count'] = UserFavouritePlan.objects.filter(user=user).count()
        
        return context

from django.db.models import Sum, Q
from datetime import datetime, timedelta

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
        
        # Calculate total spent
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
        
        context.update({
            'active_plans_count': active_plans_count,
            'expired_plans_count': expired_plans_count,
            'total_spent': total_spent,
        })
        
        return context

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