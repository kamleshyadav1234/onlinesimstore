from django.shortcuts import render

# Create your views here.
# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
import razorpay
import json
import uuid
from django.db.models import Sum

from users.models import UserPlanHistory  # Add this import

from .models import Payment, Coupon
from plans.models import Plan
import logging

logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def process_payment(request):
    """Show payment page for a plan"""
    plan_id = request.GET.get('plan_id')
    coupon_code = request.GET.get('coupon')
    
    if not plan_id:
        messages.error(request, 'Please select a plan first.')
        return redirect('plan_list')
    
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    
    # Calculate amount
    amount = float(plan.price)
    discount = 0
    coupon = None
    
    # Apply coupon if provided
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
            if coupon.is_valid():
                if coupon.discount_type == 'percentage':
                    discount = (amount * float(coupon.discount_value)) / 100
                    if coupon.max_discount and discount > float(coupon.max_discount):
                        discount = float(coupon.max_discount)
                else:  # fixed amount
                    discount = float(coupon.discount_value)
                
                # Ensure discount doesn't exceed amount
                discount = min(discount, amount)
        except Coupon.DoesNotExist:
            messages.warning(request, 'Invalid coupon code')
    
    final_amount = amount - discount
    
    razorpay_order = None
    payment_record = None  # Initialize payment record
    
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        try:
            receipt_id = f'order_{uuid.uuid4().hex[:10]}'
            
            order_data = {
                'amount': int(final_amount * 100),  
                'currency': 'INR',
                'receipt': receipt_id,
                'notes': {
                    'plan_id': str(plan.id),
                    'user_id': str(request.user.id),
                }
            }
            razorpay_order = client.order.create(data=order_data)
            
            payment_record = Payment.objects.create(
                user=request.user,
                plan=plan,
                amount=final_amount,
                payment_method='razorpay',  
                transaction_id=receipt_id,  
                payment_status='pending',
                razorpay_order_id=razorpay_order['id'],
            )
            
            request.session['current_payment_id'] = payment_record.id
            
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            messages.warning(request, 'Payment gateway is currently unavailable. Please try again later.')
    
    context = {
        'plan': plan,
        'amount': amount,
        'discount': discount,
        'final_amount': final_amount,
        'coupon': coupon,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'payment_record': payment_record,
    }
    
    return render(request, 'payments/process_payment.html', context)

@login_required
def apply_coupon(request):
    """Apply coupon and return updated amount"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            coupon_code = data.get('coupon_code')
            
            if not plan_id or not coupon_code:
                return JsonResponse({'success': False, 'error': 'Missing parameters'})
            
            plan = get_object_or_404(Plan, id=plan_id)
            amount = float(plan.price)
            
            try:
                coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
                
                if not coupon.is_valid():
                    return JsonResponse({
                        'success': False,
                        'error': 'Coupon has expired or reached usage limit'
                    })
                
                if float(plan.price) < float(coupon.min_order_amount):
                    return JsonResponse({
                        'success': False,
                        'error': f'Minimum order amount should be ₹{coupon.min_order_amount}'
                    })
                
                # Calculate discount
                if coupon.discount_type == 'percentage':
                    discount = (amount * float(coupon.discount_value)) / 100
                    if coupon.max_discount and discount > float(coupon.max_discount):
                        discount = float(coupon.max_discount)
                else:  # fixed amount
                    discount = float(coupon.discount_value)
                
                discount = min(discount, amount)
                final_amount = amount - discount
                
                return JsonResponse({
                    'success': True,
                    'discount': discount,
                    'final_amount': final_amount,
                    'coupon_code': coupon.code,
                    'message': f'Coupon applied successfully! You saved ₹{discount:.2f}'
                })
                
            except Coupon.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid coupon code'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def payment_webhook(request):
    """Handle Razorpay webhook for payment verification"""
    if request.method == 'POST':
        try:
            # Verify webhook signature
            body = request.body.decode('utf-8')
            signature = request.headers.get('X-Razorpay-Signature', '')
            
            client.utility.verify_webhook_signature(
                body, 
                signature, 
                settings.RAZORPAY_WEBHOOK_SECRET
            )
            
            # Process webhook
            data = json.loads(body)
            event = data.get('event')
            
            if event == 'payment.captured':
                payment_data = data.get('payload', {}).get('payment', {}).get('entity', {})
                
                # Update payment status
                try:
                    payment = Payment.objects.get(
                        razorpay_payment_id=payment_data.get('id')
                    )
                    payment.payment_status = 'completed'
                    payment.save()
                    
                    logger.info(f"Payment completed: {payment.bill_number}")
                    
                except Payment.DoesNotExist:
                    logger.error(f"Payment not found: {payment_data.get('id')}")
            
            elif event == 'payment.failed':
                payment_data = data.get('payload', {}).get('payment', {}).get('entity', {})
                
                try:
                    payment = Payment.objects.get(
                        razorpay_payment_id=payment_data.get('id')
                    )
                    payment.payment_status = 'failed'
                    payment.save()
                    
                    logger.info(f"Payment failed: {payment.bill_number}")
                    
                except Payment.DoesNotExist:
                    logger.error(f"Payment not found: {payment_data.get('id')}")
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)



@login_required
def payment_success(request):
    """Show payment success page"""
    payment_id = request.GET.get('payment_id')  # Razorpay payment ID (e.g., "pay_S9OHc8lbjEOoBR")
    order_id = request.GET.get('order_id')      # Razorpay order ID (e.g., "order_S9OGSLzwxUHKWc")
    
    payment = None
    
    # Try to find payment by different identifiers
    if payment_id:
        try:
            # ❌ REMOVE THIS - Don't try to convert to int for Razorpay IDs
            # try:
            #     payment = Payment.objects.get(id=int(payment_id), user=request.user)
            # except (ValueError, Payment.DoesNotExist):
            #     # Try as string ID
            #     payment = Payment.objects.get(id=payment_id, user=request.user)
            
            # ✅ FIRST: Try razorpay_payment_id (this is the correct field)
            payment = Payment.objects.get(razorpay_payment_id=payment_id, user=request.user)
            
        except Payment.DoesNotExist:
            # Also try transaction_id (some systems store it there)
            try:
                payment = Payment.objects.get(transaction_id=payment_id, user=request.user)
            except Payment.DoesNotExist:
                pass
    
    # If still not found, try with order_id
    if not payment and order_id:
        try:
            payment = Payment.objects.get(razorpay_order_id=order_id, user=request.user)
        except Payment.DoesNotExist:
            pass
    
    # If payment is still None, get the latest payment for this user
    if not payment:
        try:
            payment = Payment.objects.filter(user=request.user).latest('payment_date')
        except Payment.DoesNotExist:
            messages.info(request, 'No payment found. Please check your payment history.')
            return redirect('payment_history')
    
    # Now we have the payment, update status to completed
    if payment.payment_status == 'pending':
        payment.payment_status = 'completed'
        
        # Make sure Razorpay IDs are saved
        if payment_id and not payment.razorpay_payment_id:
            payment.razorpay_payment_id = payment_id
        if order_id and not payment.razorpay_order_id:
            payment.razorpay_order_id = order_id
        
        payment.save()
    
    # Activate user's plan
    if payment.payment_status == 'completed' and payment.plan:
        # Check if already activated
        plan_history_exists = UserPlanHistory.objects.filter(
            user=request.user,
            plan=payment.plan,
            transaction_id=payment.transaction_id
        ).exists()
        
        if not plan_history_exists:
            from datetime import timedelta
            from django.utils import timezone
            
            validity_days = payment.plan.validity
            
            if payment.plan.validity_unit == 'months':
                validity_days = validity_days * 30  # Approximate
            elif payment.plan.validity_unit == 'year':
                validity_days = validity_days * 365  # Approximate
            
            # Create plan history
            UserPlanHistory.objects.create(
                user=request.user,
                plan=payment.plan,
                purchased_on=payment.payment_date,
                activated_on=timezone.now(),
                expires_on=timezone.now() + timedelta(days=validity_days),
                status='active',
                transaction_id=payment.transaction_id
            )
            
            # Also update user's current plan
            try:
                if hasattr(request.user, 'profile'):
                    request.user.profile.current_plan = payment.plan
                    request.user.profile.plan_start_date = timezone.now()
                    request.user.profile.plan_expiry_date = timezone.now() + timedelta(days=validity_days)
                    request.user.profile.save()
            except AttributeError:
                pass  # No profile model
            
            messages.success(request, f'Plan activated successfully! It will expire in {payment.plan.get_full_validity}.')
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/success.html', context)




# @login_required
# def payment_success(request):
#     """Show payment success page"""
#     payment_id = request.GET.get('payment_id')
#     order_id = request.GET.get('order_id')
    
#     payment = None
    
#     # Try to find payment by different identifiers
#     if payment_id:
#         try:
#             # First try to convert to int (if it's a numeric ID)
#             try:
#                 payment = Payment.objects.get(id=int(payment_id), user=request.user)
#             except (ValueError, Payment.DoesNotExist):
#                 # Try as string ID
#                 payment = Payment.objects.get(id=payment_id, user=request.user)
#         except Payment.DoesNotExist:
#             # Try razorpay_payment_id
#             try:
#                 payment = Payment.objects.get(razorpay_payment_id=payment_id, user=request.user)
#             except Payment.DoesNotExist:
#                 pass
    
#     if not payment and order_id:
#         try:
#             payment = Payment.objects.get(razorpay_order_id=order_id, user=request.user)
#         except Payment.DoesNotExist:
#             pass
    
#     if not payment:
#         try:
#             payment = Payment.objects.filter(user=request.user).latest('payment_date')
#         except Payment.DoesNotExist:
#             messages.info(request, 'No payment found. Please check your payment history.')
#             return redirect('payment_history')
    
#     if payment.payment_status == 'completed' and payment.plan:
#         plan_history_exists = UserPlanHistory.objects.filter(
#             user=request.user,
#             plan=payment.plan,
#             transaction_id=payment.transaction_id
#         ).exists()
        
#         if not plan_history_exists:
#             from datetime import timedelta
#             from django.utils import timezone
            
#             validity_days = payment.plan.validity
            
#             if payment.plan.validity_unit == 'months':
#                 validity_days = validity_days * 30  # Approximate
#             elif payment.plan.validity_unit == 'year':
#                 validity_days = validity_days * 365  # Approximate
            
#             UserPlanHistory.objects.create(
#                 user=request.user,
#                 plan=payment.plan,
#                 purchased_on=payment.payment_date,
#                 activated_on=timezone.now(),
#                 expires_on=timezone.now() + timedelta(days=validity_days),
#                 status='active',
#                 transaction_id=payment.transaction_id
#             )
            
#             messages.success(request, f'Plan activated successfully! It will expire in {payment.plan.get_full_validity}.')
    
#     context = {
#         'payment': payment,
#     }
    
#     return render(request, 'payments/success.html', context)

@login_required
def payment_failed(request):
    error_message = request.GET.get('error', 'Payment failed. Please try again.')
    
    context = {
        'error_message': error_message
    }
    
    return render(request, 'payments/failed.html', context)
@login_required
def create_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            payment_method = data.get('payment_method')
            coupon_code = data.get('coupon_code')
            
            if not plan_id:
                return JsonResponse({'success': False, 'error': 'Plan ID is required'})
            
            plan = get_object_or_404(Plan, id=plan_id, is_active=True)
            
            # Calculate amount with coupon
            amount = float(plan.price)
            discount = 0
            
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
                    if coupon.is_valid() and float(plan.price) >= float(coupon.min_order_amount):
                        if coupon.discount_type == 'percentage':
                            discount = (amount * float(coupon.discount_value)) / 100
                            if coupon.max_discount and discount > float(coupon.max_discount):
                                discount = float(coupon.max_discount)
                        else:
                            discount = float(coupon.discount_value)
                        discount = min(discount, amount)
                        
                        # Update coupon usage
                        coupon.used_count += 1
                        coupon.save()
                except Coupon.DoesNotExist:
                    pass
            
            final_amount = amount - discount
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                plan=plan,
                amount=final_amount,
                payment_method=payment_method,
                payment_status='pending',
                transaction_id=f'TXN{uuid.uuid4().hex[:10].upper()}',
            )
            
            # ***** Create plan history immediately *****
            from datetime import timedelta
            from django.utils import timezone
            
            validity_days = plan.validity
            if plan.validity_unit == 'months':
                validity_days = validity_days * 30
            elif plan.validity_unit == 'year':
                validity_days = validity_days * 365
            
            UserPlanHistory.objects.create(
                user=request.user,
                plan=plan,
                purchased_on=timezone.now(),
                activated_on=None,  # Will be set when payment is completed
                expires_on=timezone.now() + timedelta(days=validity_days) if validity_days else None,
                status='pending',  # Will be updated to 'active' when payment completes
                transaction_id=payment.transaction_id
            )
            
            # Create Razorpay order
            razorpay_order = None
            if payment_method in ['credit_card', 'debit_card', 'net_banking', 'upi', 'wallet']:
                try:
                    order_data = {
                        'amount': int(final_amount * 100),
                        'currency': 'INR',
                        'receipt': payment.bill_number,
                        'notes': {
                            'payment_id': str(payment.id),
                            'plan_id': str(plan.id),
                            'user_id': str(request.user.id),
                        }
                    }
                    razorpay_order = client.order.create(data=order_data)
                    
                    # Update payment with Razorpay order ID
                    payment.razorpay_order_id = razorpay_order['id']
                    payment.save()
                    
                except Exception as e:
                    logger.error(f"Razorpay order creation failed: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'error': 'Payment gateway error'
                    })
            
            return JsonResponse({
                'success': True,
                'payment_id': payment.id,
                'razorpay_order_id': razorpay_order['id'] if razorpay_order else None,
                'amount': final_amount,
                'bill_number': payment.bill_number,
            })
            
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def payment_history(request):
    """Show user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    
    # Apply filters
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if status:
        payments = payments.filter(payment_status=status)
    
    if start_date:
        payments = payments.filter(payment_date__date__gte=start_date)
    
    if end_date:
        payments = payments.filter(payment_date__date__lte=end_date)
    
    # Calculate statistics
    total_spent = payments.filter(payment_status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    successful_count = payments.filter(payment_status='completed').count()
    failed_count = payments.filter(payment_status='failed').count()
    pending_count = payments.filter(payment_status='pending').count()
    
    context = {
        'payments': payments,
        'total_spent': total_spent,
        'successful_count': successful_count,
        'failed_count': failed_count,
        'pending_count': pending_count,
    }
    
    return render(request, 'payments/history.html', context)

@login_required
def payment_detail(request, bill_number):
    """Show payment details"""
    payment = get_object_or_404(Payment, bill_number=bill_number, user=request.user)
    
    context = {
        'payment': payment
    }
    
    return render(request, 'payments/detail.html', context)