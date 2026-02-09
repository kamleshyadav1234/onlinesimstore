from datetime import datetime, timedelta
import random
import string
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.views import View

from plans.forms import  DocumentUploadForm, NewConnectionForm, SIMReplacementForm
from .models import TelecomOperator, ServiceArea
from plans.models import NewConnectionRequest, Plan, PlanCategory, PortRequest, SIMReplacementRequest

# class HomeView(TemplateView):
#     template_name = 'home.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['popular_plans'] = Plan.objects.filter(is_popular=True, is_active=True)[:8]
#         context['featured_operators'] = TelecomOperator.objects.filter(is_active=True)[:6]
#         context['categories'] = PlanCategory.objects.all()[:6]
#         return context

# class HomeView(TemplateView):
#     template_name = 'home.html'  # or whatever your template is called
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Get all active operators
#         context['operators'] = TelecomOperator.objects.filter(is_active=True)
        
#         # Get all categories
#         context['categories'] = PlanCategory.objects.all()
        
#         # Get popular plans (is_popular=True and is_active=True)
#         context['popular_plans'] = Plan.objects.filter(
#             is_popular=True, 
#             is_active=True
#         ).select_related('operator', 'category')[:8]  # Limit to 8 plans
        
#         # Get featured operators (you might want to add a 'is_featured' field)
#         # For now, let's get the first 6 active operators
#         context['featured_operators'] = TelecomOperator.objects.filter(
#             is_active=True
#         )[:6]
        
#         return context

# views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone
from plans.models import PlanCategory
# plans/views.py
from django.views.generic import TemplateView, CreateView, DetailView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from plans.forms import PortNumberForm, NewConnectionForm

# views.py
from django.views.generic import TemplateView, CreateView, DetailView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all active operators
        context['operators'] = TelecomOperator.objects.filter(is_active=True)
        context['categories'] = PlanCategory.objects.all()
        
        # Get popular plans
        context['popular_plans'] = Plan.objects.filter(
            is_popular=True, 
            is_active=True
        ).select_related('operator', 'category')[:8]
        
        # Get featured operators
        context['featured_operators'] = TelecomOperator.objects.filter(
            is_active=True
        )[:6]
        
        # Get featured plans by type
        context['new_connection_plans'] = Plan.objects.filter(
            plan_type='new_connection',
            is_active=True,
            is_featured=True
        ).select_related('operator')[:3]
        
        context['port_in_plans'] = Plan.objects.filter(
            plan_type='port_in',
            is_active=True,
            is_featured=True
        ).select_related('operator')[:3]
        
        # Connection types for cards
        context['connection_types'] = [
            {
                'id': 'new',
                'name': 'New Connection',
                'icon': 'fas fa-sim-card',
                'description': 'Get a new mobile SIM card',
                'color': 'primary',
                'url': reverse_lazy('new_connection')  # Changed to separate page
            },
            {
                'id': 'mnp',
                'name': 'Port Number (MNP)',
                'icon': 'fas fa-exchange-alt',
                'description': 'Keep number, change operator',
                'color': 'success',
                'url': reverse_lazy('port_number')  # Changed to separate page
            },
            {
                'id': 'sim_replace',
                'name': 'SIM Replacement',
                'icon': 'fas fa-redo',
                'description': 'Replace lost/damaged SIM',
                'color': 'warning',
                 'url': reverse_lazy('sim_replacement_create')
            },
            {
                'id': 'plan_upgrade',
                'name': 'Plan Upgrade',
                'icon': 'fas fa-chart-line',
                'description': 'Upgrade your existing plan',
                'color': 'info',
                'url': reverse_lazy('plan_list')
            }
        ]
        
        return context



from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView, FormView
# your_app/views.py
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import uuid



# # SIM Replacement Create View (Step 1)
# class SIMReplacementCreateView(LoginRequiredMixin, CreateView):
#     model = SIMReplacementRequest
#     form_class = SIMReplacementForm
#     template_name = 'plans/sim_replacement_create.html'
#     success_url = reverse_lazy('sim_replacement_documents')
    
#     def form_valid(self, form):
#         # Set user before saving
#         form.instance.user = self.request.user
        
#         # Calculate amount based on service type
#         if form.instance.service_type == 'fast':
#             form.instance.amount_paid = 199.00
#         else:
#             form.instance.amount_paid = 99.00
        
#         # Generate request ID
#         form.instance.request_id = f"SIM{str(uuid.uuid4())[:8].upper()}"
        
#         # Convert date objects to string for JSON serialization
#         form_data = form.cleaned_data.copy()
#         if form_data.get('date_of_birth'):
#             form_data['date_of_birth'] = form_data['date_of_birth'].isoformat()
        
#         # Store in session for document upload step
#         self.request.session['sim_request_data'] = {
#             'form_data': form_data,  # Use the converted copy
#             'amount_paid': str(form.instance.amount_paid),
#             'request_id': form.instance.request_id
#         }
        
#         messages.success(self.request, 'Step 1 completed! Please upload required documents.')
#         return redirect(self.success_url)
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import random

# telecom/views.py
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from payments.models import Payment
from django.db import transaction

class SIMReplacementCreateView(LoginRequiredMixin, CreateView):
    model = SIMReplacementRequest
    form_class = SIMReplacementForm
    template_name = 'plans/sim_replacement_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Clean up any old locks
        from django.db import connection
        connection.close_if_unusable_or_obsolete()
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Check for pending requests
        pending_requests = SIMReplacementRequest.objects.filter(
            user=request.user,
            status='pending',
            created_at__gte=timezone.now() - timedelta(minutes=5)
        )
        
        if pending_requests.exists():
            latest_request = pending_requests.latest('created_at')
            payment = Payment.objects.filter(
                sim_replacement=latest_request,
                user=request.user,
                payment_status__in=['pending', 'completed']
            ).first()
            
            if payment:
                return redirect(reverse('process_payment') + f'?sim_replacement_id={latest_request.id}')
        
        return super().get(request, *args, **kwargs)
    
    @transaction.atomic
    def form_valid(self, form):
        try:
            # Get form data
            mobile_number = form.cleaned_data.get('mobile_number')
            operator = form.cleaned_data.get('operator')
            
            # Check for recent pending requests
            recent_pending = SIMReplacementRequest.objects.filter(
                user=self.request.user,
                mobile_number=mobile_number,
                operator=operator,
                status='pending',
                created_at__gte=timezone.now() - timedelta(minutes=2)
            ).exists()
            
            if recent_pending:
                messages.warning(self.request, 'You already have a pending SIM replacement request.')
                return redirect('sim_replacement_status')
            
            # Check for completed request in last 24 hours
            recent_completed = SIMReplacementRequest.objects.filter(
                user=self.request.user,
                mobile_number=mobile_number,
                operator=operator,
                status='completed',
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).exists()
            
            if recent_completed:
                messages.warning(self.request, 'You already processed a SIM replacement for this number recently.')
                return redirect('sim_replacement_status')
            
            # Create SIM replacement request
            sim_request = form.save(commit=False)
            sim_request.user = self.request.user
            sim_request.status = 'pending'
            
            # Calculate amount
            if sim_request.service_type == 'fast':
                sim_request.amount_paid = 199
            else:
                sim_request.amount_paid = 99
            
            # Generate unique request ID
            import random
            while True:
                request_id = f"SIM{random.randint(100000, 999999)}"
                if not SIMReplacementRequest.objects.filter(request_id=request_id).exists():
                    sim_request.request_id = request_id
                    break
            
            # ✅ Save SIM request FIRST
            sim_request.save()
            
            # Check for existing payment
            existing_payment = Payment.objects.filter(
                sim_replacement=sim_request,
                user=self.request.user,
                payment_status__in=['pending', 'completed']
            ).first()
            
            if existing_payment:
                payment = existing_payment
                print(f"✅ Using existing payment: {payment.bill_number}")
            else:
                # Create payment with minimal operations
                payment = Payment.objects.create(
                    user=self.request.user,
                    payment_type='sim_replacement',
                    sim_replacement=sim_request,
                    amount=sim_request.amount_paid,
                    payment_method='razorpay',
                    payment_status='pending',
                    transaction_id=f"SIMPAY{random.randint(100000, 999999)}"
                )
                print(f"✅ Created new payment: {payment.bill_number}")
            
            # For AJAX requests
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'request_id': sim_request.request_id,
                    'connection_request_id': sim_request.id,
                    'payment_id': payment.id,
                    'redirect_url': reverse('process_payment') + f'?sim_replacement_id={sim_request.id}',
                    'message': 'SIM replacement request created successfully'
                })
            
            # Redirect to payment page
            return redirect(reverse('process_payment') + f'?sim_replacement_id={sim_request.id}')
            
        except Exception as e:
            print(f"❌ Error in SIM replacement creation: {str(e)}")
            import traceback
            traceback.print_exc()
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Database error. Please try again.'
                }, status=500)
            
            messages.error(self.request, 'An error occurred. Please try again.')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field in form.errors:
                errors[field] = form.errors[field]
            
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the form errors'
            }, status=400)
        
        return super().form_invalid(form)


# class SIMReplacementCreateView(LoginRequiredMixin, CreateView):
#     model = SIMReplacementRequest
#     form_class = SIMReplacementForm
#     template_name = 'plans/sim_replacement_create.html'
    
#     def dispatch(self, request, *args, **kwargs):
#         # Use atomic transaction to prevent race conditions
#         from django.db import transaction
#         return super().dispatch(request, *args, **kwargs)
    
#     def get(self, request, *args, **kwargs):
#         # Check if user has a pending request in the last 5 minutes
#         pending_requests = SIMReplacementRequest.objects.filter(
#             user=request.user,
#             status='pending',
#             created_at__gte=timezone.now() - timedelta(minutes=5)
#         )
        
#         if pending_requests.exists():
#             latest_request = pending_requests.latest('created_at')
#             # Check if there's a payment for this request
#             payment = Payment.objects.filter(
#                 sim_replacement=latest_request,
#                 user=request.user,
#                 payment_status__in=['pending', 'completed']
#             ).first()
            
#             if payment:
#                 messages.info(request, f'You have a pending SIM replacement request: {latest_request.request_id}')
#                 return redirect(reverse('process_payment') + f'?sim_replacement_id={latest_request.id}')
        
#         return super().get(request, *args, **kwargs)
    
#     def form_valid(self, form):
#         # Get form data
#         mobile_number = form.cleaned_data.get('mobile_number')
#         operator = form.cleaned_data.get('operator')
        
#         # ✅ CRITICAL: Use database lock to prevent race conditions
#         from django.db import transaction
#         with transaction.atomic():
#             # Check for existing pending request in the last 2 minutes
#             recent_pending = SIMReplacementRequest.objects.select_for_update().filter(
#                 user=self.request.user,
#                 mobile_number=mobile_number,
#                 operator=operator,
#                 status='pending',
#                 created_at__gte=timezone.now() - timedelta(minutes=2)
#             ).exists()
            
#             if recent_pending:
#                 if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                     return JsonResponse({
#                         'success': False,
#                         'message': 'You already have a pending SIM replacement request for this number. Please wait.'
#                     }, status=400)
#                 messages.warning(self.request, 'You already have a pending SIM replacement request.')
#                 return redirect('sim_replacement_status')
            
#             # Check for completed request in last 24 hours
#             recent_completed = SIMReplacementRequest.objects.filter(
#                 user=self.request.user,
#                 mobile_number=mobile_number,
#                 operator=operator,
#                 status='completed',
#                 created_at__gte=timezone.now() - timedelta(hours=24)
#             ).exists()
            
#             if recent_completed:
#                 if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                     return JsonResponse({
#                         'success': False,
#                         'message': 'You already processed a SIM replacement for this number in the last 24 hours.'
#                     }, status=400)
#                 messages.warning(self.request, 'You already processed a SIM replacement for this number recently.')
#                 return redirect('sim_replacement_status')
            
#             # Create the SIM request
#             sim_request = form.save(commit=False)
#             sim_request.user = self.request.user
#             sim_request.status = 'pending'
            
#             # Calculate amount
#             if sim_request.service_type == 'fast':
#                 sim_request.amount_paid = 199
#             else:
#                 sim_request.amount_paid = 99
            
#             # Generate unique request ID
#             import random
#             while True:
#                 request_id = f"SIM{random.randint(100000, 999999)}"
#                 if not SIMReplacementRequest.objects.filter(request_id=request_id).exists():
#                     sim_request.request_id = request_id
#                     break
            
#             # ✅ CRITICAL: Save to database immediately
#             sim_request.save()
            
#             # Check if a payment already exists for this request
#             existing_payment = Payment.objects.filter(
#                 sim_replacement=sim_request,
#                 user=self.request.user,
#                 payment_status__in=['pending', 'completed']
#             ).first()
            
#             if existing_payment:
#                 # Use existing payment
#                 payment = existing_payment
#                 print(f"✅ Using existing payment: {payment.bill_number}")
#             else:
#                 # Create new payment record
#                 payment = Payment.objects.create(
#                     user=self.request.user,
#                     payment_type='sim_replacement',
#                     sim_replacement=sim_request,
#                     amount=sim_request.amount_paid,
#                     payment_method='razorpay',
#                     payment_status='pending',
#                     transaction_id=f"SIMPAY{random.randint(100000, 999999)}"
#                 )
#                 print(f"✅ Created new payment: {payment.bill_number}")
        
#         # For AJAX requests
#         if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'request_id': sim_request.request_id,
#                 'connection_request_id': sim_request.id,
#                 'payment_id': payment.id,
#                 'redirect_url': reverse('process_payment') + f'?sim_replacement_id={sim_request.id}',
#                 'message': 'SIM replacement request created successfully'
#             })
        
#         # For non-AJAX
#         return redirect('process_payment') + f'?sim_replacement_id={sim_request.id}'
    
#     def form_invalid(self, form):
#         if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             errors = {}
#             for field in form.errors:
#                 errors[field] = form.errors[field]
            
#             return JsonResponse({
#                 'success': False,
#                 'errors': errors,
#                 'message': 'Please correct the form errors'
#             }, status=400)
        
#         return super().form_invalid(form)
    

# SIM Replacement Document Upload View (Step 2)
class SIMReplacementDocumentView(LoginRequiredMixin, FormView):
    form_class = DocumentUploadForm
    template_name = 'plans/sim_replacement_documents.html'
    success_url = reverse_lazy('sim_replacement_status')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has completed step 1
        if 'sim_request_data' not in request.session:
            messages.warning(request, 'Please complete the request form first.')
            return redirect('sim_replacement_create')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Get data from session
        sim_data = self.request.session['sim_request_data']
        form_data = sim_data['form_data']
        
        # Create SIM replacement request object
        sim_request = SIMReplacementRequest.objects.create(
            user=self.request.user,
            request_id=sim_data['request_id'],
            reason=form_data['reason'],
            operator=form_data['operator'],
            mobile_number=form_data['mobile_number'],
            old_sim_type=form_data['old_sim_type'],
            new_sim_type=form_data['new_sim_type'],
            full_name=form_data['full_name'],
            email=form_data['email'],
            alternate_contact=form_data['alternate_contact'],
            date_of_birth=form_data.get('date_of_birth'),
            address_line1=form_data['address_line1'],
            address_line2=form_data.get('address_line2', ''),
            city=form_data['city'],
            state=form_data['state'],
            pincode=form_data['pincode'],
            service_type=form_data['service_type'],
            amount_paid=sim_data['amount_paid'],
            id_proof=form.cleaned_data['id_proof'],
            address_proof=form.cleaned_data['address_proof'],
            status='pending'
        )
        
        # Save optional documents
        if form.cleaned_data['declaration_form']:
            sim_request.declaration_form = form.cleaned_data['declaration_form']
        
        if form.cleaned_data['photo']:
            sim_request.photo = form.cleaned_data['photo']
        
        # Set estimated delivery
        if sim_request.service_type == 'fast':
            sim_request.estimated_delivery = timezone.now() + timedelta(hours=4)
        else:
            sim_request.estimated_delivery = timezone.now() + timedelta(hours=48)
        
        sim_request.save()
        
        # Clear session data
        del self.request.session['sim_request_data']
        
        # Store request ID in session for status page
        self.request.session['last_sim_request_id'] = sim_request.request_id
        
        messages.success(self.request, f'Request submitted successfully! Your request ID: {sim_request.request_id}')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sim_data = self.request.session.get('sim_request_data', {})
        context['request_data'] = sim_data.get('form_data', {})
        context['title'] = 'Upload Documents'
        return context

# SIM Replacement Status View
class SIMReplacementStatusView(LoginRequiredMixin, DetailView):
    model = SIMReplacementRequest
    template_name = 'plans/sim_replacement_status.html'
    context_object_name = 'sim_request'
    
    def get_object(self, queryset=None):
        # Try to get request_id from URL first, then from session
        request_id = self.kwargs.get('request_id') or self.request.session.get('last_sim_request_id')
        if request_id:
            return get_object_or_404(SIMReplacementRequest, request_id=request_id, user=self.request.user)
        raise Http404("No SIM replacement request found.")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Request Status - {self.object.request_id}'
        return context

# SIM Replacement List View (Track all requests)
class SIMReplacementListView(LoginRequiredMixin, ListView):
    model = SIMReplacementRequest
    template_name = 'sim_replacement_list.html'
    context_object_name = 'requests'
    paginate_by = 10
    
    def get_queryset(self):
        return SIMReplacementRequest.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My SIM Replacement Requests'
        return context

# SIM Replacement Detail View
class SIMReplacementDetailView(LoginRequiredMixin, DetailView):
    model = SIMReplacementRequest
    template_name = 'sim_replacement_detail.html'
    context_object_name = 'sim_request'
    
    def get_queryset(self):
        return SIMReplacementRequest.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Request Details - {self.object.request_id}'
        return context

# SIM Replacement Update View (for admin updates)
class SIMReplacementUpdateView(LoginRequiredMixin, UpdateView):
    model = SIMReplacementRequest
    template_name = 'sim_replacement_update.html'
    fields = ['status', 'tracking_number', 'courier_partner', 'notes']
    
    def get_queryset(self):
        # Only allow updates if user is staff or owner
        if self.request.user.is_staff:
            return SIMReplacementRequest.objects.all()
        return SIMReplacementRequest.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Request updated successfully!')
        return response
    
    def get_success_url(self):
        return reverse('sim_replacement_detail', kwargs={'pk': self.object.pk})

# SIM Replacement Instructions View
class SIMReplacementInstructionsView(TemplateView):
    template_name = 'sim_replacement_instructions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'SIM Replacement Instructions'
        context['steps'] = [
            {
                'number': 1,
                'title': 'Fill Request Form',
                'description': 'Provide your mobile number and personal details',
                'icon': 'fas fa-edit'
            },
            {
                'number': 2,
                'title': 'Upload Documents',
                'description': 'Upload ID proof and address proof',
                'icon': 'fas fa-upload'
            },
            {
                'number': 3,
                'title': 'Make Payment',
                'description': 'Pay the SIM replacement fee (₹99-₹199)',
                'icon': 'fas fa-credit-card'
            },
            {
                'number': 4,
                'title': 'Receive New SIM',
                'description': 'Get new SIM delivered to your address',
                'icon': 'fas fa-truck'
            },
            {
                'number': 5,
                'title': 'Activation',
                'description': 'New SIM activated within 1-4 hours',
                'icon': 'fas fa-bolt'
            }
        ]
        return context




# views.py - UPDATED PortNumberView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin


from django.db import transaction
from plans.models import PortRequest
from payments.models import Payment
from users.models import UserPlanHistory

class PortNumberView(LoginRequiredMixin, CreateView):
    """View for porting existing number"""
    model = PortRequest
    form_class = PortNumberForm
    template_name = 'plans/port_number.html'
    
    def get_success_url(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return None
        return reverse_lazy('port_request_status')
    


    def handle_ajax_request(self, request):
        """Handle AJAX request for loading plans"""
        new_operator_id = request.GET.get('new_operator')
        
        # Get port-in plans for the selected operator or all
        port_plans = Plan.objects.filter(
            plan_type='port_in',
            is_active=True
        ).select_related('operator')
        
        if new_operator_id:
            port_plans = port_plans.filter(operator_id=new_operator_id)
        
        # Serialize plans data
        plans_data = []
        for plan in port_plans.order_by('operator__name', 'price'):
            plans_data.append({
                'id': plan.id,
                'name': plan.name,
                'operator_id': plan.operator.id,
                'operator_name': plan.operator.name,
                'price': str(plan.price),
                'validity': plan.validity,
                'validity_unit': plan.get_validity_unit_display(),
                'data_allowance': plan.data_allowance or 'Unlimited',
                'voice_calls': plan.voice_calls or 'Unlimited',
                'sms': plan.sms or 'Unlimited',
                'port_in_bonus': plan.port_in_bonus,
            })
        
        return JsonResponse({
            'plans': plans_data,
            'count': len(plans_data)
        })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Port Your Number'
        context['subtitle'] = 'Keep your number, switch to better operator with exclusive port-in offers'
        
        # Get all active operators
        context['operators'] = TelecomOperator.objects.filter(is_active=True)
        
        # Get selected operator from GET parameter
        new_operator_id = self.request.GET.get('new_operator')
        context['selected_operator'] = None
        
        # Get ALL port-in plans initially
        port_plans = Plan.objects.filter(
            plan_type='port_in',
            is_active=True
        ).select_related('operator').order_by('operator__name', 'price')
        
        if new_operator_id:
            port_plans = port_plans.filter(operator_id=new_operator_id)
            try:
                context['selected_operator'] = TelecomOperator.objects.get(id=new_operator_id, is_active=True)
            except TelecomOperator.DoesNotExist:
                pass
        
        context['port_plans'] = port_plans
        
        # Get featured port plans
        context['featured_port_plans'] = Plan.objects.filter(
            plan_type='port_in',
            is_active=True,
            is_featured=True
        ).select_related('operator')[:6]
        
        if 'form' not in context:
            context['form'] = self.get_form()
        
        # Check if we should show step 3 directly
        show_step_3 = self.request.session.pop('show_step_3', False)
        context['show_step_3'] = show_step_3
        
        return context
    
    def get_initial(self):
        """Set initial values for the form"""
        initial = super().get_initial()
        initial['full_name'] = self.request.user.get_full_name()
        initial['email'] = self.request.user.email
        
        # Set new_operator from GET parameter if exists
        new_operator_id = self.request.GET.get('new_operator')
        if new_operator_id:
            try:
                initial['new_operator'] = TelecomOperator.objects.get(id=new_operator_id)
            except TelecomOperator.DoesNotExist:
                pass
        
        # Check for preserved form data in session
        form_data = self.request.session.get('form_data', {})
        if form_data:
            initial.update(form_data)
            if 'form_data' in self.request.session:
                del self.request.session['form_data']
        
        # Also restore Step 1 data specifically
        step1_data = self.request.session.get('step1_data', {})
        if step1_data:
            initial.update(step1_data)
            if 'step1_data' in self.request.session:
                del self.request.session['step1_data']
        
        return initial
    
    @transaction.atomic
    def form_valid(self, form):
        """Handle valid form submission"""
        try:
            # Get mobile number from form
            mobile_number = form.cleaned_data['mobile_number']
            
            # Basic validation
            if len(mobile_number) != 10 or mobile_number[0] not in '6789':
                form.add_error('mobile_number', 
                    "Please enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
                self.request.session['show_step_3'] = True
                return self.form_invalid(form)
            
            # Check if number is already being ported by this user
            if PortRequest.objects.filter(
                mobile_number=mobile_number,
                user=self.request.user,
                status__in=['pending', 'upc_sent', 'processing']
            ).exists():
                form.add_error('mobile_number', 
                    f"Mobile number {mobile_number} already has an active port request.")
                self.request.session['show_step_3'] = True
                return self.form_invalid(form)
            
            # Get selected plan
            selected_plan = form.cleaned_data.get('selected_plan')
            if not selected_plan:
                form.add_error('selected_plan', 'Please select a port-in plan.')
                self.request.session['show_step_3'] = True
                return self.form_invalid(form)
            
            # Set new_operator from the selected plan's operator
            new_operator = selected_plan.operator
            
            # Save the port request with user
            port_request = form.save(commit=False)
            port_request.user = self.request.user
            port_request.new_operator = new_operator
            port_request.selected_plan = selected_plan  # Make sure selected_plan is saved
            port_request.status = 'pending'
            
            # Generate tracking ID
            tracking_id = self.generate_tracking_id()
            port_request.tracking_id = tracking_id
            
            # Generate UPC code
            upc_code = self.generate_upc_code()
            port_request.upc_code = upc_code
            port_request.upc_expiry = timezone.now() + timezone.timedelta(days=4)
            
            # Save the instance
            port_request.save()
            
            # Set the object for CreateView
            self.object = port_request
            
            # ✅ CRITICAL: Handle payment based on payment method
            payment_method = self.request.POST.get('payment_method', 'cod')
            
            # Create Payment record for COD
            if payment_method == 'cod':
                payment = self.create_cod_payment(port_request, selected_plan)
                
                # Store payment ID in session for later use
                self.request.session['current_payment_id'] = payment.id
                
                # For COD, update port request status directly to payment_completed
                port_request.status = 'payment_completed'
                port_request.save()
                
                # Create plan history for COD
                self.create_plan_history_for_cod(payment, selected_plan)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Port request created successfully',
                    'tracking_id': tracking_id,
                    'port_request_id': port_request.id,
                    'redirect_url': self.get_payment_redirect_url(port_request, payment_method)
                })
            
            # Handle regular form submission
            return self.payment_redirect(port_request, payment_method)
            
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            self.request.session['show_step_3'] = True
            return self.form_invalid(form)
    
    def create_cod_payment(self, port_request, selected_plan):
        """Create a COD payment record"""
        from django.utils import timezone
        
        # Generate a unique transaction ID for COD
        import uuid
        transaction_id = f"COD-{uuid.uuid4().hex[:12].upper()}"
        
        # Generate bill number
        from datetime import datetime
        bill_number = f"BILL-COD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create payment record
        payment = Payment.objects.create(
            user=self.request.user,
            amount=selected_plan.price,
            payment_method='cod',
            payment_status='completed',  # COD is considered completed as user will pay later
            transaction_id=transaction_id,
            bill_number=bill_number,
            payment_date=timezone.now(),
            plan=selected_plan,
            port_request=port_request,
            notes="Cash on Delivery - Payment pending collection"
        )
        
        return payment
    
    def create_plan_history_for_cod(self, payment, selected_plan):
        """Create plan history entry for COD payments"""
        from django.utils import timezone
        from datetime import timedelta
        
        validity_days = selected_plan.validity
        
        if selected_plan.validity_unit == 'months':
            validity_days = validity_days * 30
        elif selected_plan.validity_unit == 'year':
            validity_days = validity_days * 365
        
        # Create plan history
        UserPlanHistory.objects.create(
            user=self.request.user,
            plan=selected_plan,
            purchased_on=payment.payment_date,
            activated_on=timezone.now(),
            expires_on=timezone.now() + timedelta(days=validity_days),
            status='active',
            transaction_id=payment.transaction_id,
            port_request=payment.port_request
        )
        
        # Update user's current plan
        try:
            if hasattr(self.request.user, 'profile'):
                self.request.user.profile.current_plan = selected_plan
                self.request.user.profile.plan_start_date = timezone.now()
                self.request.user.profile.plan_expiry_date = timezone.now() + timedelta(days=validity_days)
                self.request.user.profile.save()
        except AttributeError:
            pass  # No profile model
    
    def form_invalid(self, form):
        """Handle invalid form submission"""
        print("Form errors:", form.errors)
        print("Form non-field errors:", form.non_field_errors())
        
        messages.error(self.request, "Please correct the errors below.")
        self.request.session['show_step_3'] = True
        
        # Preserve the form data including Step 1 data
        self.request.session['form_data'] = {
            'mobile_number': form.data.get('mobile_number', ''),
            'current_operator': form.data.get('current_operator', ''),
            'selected_plan': form.data.get('selected_plan', ''),
            'full_name': form.data.get('full_name', ''),
            'email': form.data.get('email', ''),
            'address': form.data.get('address', ''),
            'pincode': form.data.get('pincode', ''),
            'city': form.data.get('city', ''),
            'state': form.data.get('state', ''),
        }
        
        # Also preserve Step 1 data separately
        if form.data.get('mobile_number') or form.data.get('current_operator'):
            self.request.session['step1_data'] = {
                'mobile_number': form.data.get('mobile_number', ''),
                'current_operator': form.data.get('current_operator', ''),
            }
        
        return self.render_to_response(self.get_context_data(form=form))
    
    def payment_redirect(self, port_request, payment_method):
        """Redirect to appropriate page based on payment method"""
        if payment_method == 'online':
            return redirect('process_payment') + f'?plan_id={port_request.selected_plan.id}&port_request_id={port_request.id}'
        else:
            # For COD, redirect to status page
            messages.success(self.request, 
                           f"Port request submitted successfully! Tracking ID: {port_request.tracking_id}")
            return redirect('port_request_status', tracking_id=port_request.tracking_id)
    
    def get_payment_redirect_url(self, port_request, payment_method):
        """Generate payment redirect URL for AJAX responses"""
        if payment_method == 'online':
            from django.urls import reverse
            base_url = reverse('process_payment')
            return f"{base_url}?plan_id={port_request.selected_plan.id}&port_request_id={port_request.id}"
        else:
            return reverse('port_request_status', kwargs={
                'tracking_id': port_request.tracking_id
            })
    
    def generate_tracking_id(self):
        """Generate unique tracking ID"""
        today = datetime.now()
        date_str = today.strftime('%y%m%d')
        
        last_request = PortRequest.objects.filter(
            tracking_id__startswith=f'MNP{date_str}'
        ).order_by('-tracking_id').first()
        
        if last_request:
            last_number = int(last_request.tracking_id[-4:])
            next_number = last_number + 1
        else:
            next_number = 1
        
        return f'MNP{date_str}{next_number:04d}'
    def get(self, request, *args, **kwargs):
        """Handle AJAX requests for loading plans"""
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
            return self.handle_ajax_request(request)
        return super().get(request, *args, **kwargs)
    

    def generate_upc_code(self):
        """Generate Unique Porting Code"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


# views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

class UserPortRequestHistoryView(LoginRequiredMixin, ListView):
    """View for displaying user's port request history"""
    model = PortRequest
    template_name = 'plans/port_request_history.html'
    context_object_name = 'port_requests'
    paginate_by = 10
    
    def get_queryset(self):
        # Get user's port requests, ordered by creation date
        return PortRequest.objects.filter(
            user=self.request.user
        ).select_related(
            'current_operator', 'new_operator', 'selected_plan'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the full queryset (not paginated) for stats
        all_requests = PortRequest.objects.filter(user=self.request.user)
        
        # Calculate counts for each status
        context['total_requests'] = all_requests.count()
        context['pending_count'] = all_requests.filter(status='pending').count()
        context['processing_count'] = all_requests.filter(status='processing').count()
        context['completed_count'] = all_requests.filter(status='completed').count()
        context['failed_count'] = all_requests.filter(status='failed').count()
        
        # Get status choices for display
        context['status_choices'] = dict(PortRequest.STATUS_CHOICES)
        
        return context

class UserNewConnectionHistoryView(LoginRequiredMixin, ListView):
    """View to show user's new connection history"""
    model = NewConnectionRequest
    template_name = 'plans/new_connection_history.html'
    context_object_name = 'connection_requests'
    paginate_by = 10
    
    def get_queryset(self):
        return NewConnectionRequest.objects.filter(
            user=self.request.user
        ).select_related('operator', 'selected_plan').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My New Connections'
        return context
    


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
import traceback
# class NewConnectionView(LoginRequiredMixin, CreateView):
#     """View for creating new mobile connection request"""
#     model = NewConnectionRequest
#     form_class = NewConnectionForm
#     template_name = 'plans/new_connection.html'
    
#     def get_success_url(self):
#         if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             return None  # For AJAX requests, we return JSON
#         return reverse_lazy('new_connection_status')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['operators'] = TelecomOperator.objects.filter(is_active=True)
#         return context
    
#     def get_initial(self):
#         """Set initial values for the form"""
#         initial = super().get_initial()
#         initial['full_name'] = self.request.user.get_full_name()
#         initial['email'] = self.request.user.email
#         return initial
    
#     def form_valid(self, form):
#         try:
#             # Create new connection request
#             connection_request = form.save(commit=False)
#             connection_request.user = self.request.user
#             connection_request.status = 'pending'
            
#             # ✅ IMPORTANT: Check for duplicate pending requests
#             duplicate_check = NewConnectionRequest.objects.filter(
#                 user=self.request.user,
#                 operator=connection_request.operator,
#                 selected_plan=connection_request.selected_plan,
#                 full_name=connection_request.full_name,
#                 email=connection_request.email,
#                 status__in=['draft', 'pending']
#             ).exclude(id=connection_request.id if connection_request.id else None).first()
            
#             if duplicate_check:
#                 # Return existing request instead of creating new one
#                 print(f"✅ Using existing request: {duplicate_check.tracking_id}")
#                 if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                     return JsonResponse({
#                         'success': True,
#                         'message': 'Using existing connection request',
#                         'tracking_id': duplicate_check.tracking_id,
#                         'connection_request_id': duplicate_check.id,
#                         'redirect_url': self.get_payment_redirect_url(duplicate_check)
#                     })
#                 return self.payment_redirect(duplicate_check)
            
#             # Save the new request
#             connection_request.save()
            
#             print(f"✅ New connection request created: {connection_request.tracking_id}")
#             print(f"   User: {connection_request.email}")
#             print(f"   Operator: {connection_request.operator}")
#             print(f"   Plan: {connection_request.selected_plan}")
#             print(f"   Status: {connection_request.status}")
            
#             # Handle AJAX request
#             if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': True,
#                     'message': 'Connection request created successfully',
#                     'tracking_id': connection_request.tracking_id,
#                     'connection_request_id': connection_request.id,
#                     'redirect_url': self.get_payment_redirect_url(connection_request)
#                 })
            
#             # Handle regular form submission (COD)
#             return self.payment_redirect(connection_request)
            
#         except IntegrityError as e:
#             print(f"❌ IntegrityError in form_valid: {str(e)}")
            
#             # Handle duplicate tracking_id gracefully
#             if 'tracking_id' in str(e):
#                 # Get the latest request for this user
#                 existing_request = NewConnectionRequest.objects.filter(
#                     user=self.request.user
#                 ).order_by('-created_at').first()
                
#                 if existing_request:
#                     print(f"✅ Found existing request: {existing_request.tracking_id}")
                    
#                     if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                         return JsonResponse({
#                             'success': True,
#                             'message': 'Using existing connection request',
#                             'tracking_id': existing_request.tracking_id,
#                             'connection_request_id': existing_request.id,
#                             'redirect_url': self.get_payment_redirect_url(existing_request)
#                         })
#                     return self.payment_redirect(existing_request)
            
#             # Return error response
#             if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Database error occurred. Please try again.'
#                 })
            
#             messages.error(self.request, "Database error occurred. Please try again.")
#             return self.form_invalid(form)
            
#         except Exception as e:
#             print(f"❌ Error in form_valid: {str(e)}")
#             import traceback
#             print(traceback.format_exc())
            
#             if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'success': False,
#                     'error': str(e)
#                 })
            
#             messages.error(self.request, f"Error creating connection request: {str(e)}")
#             return self.form_invalid(form)
    
#     def form_invalid(self, form):
#         """Handle invalid form submission"""
#         print("❌ DEBUG: form_invalid method called!")
#         print(f"❌ DEBUG: Form errors: {form.errors}")
#         print(f"❌ DEBUG: Non-field errors: {form.non_field_errors()}")
        
#         # Check if it's an AJAX request
#         if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             # Convert form errors to JSON-friendly format
#             error_dict = {}
#             for field, errors in form.errors.items():
#                 error_dict[field] = [str(error) for error in errors]
            
#             return JsonResponse({
#                 'success': False,
#                 'errors': error_dict,
#                 'message': 'Please correct the errors below'
#             }, status=400)
        
#         messages.error(self.request, "Please correct the errors below.")
#         return super().form_invalid(form)
    
#     # ✅ FIXED METHOD: Use correct URL name 'process_payment' instead of 'payment_process'
#     def payment_redirect(self, connection_request):
#         """Redirect to appropriate page based on payment method"""
#         payment_method = self.request.POST.get('payment_method', 'cod')
        
#         if payment_method == 'online':
#             # ✅ CORRECTED: Use 'process_payment' URL name with query parameters
#             return redirect('process_payment') + f'?plan_id={connection_request.selected_plan.id}&new_connection=true&connection_request_id={connection_request.id}'
#         else:
#             # Redirect to status page for COD
#             messages.success(self.request, 
#                            f"Connection request submitted successfully! Tracking ID: {connection_request.tracking_id}")
#             return redirect('new_connection_status', tracking_id=connection_request.tracking_id)
    
#     # ✅ FIXED METHOD: Use correct URL name 'process_payment' instead of 'payment_process'
#     def get_payment_redirect_url(self, connection_request):
#         """Generate payment redirect URL for AJAX responses"""
#         payment_method = self.request.POST.get('payment_method', 'cod')
        
#         if payment_method == 'online':
#             # ✅ CORRECTED: Build URL with query parameters
#             from django.urls import reverse
#             base_url = reverse('process_payment')
#             return f"{base_url}?plan_id={connection_request.selected_plan.id}&new_connection=true&connection_request_id={connection_request.id}"
#         else:
#             return reverse('new_connection_status', kwargs={
#                 'tracking_id': connection_request.tracking_id
#             })

class NewConnectionView(LoginRequiredMixin, CreateView):
    """View for creating new mobile connection request"""
    model = NewConnectionRequest
    form_class = NewConnectionForm
    template_name = 'plans/new_connection.html'
    
    def get_success_url(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return None  # For AJAX requests, we return JSON
        return reverse_lazy('new_connection_status')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operators'] = TelecomOperator.objects.filter(is_active=True)
        return context
    
    def get_initial(self):
        """Set initial values for the form"""
        initial = super().get_initial()
        initial['full_name'] = self.request.user.get_full_name()
        initial['email'] = self.request.user.email
        return initial
    
    def form_valid(self, form):
        try:
            # Create new connection request
            connection_request = form.save(commit=False)
            connection_request.user = self.request.user
            connection_request.status = 'pending'
            
            # ✅ IMPORTANT: Check for duplicate pending requests
            duplicate_check = NewConnectionRequest.objects.filter(
                user=self.request.user,
                operator=connection_request.operator,
                selected_plan=connection_request.selected_plan,
                full_name=connection_request.full_name,
                email=connection_request.email,
                status__in=['draft', 'pending']
            ).exclude(id=connection_request.id if connection_request.id else None).first()
            
            if duplicate_check:
                # Return existing request instead of creating new one
                print(f"✅ Using existing request: {duplicate_check.tracking_id}")
                
                # ✅ CRITICAL: Handle payment for duplicate request
                payment_method = self.request.POST.get('payment_method', 'cod')
                if payment_method == 'cod':
                    self.handle_cod_payment_for_duplicate(duplicate_check)
                
                if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Using existing connection request',
                        'tracking_id': duplicate_check.tracking_id,
                        'connection_request_id': duplicate_check.id,
                        'redirect_url': self.get_payment_redirect_url(duplicate_check)
                    })
                return self.payment_redirect(duplicate_check)
            
            # Save the new request
            connection_request.save()
            
            print(f"✅ New connection request created: {connection_request.tracking_id}")
            print(f"   User: {connection_request.email}")
            print(f"   Operator: {connection_request.operator}")
            print(f"   Plan: {connection_request.selected_plan}")
            print(f"   Status: {connection_request.status}")
            
            # ✅ CRITICAL: Handle payment based on payment method
            payment_method = self.request.POST.get('payment_method', 'cod')
            
            # Create Payment record for COD
            if payment_method == 'cod':
                payment = self.create_cod_payment(connection_request)
                
                # Store payment ID in session for later use
                self.request.session['current_payment_id'] = payment.id
                
                # For COD, update connection request status directly to payment_completed
                connection_request.status = 'payment_completed'
                connection_request.save()
                
                # Create plan history for COD
                self.create_plan_history_for_cod(payment, connection_request.selected_plan)
            
            # Handle AJAX request
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Connection request created successfully',
                    'tracking_id': connection_request.tracking_id,
                    'connection_request_id': connection_request.id,
                    'redirect_url': self.get_payment_redirect_url(connection_request)
                })
            
            # Handle regular form submission (COD)
            return self.payment_redirect(connection_request)
            
        except IntegrityError as e:
            print(f"❌ IntegrityError in form_valid: {str(e)}")
            
            # Handle duplicate tracking_id gracefully
            if 'tracking_id' in str(e):
                # Get the latest request for this user
                existing_request = NewConnectionRequest.objects.filter(
                    user=self.request.user
                ).order_by('-created_at').first()
                
                if existing_request:
                    print(f"✅ Found existing request: {existing_request.tracking_id}")
                    
                    # ✅ CRITICAL: Handle payment for existing request
                    payment_method = self.request.POST.get('payment_method', 'cod')
                    if payment_method == 'cod':
                        self.handle_cod_payment_for_duplicate(existing_request)
                    
                    if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'Using existing connection request',
                            'tracking_id': existing_request.tracking_id,
                            'connection_request_id': existing_request.id,
                            'redirect_url': self.get_payment_redirect_url(existing_request)
                        })
                    return self.payment_redirect(existing_request)
            
            # Return error response
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Database error occurred. Please try again.'
                })
            
            messages.error(self.request, "Database error occurred. Please try again.")
            return self.form_invalid(form)
            
        except Exception as e:
            print(f"❌ Error in form_valid: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            
            messages.error(self.request, f"Error creating connection request: {str(e)}")
            return self.form_invalid(form)
    
    def handle_cod_payment_for_duplicate(self, connection_request):
        """Handle COD payment for duplicate/new connection request"""
        # Check if payment already exists
        existing_payment = Payment.objects.filter(
            new_connection=connection_request,
            user=self.request.user,
            payment_method='cod',
            payment_status='completed'
        ).first()
        
        if existing_payment:
            print(f"✅ Using existing COD payment: {existing_payment.bill_number}")
            self.request.session['current_payment_id'] = existing_payment.id
            return
        
        # Create new COD payment
        payment = self.create_cod_payment(connection_request)
        
        # Store payment ID in session
        self.request.session['current_payment_id'] = payment.id
        
        # Update connection request status
        connection_request.status = 'payment_completed'
        connection_request.save()
        
        # Create plan history
        self.create_plan_history_for_cod(payment, connection_request.selected_plan)
    
    def create_cod_payment(self, connection_request):
        """Create a COD payment record for new connection"""
        from django.utils import timezone
        import uuid
        from datetime import datetime
        
        # Generate a unique transaction ID for COD
        transaction_id = f"NEW-COD-{uuid.uuid4().hex[:12].upper()}"
        
        # Generate bill number
        bill_number = f"BILL-NEW-COD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create payment record
        payment = Payment.objects.create(
            user=self.request.user,
            amount=connection_request.selected_plan.price,
            payment_method='cod',
            payment_status='completed',  # COD is considered completed
            transaction_id=transaction_id,
            bill_number=bill_number,
            payment_date=timezone.now(),
            plan=connection_request.selected_plan,
            new_connection=connection_request
        )
        
        print(f"✅ Created COD payment for new connection: {payment.bill_number}")
        return payment
    
    def create_plan_history_for_cod(self, payment, selected_plan):
        """Create plan history entry for COD payments (new connection)"""
        from django.utils import timezone
        from datetime import timedelta
        
        validity_days = selected_plan.validity
        
        if selected_plan.validity_unit == 'months':
            validity_days = validity_days * 30
        elif selected_plan.validity_unit == 'year':
            validity_days = validity_days * 365
        
        # Create plan history
        UserPlanHistory.objects.create(
            user=self.request.user,
            plan=selected_plan,
            purchased_on=payment.payment_date,
            activated_on=timezone.now(),
            expires_on=timezone.now() + timedelta(days=validity_days),
            status='active',
            transaction_id=payment.transaction_id,
            new_connection=payment.new_connection  # Link to new connection

            # Note: new_connection field is not in UserPlanHistory model
            # If you want to link it, you need to add the field to the model
        )
        
        # Update user's current plan
        try:
            if hasattr(self.request.user, 'profile'):
                self.request.user.profile.current_plan = selected_plan
                self.request.user.profile.plan_start_date = timezone.now()
                self.request.user.profile.plan_expiry_date = timezone.now() + timedelta(days=validity_days)
                self.request.user.profile.save()
        except AttributeError:
            pass  # No profile model
        
        print(f"✅ Created UserPlanHistory for new connection COD payment: {payment.bill_number}")
    
    def form_invalid(self, form):
        """Handle invalid form submission"""
        print("❌ DEBUG: form_invalid method called!")
        print(f"❌ DEBUG: Form errors: {form.errors}")
        print(f"❌ DEBUG: Non-field errors: {form.non_field_errors()}")
        
        # Check if it's an AJAX request
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Convert form errors to JSON-friendly format
            error_dict = {}
            for field, errors in form.errors.items():
                error_dict[field] = [str(error) for error in errors]
            
            return JsonResponse({
                'success': False,
                'errors': error_dict,
                'message': 'Please correct the errors below'
            }, status=400)
        
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
    def payment_redirect(self, connection_request):
        """Redirect to appropriate page based on payment method"""
        payment_method = self.request.POST.get('payment_method', 'cod')
        
        if payment_method == 'online':
            return redirect('process_payment') + f'?plan_id={connection_request.selected_plan.id}&new_connection=true&connection_request_id={connection_request.id}'
        else:
            # For COD, redirect to status page with success message
            messages.success(self.request, 
                           f"New connection request submitted successfully! Tracking ID: {connection_request.tracking_id}")
            return redirect('new_connection_status', tracking_id=connection_request.tracking_id)
    
    def get_payment_redirect_url(self, connection_request):
        """Generate payment redirect URL for AJAX responses"""
        payment_method = self.request.POST.get('payment_method', 'cod')
        
        if payment_method == 'online':
            from django.urls import reverse
            base_url = reverse('process_payment')
            return f"{base_url}?plan_id={connection_request.selected_plan.id}&new_connection=true&connection_request_id={connection_request.id}"
        else:
            return reverse('new_connection_status', kwargs={
                'tracking_id': connection_request.tracking_id
            })












class PortRequestStatusView(LoginRequiredMixin, DetailView):
    """View to check port request status"""
    model = PortRequest
    template_name = 'plans/port_request_status.html'
    context_object_name = 'port_request'
    slug_field = 'tracking_id'
    slug_url_kwarg = 'tracking_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add plan details
        context['plan_details'] = {
            'name': self.object.selected_plan.name,
            'price': self.object.selected_plan.price,
            'validity': self.object.selected_plan.get_full_validity(),
            'data': self.object.selected_plan.data_allowance,
            'bonus': self.object.selected_plan.port_in_bonus,
        }
        
        # Add porting steps based on status
        context['steps'] = self.get_porting_steps(self.object.status)
        
        return context
    
    def get_porting_steps(self, status):
        """Get porting process steps based on current status"""
        steps = [
            {'id': 1, 'name': 'Request Submitted', 'icon': 'fas fa-paper-plane', 
             'status': 'completed', 'description': 'Port request submitted successfully'},
            {'id': 2, 'name': 'UPC Generated', 'icon': 'fas fa-qrcode',
             'status': 'completed' if status != 'pending' else 'pending',
             'description': 'Unique Porting Code generated'},
            {'id': 3, 'name': 'Documents Verified', 'icon': 'fas fa-file-check',
             'status': 'completed' if status in ['verified', 'processing', 'completed'] else 'pending',
             'description': 'Documents verified and approved'},
            {'id': 4, 'name': 'Porting in Progress', 'icon': 'fas fa-sync-alt',
             'status': 'completed' if status == 'completed' else 
                      'active' if status == 'processing' else 'pending',
             'description': 'Number porting in progress'},
            {'id': 5, 'name': 'Porting Complete', 'icon': 'fas fa-check-circle',
             'status': 'completed' if status == 'completed' else 'pending',
             'description': 'Number successfully ported'},
        ]
        return steps

class NewConnectionStatusView(LoginRequiredMixin, DetailView):
    """View to check new connection status"""
    model = NewConnectionRequest
    template_name = 'plans/new_connection_status.html'
    context_object_name = 'connection_request'
    slug_field = 'tracking_id'
    slug_url_kwarg = 'tracking_id'


    def get_queryset(self):
        return NewConnectionRequest.objects.filter(user=self.request.user)
    
    def get_object(self):
        tracking_id = self.kwargs.get('tracking_id')
        return get_object_or_404(NewConnectionRequest, tracking_id=tracking_id, user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add connection steps based on status
        context['steps'] = self.get_connection_steps(self.object.status)
        
        return context
    
    def get_connection_steps(self, status):
        """Get connection process steps based on current status"""
        steps = [
            {'id': 1, 'name': 'Request Submitted', 'icon': 'fas fa-paper-plane',
             'status': 'completed', 'description': 'Connection request submitted'},
            {'id': 2, 'name': 'Document Verification', 'icon': 'fas fa-file-check',
             'status': 'completed' if status != 'pending' else 'pending',
             'description': 'KYC documents verification'},
            {'id': 3, 'name': 'SIM Dispatch', 'icon': 'fas fa-truck',
             'status': 'completed' if status in ['sim_delivered', 'activated'] else 
                      'active' if status == 'sim_dispatch' else 'pending',
             'description': 'SIM card dispatched for delivery'},
            {'id': 4, 'name': 'SIM Delivered', 'icon': 'fas fa-box-open',
             'status': 'completed' if status in ['sim_delivered', 'activated'] else 'pending',
             'description': 'SIM card delivered to address'},
            {'id': 5, 'name': 'Activation Complete', 'icon': 'fas fa-check-circle',
             'status': 'completed' if status == 'activated' else 'pending',
             'description': 'Number activated and ready to use'},
        ]
        return steps
class PlanListView(ListView):
    """View to list all plans with filtering"""
    model = Plan
    template_name = 'plans/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Plan.objects.filter(is_active=True).select_related('operator', 'category')
        
        # Apply filters
        plan_type_filter = self.request.GET.get('plan_type_filter', 'new_connection')  # Default to new_connection
        operator = self.request.GET.get('operator')
        category = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        # Apply Plan Type filter
        if plan_type_filter == 'new_connection':
            queryset = queryset.filter(plan_type='new_connection')
        elif plan_type_filter == 'port_in':
            queryset = queryset.filter(plan_type='port_in')
        elif plan_type_filter == '' or plan_type_filter is None:
            # Show all plans if empty or None
            pass
        
        if operator:
            queryset = queryset.filter(operator_id=operator)
        
        if category:
            queryset = queryset.filter(category_id=category)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Data filter handling
        data_filter = self.request.GET.getlist('data')
        if data_filter:
            data_q = Q()
            if 'unlimited' in data_filter:
                data_q |= Q(data_allowance__icontains='unlimited')
            if '2gb+' in data_filter:
                data_q |= Q(data_allowance__icontains='2gb') | Q(data_allowance__icontains='2 gb')
            if '1gb+' in data_filter:
                data_q |= Q(data_allowance__icontains='1gb') | Q(data_allowance__icontains='1 gb')
            queryset = queryset.filter(data_q)
        
        # Apply sorting (using the 'sort' parameter from the template)
        sort_by = self.request.GET.get('sort')
        if sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == '-price':
            queryset = queryset.order_by('-price')
        elif sort_by == 'validity':
            queryset = queryset.order_by('validity')
        elif sort_by == '-validity':
            queryset = queryset.order_by('-validity')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-is_popular', 'price')
        elif sort_by == 'featured':
            queryset = queryset.order_by('-is_featured', 'price')
        else:
            queryset = queryset.order_by('-is_popular', 'price')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_operators'] = TelecomOperator.objects.filter(is_active=True)
        context['categories'] = PlanCategory.objects.all()
        
        # Add plan type filter value to context
        context['plan_type_filter'] = self.request.GET.get('plan_type_filter', 'new_connection')
        
        return context

class PlanDetailView(DetailView):
    """View to show plan details"""
    model = Plan
    template_name = 'plans/plan_detail.html'
    context_object_name = 'plan'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get similar plans
        similar_plans = Plan.objects.filter(
            operator=self.object.operator,
            plan_type=self.object.plan_type,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        
        context['similar_plans'] = similar_plans
        
        # Check if user is authenticated to show action buttons
        context['user_has_active_connection'] = False
        if self.request.user.is_authenticated:
            # Check if user already has this operator's connection
            context['user_has_active_connection'] = NewConnectionRequest.objects.filter(
                user=self.request.user,
                operator=self.object.operator,
                status__in=['completed', 'processing']
            ).exists()
        
        return context

# API Views for AJAX requests
class GetPortInPlansView(View):
    """API view to get port-in plans for an operator"""
    def get(self, request, *args, **kwargs):
        operator_id = request.GET.get('operator_id')
        
        if not operator_id:
            return JsonResponse({'error': 'Operator ID required'}, status=400)
        
        plans = Plan.objects.filter(
            operator_id=operator_id,
            plan_type='port_in',
            is_active=True
        ).values('id', 'name', 'price', 'validity', 'validity_unit', 
                'data_allowance', 'port_in_bonus')
        
        return JsonResponse(list(plans), safe=False)



class GetNewConnectionPlansView(View):
    """API view to get new connection plans for an operator"""
    def get(self, request, *args, **kwargs):
        operator_id = request.GET.get('operator_id')
        
        if not operator_id:
            return JsonResponse({'error': 'Operator ID required'}, status=400)
        
        try:
            # Filter plans for new connections only
            plans = Plan.objects.filter(
                operator_id=operator_id,
                plan_type='new_connection',  # This is the correct field
                is_active=True
            )
            
            plans_data = []
            for plan in plans:
                plans_data.append({
                    'id': plan.id,
                    'name': plan.name,
                    'operator_name': plan.operator.name if plan.operator else '',
                    'price': float(plan.price) if plan.price else 0,
                    'validity': plan.validity,
                    'validity_unit': plan.get_validity_unit_display(),
                    'data_allowance': plan.data_allowance or 'Not specified',
                    'voice_calls': plan.voice_calls or 'Not specified',
                    'sms': plan.sms or 'Not specified',
                    'new_connection_bonus': plan.new_connection_bonus or '',
                    'description': plan.description or '',
                })
            
            return JsonResponse(plans_data, safe=False)
            
        except Exception as e:
            print(f"Error fetching new connection plans: {e}")
            return JsonResponse({'error': str(e)}, status=500)

class CheckMNPEligibilityView(View):
    """API view to check MNP eligibility"""
    def get(self, request, *args, **kwargs):
        mobile_number = request.GET.get('mobile_number')
        
        if not mobile_number or len(mobile_number) != 10:
            return JsonResponse({
                'eligible': False,
                'message': 'Invalid mobile number format'
            })
        
        # Basic validation
        is_valid = mobile_number[0] in '6789'
        
        # Check if already porting
        is_porting = PortRequest.objects.filter(
            mobile_number=mobile_number,
            status__in=['pending', 'upc_sent', 'processing']
        ).exists()
        
        eligible = is_valid and not is_porting
        
        return JsonResponse({
            'eligible': eligible,
            'message': 'Number is eligible for porting' if eligible else 
                      'Number may not be eligible for porting'
        })

class UserConnectionHistoryView(LoginRequiredMixin, ListView):
    """View to show user's connection history"""
    model = NewConnectionRequest
    template_name = 'plans/connection_history.html'
    context_object_name = 'connection_requests'
    
    def get_queryset(self):
        return NewConnectionRequest.objects.filter(
            user=self.request.user
        ).select_related('operator', 'connection_type').order_by('-created_at')


# views.py
class CancelConnectionRequestView(LoginRequiredMixin, View):
    """View to cancel a new connection request"""
    
    def post(self, request, tracking_id):
        try:
            connection_request = NewConnectionRequest.objects.get(
                tracking_id=tracking_id,
                user=request.user,
                status='pending'  # Only allow canceling pending requests
            )
            
            connection_request.status = 'cancelled'
            connection_request.notes = f"Cancelled by user. Reason: {request.POST.get('reason', 'Not specified')}"
            connection_request.save()
            
            messages.success(request, "Connection request cancelled successfully.")
            return redirect('new_connection_status', tracking_id=tracking_id)
            
        except NewConnectionRequest.DoesNotExist:
            messages.error(request, "Connection request not found or cannot be cancelled.")
            return redirect('new_connection_status', tracking_id=tracking_id)



class OperatorListView(ListView):
    model = TelecomOperator
    template_name = 'telecom/operator_list.html'
    context_object_name = 'operators'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = TelecomOperator.objects.filter(is_active=True)
        operator_type = self.request.GET.get('type')
        if operator_type:
            queryset = queryset.filter(operator_type=operator_type)
        return queryset



class SearchView(ListView):
    template_name = 'telecom/search_results.html'
    context_object_name = 'plans'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        filter_type = self.request.GET.get('type', 'all')
        
        if query:
            # Base queryset
            plans = Plan.objects.all()
            operators = TelecomOperator.objects.all()
            
            # Apply search to plans
            plans = plans.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(operator__name__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()
            
            # Apply search to operators
            operators = operators.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(operator_type__icontains=query)
            ).distinct()
            
            # Apply filters
            if filter_type == 'plans':
                return plans
            elif filter_type == 'operators':
                return operators
            elif filter_type in ['mobile', 'broadband', 'dth']:
                plans = plans.filter(operator__operator_type=filter_type)
                operators = operators.filter(operator_type=filter_type)
                return list(plans) + list(operators)
            else:
                # Return all results
                return list(plans) + list(operators)
        
        return Plan.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        filter_type = self.request.GET.get('type', 'all')
        
        # Get separate querysets for counts
        if query:
            plans = Plan.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(operator__name__icontains=query)
            ).distinct()
            
            operators = TelecomOperator.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).distinct()
            
            # Apply type filter
            if filter_type in ['mobile', 'broadband', 'dth']:
                plans = plans.filter(operator__operator_type=filter_type)
                operators = operators.filter(operator_type=filter_type)
            
            context['plans'] = plans
            context['operators'] = operators
            context['plans_count'] = plans.count()
            context['operators_count'] = operators.count()
            context['total_results'] = plans.count() + operators.count()
        else:
            context['plans'] = Plan.objects.none()
            context['operators'] = TelecomOperator.objects.none()
            context['plans_count'] = 0
            context['operators_count'] = 0
            context['total_results'] = 0
        
        context['query'] = query
        context['filter_type'] = filter_type
        
        return context

# class CoverageCheckView(TemplateView):
#     template_name = 'telecom/coverage_check.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         pincode = self.request.GET.get('pincode')
#         operator_id = self.request.GET.get('operator')
        
#         if pincode and operator_id:
#             try:
#                 operator = TelecomOperator.objects.get(id=operator_id)
#                 coverage = ServiceArea.objects.filter(
#                     operator=operator,
#                     pincodes__contains=pincode,
#                     availability=True
#                 ).first()
#                 context['coverage_result'] = {
#                     'operator': operator,
#                     'pincode': pincode,
#                     'available': bool(coverage),
#                     'area': coverage
#                 }
#             except TelecomOperator.DoesNotExist:
#                 pass
#         return context
    

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Q
from .models import TelecomOperator, ServiceArea
from plans.models import Plan, PlanCategory

class CoverageCheckView(TemplateView):
    template_name = 'telecom/coverage_check.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pincode = self.request.GET.get('pincode')
        operator_id = self.request.GET.get('operator')
        
        context['all_operators'] = TelecomOperator.objects.filter(is_active=True)
        context['all_categories'] = PlanCategory.objects.all()
        
        if pincode and len(pincode) == 6:
            try:
                # Clean pincode
                pincode = pincode.strip()
                
                if operator_id:
                    # Check specific operator
                    operator = get_object_or_404(TelecomOperator, id=operator_id, is_active=True)
                    coverage = ServiceArea.objects.filter(
                        operator=operator,
                        pincodes__contains=pincode,
                        availability=True
                    ).first()
                    
                    if coverage:
                        context['coverage_result'] = {
                            'operator': operator,
                            'area': coverage,
                            'available': True
                        }
                    else:
                        context['coverage_result'] = None
                else:
                    # Check all operators
                    operators_with_coverage = []
                    for operator in TelecomOperator.objects.filter(is_active=True):
                        coverage = ServiceArea.objects.filter(
                            operator=operator,
                            pincodes__contains=pincode,
                            availability=True
                        ).first()
                        if coverage:
                            operators_with_coverage.append({
                                'operator': operator,
                                'area': coverage
                            })
                    
                    if operators_with_coverage:
                        context['coverage_result'] = {
                            'operator': operators_with_coverage[0]['operator'],
                            'area': operators_with_coverage[0]['area'],
                            'available': True,
                            'all_operators': operators_with_coverage
                        }
                    else:
                        context['coverage_result'] = None
            
            except Exception as e:
                context['error'] = str(e)
        
        return context
    

class OperatorDetailView(DetailView):
    model = TelecomOperator
    template_name = 'telecom/operator_detail.html'
    context_object_name = 'operator'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get plans for this operator
        from plans.models import Plan
        plans = Plan.objects.filter(
            operator=self.object,
            is_active=True
        ).order_by('price')
        
        # Calculate popular plans count
        popular_plans_count = plans.filter(is_popular=True).count()
        
        # Get service areas
        from .models import ServiceArea
        service_areas = ServiceArea.objects.filter(
            operator=self.object,
            availability=True
        )
        
        # Get similar operators
        similar_operators = TelecomOperator.objects.filter(
            operator_type=self.object.operator_type,
            is_active=True
        ).exclude(id=self.object.id)[:3]
        
        # Add to context
        context.update({
            'plans': plans,
            'service_areas': service_areas,
            'similar_operators': similar_operators,
            'popular_plans_count': popular_plans_count,
            'plans_count': plans.count(),
            'service_areas_count': service_areas.count(),
        })
        
        return context
    

def check_port_request(request, mobile_number):
    """Check if mobile number already has active port request"""
    has_active_request = PortRequest.objects.filter(
        mobile_number=mobile_number,
        user=request.user,
        status__in=['pending', 'upc_sent', 'processing']
    ).exists()
    
    return JsonResponse({
        'has_active_request': has_active_request,
        'mobile_number': mobile_number
    })