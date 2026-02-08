import random
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
from plans.models import Plan, SIMReplacementRequest
import logging

logger = logging.getLogger(__name__)

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# payments/views.py

@login_required
def process_payment(request):
    """Show payment page for plan or SIM replacement or new connection"""
    plan_id = request.GET.get('plan_id')
    sim_replacement_id = request.GET.get('sim_replacement_id')
    new_connection = request.GET.get('new_connection')
    connection_request_id = request.GET.get('connection_request_id')
    coupon_code = request.GET.get('coupon')
    port_request_id = request.GET.get('port_request_id')  # ✅ NEW: Add port request ID

    
    context = {}
    payment_record = None
    
    if plan_id:
        # Handle plan payment
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        
        # ✅ CRITICAL: Check for existing pending payment for this plan
        existing_payment = Payment.objects.filter(
            user=request.user,
            plan=plan,
            payment_status__in=['pending', 'completed']
        ).order_by('-payment_date').first()
        
        if existing_payment:
            if existing_payment.payment_status == 'completed':
                messages.info(request, f'Plan already purchased! Bill: {existing_payment.bill_number}')
                return redirect('payment_success') + f'?payment_id={existing_payment.razorpay_payment_id}'
            
            payment_record = existing_payment
            print(f"✅ Using existing pending plan payment: {payment_record.bill_number}")
        else:
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
            
            # Create new payment record
            payment_record = Payment.objects.create(
                user=request.user,
                payment_type='plan',
                plan=plan,
                amount=final_amount,
                payment_method='razorpay',
                payment_status='pending',
                transaction_id=f'TXN{uuid.uuid4().hex[:10].upper()}',
            )
            print(f"✅ Created new plan payment: {payment_record.bill_number}")
        
        context.update({
            'payment_type': 'plan',
            'plan': plan,
            'amount': float(plan.price),
            'discount': 0,
            'final_amount': float(plan.price),
            'coupon': None,
            'payment_record': payment_record,
        })
    elif port_request_id:
        # ✅ NEW: Handle port request payment
        from plans.models import PortRequest
        
        port_request = get_object_or_404(
            PortRequest,
            id=port_request_id,
            user=request.user
        )
        
        # Get the plan for port request
        plan = port_request.selected_plan
        if not plan:
            messages.error(request, 'No plan selected for port request')
            return redirect('port_number')
        
        final_amount = float(plan.price)
        
        # ✅ CRITICAL: Check for existing payment
        existing_payments = Payment.objects.filter(
            port_request=port_request,
            user=request.user
        ).order_by('-payment_date')
        
        if existing_payments.exists():
            # Check if there's a completed payment
            completed_payment = existing_payments.filter(payment_status='completed').first()
            if completed_payment:
                messages.info(request, f'Port request payment already completed! Bill: {completed_payment.bill_number}')
                return redirect('payment_success') + f'?payment_id={completed_payment.razorpay_payment_id}'
            
            # Use the most recent pending payment
            pending_payment = existing_payments.filter(payment_status='pending').first()
            if pending_payment:
                payment_record = pending_payment
                print(f"✅ Using existing pending port request payment: {payment_record.bill_number}")
            else:
                # Use the most recent payment regardless of status
                payment_record = existing_payments.first()
                print(f"✅ Using existing port request payment: {payment_record.bill_number} - Status: {payment_record.payment_status}")
        else:
            # Create new payment record only if none exists
            payment_record = Payment.objects.create(
                user=request.user,
                payment_type='port_request',
                port_request=port_request,
                plan=plan,
                amount=final_amount,
                payment_method='razorpay',
                payment_status='pending',
                transaction_id=f'PORT{uuid.uuid4().hex[:10].upper()}',
            )
            print(f"✅ Created new port request payment: {payment_record.bill_number}")
        
        context.update({
            'payment_type': 'port_request',
            'port_request': port_request,
            'plan': plan,
            'amount': final_amount,
            'final_amount': final_amount,
            'payment_record': payment_record,
        })
        
   
    elif sim_replacement_id:
        # Handle SIM replacement payment
        sim_request = get_object_or_404(
            SIMReplacementRequest, 
            id=sim_replacement_id, 
            user=request.user
        )
        
        # For SIM replacement, amount is fixed based on service type
        final_amount = float(sim_request.amount_paid)
        
        # ✅ CRITICAL: Check for existing payment
        existing_payment = Payment.objects.filter(
            sim_replacement=sim_request,
            user=request.user,
            payment_status__in=['pending', 'completed']
        ).order_by('-payment_date').first()
        
        if existing_payment:
            if existing_payment.payment_status == 'completed':
                messages.info(request, f'SIM replacement payment already completed! Bill: {existing_payment.bill_number}')
                return redirect('payment_success') + f'?payment_id={existing_payment.razorpay_payment_id}'
            
            payment_record = existing_payment
            print(f"✅ Using existing SIM replacement payment: {payment_record.bill_number}")
        else:
            # Create new payment record
            payment_record = Payment.objects.create(
                user=request.user,
                payment_type='sim_replacement',
                sim_replacement=sim_request,
                amount=final_amount,
                payment_method='razorpay',
                payment_status='pending',
                transaction_id=f'SIM{uuid.uuid4().hex[:10].upper()}',
            )
            print(f"✅ Created new SIM replacement payment: {payment_record.bill_number}")
        
        context.update({
            'payment_type': 'sim_replacement',
            'sim_request': sim_request,
            'amount': final_amount,
            'final_amount': final_amount,
            'payment_record': payment_record,
        })
        
    elif new_connection == 'true' and connection_request_id:
        # Handle new connection payment
        from plans.models import NewConnectionRequest
        
        new_conn_request = get_object_or_404(
            NewConnectionRequest,
            id=connection_request_id,
            user=request.user
        )
        
        # Get the plan for new connection
        plan = new_conn_request.selected_plan
        if not plan:
            messages.error(request, 'No plan selected for new connection')
            return redirect('new_connection')
        
        final_amount = float(plan.price)
        
        # ✅ CRITICAL: Check for ANY existing payment (pending OR completed)
        existing_payments = Payment.objects.filter(
            new_connection=new_conn_request,
            user=request.user
        ).order_by('-payment_date')
        
        if existing_payments.exists():
            # Check if there's a completed payment
            completed_payment = existing_payments.filter(payment_status='completed').first()
            if completed_payment:
                messages.info(request, f'New connection payment already completed! Bill: {completed_payment.bill_number}')
                return redirect('payment_success') + f'?payment_id={completed_payment.razorpay_payment_id}'
            
            # Use the most recent pending payment
            pending_payment = existing_payments.filter(payment_status='pending').first()
            if pending_payment:
                payment_record = pending_payment
                print(f"✅ Using existing pending new connection payment: {payment_record.bill_number}")
            else:
                # Use the most recent payment regardless of status
                payment_record = existing_payments.first()
                print(f"✅ Using existing new connection payment: {payment_record.bill_number} - Status: {payment_record.payment_status}")
        else:
            # Create new payment record only if none exists
            payment_record = Payment.objects.create(
                user=request.user,
                payment_type='new_connection',
                new_connection=new_conn_request,
                plan=plan,
                amount=final_amount,
                payment_method='razorpay',
                payment_status='pending',
                transaction_id=f'NEW{uuid.uuid4().hex[:10].upper()}',
            )
            print(f"✅ Created new connection payment: {payment_record.bill_number}")
        
        context.update({
            'payment_type': 'new_connection',
            'new_connection_request': new_conn_request,
            'plan': plan,
            'amount': final_amount,
            'final_amount': final_amount,
            'payment_record': payment_record,
        })
        
    else:
        messages.error(request, 'Invalid payment request.')
        return redirect('dashboard')
    
    # ✅ CRITICAL: Validate we have a payment record
    if not payment_record:
        messages.error(request, 'Failed to create or retrieve payment record.')
        return redirect('dashboard')
    
    # Create Razorpay order for all payment types
    razorpay_order = None
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        try:
            # Use existing payment record's transaction ID
            receipt_id = payment_record.transaction_id
            
            order_data = {
                'amount': int(payment_record.amount * 100),  
                'currency': 'INR',
                'receipt': receipt_id,
                'notes': {
                    'payment_type': context.get('payment_type'),
                    'user_id': str(request.user.id),
                    'payment_id': str(payment_record.id),
                }
            }
            
            # Add specific item ID based on payment type
            if context['payment_type'] == 'plan':
                order_data['notes']['plan_id'] = str(plan.id)
            elif context['payment_type'] == 'sim_replacement':
                order_data['notes']['sim_replacement_id'] = str(sim_request.id)
            elif context['payment_type'] == 'new_connection':
                order_data['notes']['new_connection_id'] = str(new_conn_request.id)
                order_data['notes']['plan_id'] = str(plan.id)
            elif context['payment_type'] == 'port_request':  # ✅ ADD THIS
                order_data['notes']['port_request_id'] = str(port_request.id)
                order_data['notes']['plan_id'] = str(plan.id)

            
            # ✅ CRITICAL: Check if we already have a Razorpay order for this payment
            if payment_record.razorpay_order_id:
                try:
                    # Try to fetch existing order
                    existing_order = client.order.fetch(payment_record.razorpay_order_id)
                    razorpay_order = existing_order
                    print(f"✅ Using existing Razorpay order: {payment_record.razorpay_order_id}")
                except Exception as e:
                    print(f"⚠️ Existing Razorpay order not found ({e}), creating new one")
                    razorpay_order = client.order.create(data=order_data)
                    payment_record.razorpay_order_id = razorpay_order['id']
                    payment_record.save()
                    print(f"✅ Created new Razorpay order: {razorpay_order['id']}")
            else:
                # Create new Razorpay order
                razorpay_order = client.order.create(data=order_data)
                payment_record.razorpay_order_id = razorpay_order['id']
                payment_record.save()
                print(f"✅ Created Razorpay order: {razorpay_order['id']}")
            
            # Store in session
            request.session['current_payment_id'] = payment_record.id
            
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            messages.warning(request, 'Payment gateway is currently unavailable. Please try again later.')
    
    context.update({
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'payment_record': payment_record,
    })
    
    return render(request, 'payments/process_payment.html', context)


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
                payment_id = payment_data.get('id')
                order_id = payment_data.get('order_id')
                
                print(f"✅ Webhook: Payment captured - {payment_id}, Order: {order_id}")
                
                # Try to find payment by razorpay_payment_id first
                try:
                    payment = Payment.objects.get(razorpay_payment_id=payment_id)
                except Payment.DoesNotExist:
                    # Try by razorpay_order_id
                    try:
                        payment = Payment.objects.get(razorpay_order_id=order_id)
                    except Payment.DoesNotExist:
                        logger.error(f"Payment not found: payment_id={payment_id}, order_id={order_id}")
                        return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)
                
                # Update payment status
                payment.payment_status = 'completed'
                payment.razorpay_payment_id = payment_id
                
                # Save payment method if available
                if payment_data.get('method'):
                    payment.payment_method = payment_data.get('method')
                
                payment.save()
                
                logger.info(f"✅ Payment completed via webhook: {payment.bill_number}")
                
                # ✅ CRITICAL: Mark any duplicate pending payments as failed
                if payment.payment_type == 'new_connection' and payment.new_connection:
                    duplicate_payments = Payment.objects.filter(
                        new_connection=payment.new_connection,
                        user=payment.user,
                        payment_status='pending'
                    ).exclude(id=payment.id)
                    
                    for dup_payment in duplicate_payments:
                        dup_payment.payment_status = 'failed'
                        dup_payment.notes = f"Duplicate - superseded by payment {payment.bill_number}"
                        dup_payment.save()
                        logger.info(f"✅ Marked duplicate payment as failed: {dup_payment.bill_number}")
                
                # Activate plan if applicable
                if payment.plan and payment.user:
                    from datetime import timedelta
                    from django.utils import timezone
                    
                    validity_days = payment.plan.validity
                    
                    if payment.plan.validity_unit == 'months':
                        validity_days = validity_days * 30
                    elif payment.plan.validity_unit == 'year':
                        validity_days = validity_days * 365
                    
                    # Create plan history
                    UserPlanHistory.objects.create(
                        user=payment.user,
                        plan=payment.plan,
                        purchased_on=payment.payment_date,
                        activated_on=timezone.now(),
                        expires_on=timezone.now() + timedelta(days=validity_days),
                        status='active',
                        transaction_id=payment.transaction_id
                    )
                    
                    logger.info(f"✅ Plan activated via webhook: {payment.plan.name} for user {payment.user.email}")
            
            elif event == 'payment.failed':
                payment_data = data.get('payload', {}).get('payment', {}).get('entity', {})
                payment_id = payment_data.get('id')
                order_id = payment_data.get('order_id')
                
                print(f"❌ Webhook: Payment failed - {payment_id}, Order: {order_id}")
                
                # Try to find and update payment
                try:
                    payment = Payment.objects.get(razorpay_payment_id=payment_id)
                except Payment.DoesNotExist:
                    try:
                        payment = Payment.objects.get(razorpay_order_id=order_id)
                    except Payment.DoesNotExist:
                        logger.error(f"Payment not found for failed payment: payment_id={payment_id}, order_id={order_id}")
                        return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)
                
                payment.payment_status = 'failed'
                payment.save()
                
                logger.info(f"❌ Payment failed via webhook: {payment.bill_number}")
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

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



@login_required
def payment_success(request):
    """Show payment success page"""
    payment_id = request.GET.get('payment_id')  # Razorpay payment ID (e.g., "pay_S9OHc8lbjEOoBR")
    order_id = request.GET.get('order_id')      # Razorpay order ID (e.g., "order_S9OGSLzwxUHKWc")
    
    payment = None
    
    # Try to find payment by different identifiers
    if payment_id:
        try:
            payment = Payment.objects.get(razorpay_payment_id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            try:
                payment = Payment.objects.get(transaction_id=payment_id, user=request.user)
            except Payment.DoesNotExist:
                pass
    
    if not payment and order_id:
        try:
            payment = Payment.objects.get(razorpay_order_id=order_id, user=request.user)
        except Payment.DoesNotExist:
            pass
    
    # If payment is still None, check session for current payment
    if not payment:
        current_payment_id = request.session.get('current_payment_id')
        if current_payment_id:
            try:
                payment = Payment.objects.get(id=current_payment_id, user=request.user)
            except Payment.DoesNotExist:
                pass
    
    # If still not found, get the latest payment for this user
    if not payment:
        try:
            payment = Payment.objects.filter(user=request.user).latest('payment_date')
        except Payment.DoesNotExist:
            messages.info(request, 'No payment found. Please check your payment history.')
            return redirect('payment_history')
        
    if payment.port_request:
        # Mark any other pending payments for the same port request as failed
        duplicate_payments = Payment.objects.filter(
            port_request=payment.port_request,
            user=request.user,
            payment_status='pending'
        ).exclude(id=payment.id)
        
        if duplicate_payments.exists():
            for dup_payment in duplicate_payments:
                dup_payment.payment_status = 'failed'
                dup_payment.notes = f"Duplicate - superseded by payment {payment.bill_number}"
                dup_payment.save()
                print(f"✅ Marked duplicate payment as failed: {dup_payment.bill_number}")
        
        # Update port request status
        port_request = payment.port_request
        port_request.status = 'payment_completed'
        port_request.save()
        
        # Create plan history for port request
        if payment.plan and not UserPlanHistory.objects.filter(
            user=request.user,
            plan=payment.plan,
            transaction_id=payment.transaction_id
        ).exists():
            from datetime import timedelta
            from django.utils import timezone
            
            validity_days = payment.plan.validity
            
            if payment.plan.validity_unit == 'months':
                validity_days = validity_days * 30
            elif payment.plan.validity_unit == 'year':
                validity_days = validity_days * 365
            
            UserPlanHistory.objects.create(
                user=request.user,
                plan=payment.plan,
                purchased_on=payment.payment_date,
                activated_on=timezone.now(),
                expires_on=timezone.now() + timedelta(days=validity_days),
                status='active',
                transaction_id=payment.transaction_id,
                port_request=port_request  # Link to port request
            )
    
    # ✅ CRITICAL: Clean up duplicate payments if this is a new connection payment
    if payment.new_connection:
        # Mark any other pending payments for the same connection as failed
        duplicate_payments = Payment.objects.filter(
            new_connection=payment.new_connection,
            user=request.user,
            payment_status='pending'
        ).exclude(id=payment.id)
        
        if duplicate_payments.exists():
            for dup_payment in duplicate_payments:
                dup_payment.payment_status = 'failed'
                dup_payment.notes = f"Duplicate - superseded by payment {payment.bill_number}"
                dup_payment.save()
                print(f"✅ Marked duplicate payment as failed: {dup_payment.bill_number}")
    
    # Now we have the payment, update status to completed if pending
    if payment.payment_status == 'pending':
        payment.payment_status = 'completed'
        
        # Make sure Razorpay IDs are saved
        if payment_id and not payment.razorpay_payment_id:
            payment.razorpay_payment_id = payment_id
        if order_id and not payment.razorpay_order_id:
            payment.razorpay_order_id = order_id
        
        payment.save()
        print(f"✅ Updated payment status to completed: {payment.bill_number}")
    
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
    
    # Clear session payment ID
    if 'current_payment_id' in request.session:
        del request.session['current_payment_id']
    
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




# payments/views.py
@csrf_exempt
@login_required
def create_payment(request):
    """Create Razorpay order for existing payment record"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method')
            plan_id = data.get('plan_id')
            sim_replacement_id = data.get('sim_replacement_id')
            new_connection_id = data.get('new_connection_id')
            coupon_code = data.get('coupon_code')
            payment_id = data.get('payment_id')  # ✅ Get existing payment ID
            
            # ✅ CRITICAL: Use existing payment ID if provided
            if payment_id:
                try:
                    payment = Payment.objects.get(
                        id=payment_id,
                        user=request.user,
                        payment_status='pending'
                    )
                    print(f"✅ Using existing payment: {payment.bill_number}")
                except Payment.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Payment not found or already processed'
                    })
            
            # If no payment_id provided, check for existing pending payments
            elif plan_id:
                # Check for existing pending plan payment
                existing_payment = Payment.objects.filter(
                    user=request.user,
                    plan_id=plan_id,
                    payment_status='pending'
                ).first()
                
                if existing_payment:
                    payment = existing_payment
                    print(f"✅ Using existing pending plan payment: {payment.bill_number}")
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'No pending payment found. Please restart payment process.'
                    })
            
            elif sim_replacement_id:
                # Check for existing pending SIM replacement payment
                existing_payment = Payment.objects.filter(
                    user=request.user,
                    sim_replacement_id=sim_replacement_id,
                    payment_status='pending'
                ).first()
                
                if existing_payment:
                    payment = existing_payment
                    print(f"✅ Using existing pending SIM replacement payment: {payment.bill_number}")
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'No pending payment found. Please restart payment process.'
                    })
            
            elif new_connection_id:
                # Check for existing pending new connection payment
                existing_payment = Payment.objects.filter(
                    user=request.user,
                    new_connection_id=new_connection_id,
                    payment_status='pending'
                ).first()
                
                if existing_payment:
                    payment = existing_payment
                    print(f"✅ Using existing pending new connection payment: {payment.bill_number}")
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'No pending payment found. Please restart payment process.'
                    })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid request parameters'
                })
            
            # ✅ IMPORTANT: Save payment method if changed
            if payment_method and payment_method != payment.payment_method:
                payment.payment_method = payment_method
                payment.save()
            
            # Create Razorpay order for the EXISTING payment
            if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                
                # Check if we already have a Razorpay order
                if payment.razorpay_order_id:
                    try:
                        existing_order = client.order.fetch(payment.razorpay_order_id)
                        razorpay_order = existing_order
                        print(f"✅ Using existing Razorpay order: {payment.razorpay_order_id}")
                    except Exception as e:
                        print(f"⚠️ Existing Razorpay order not found ({e}), creating new one")
                        # Create new order
                        order_data = {
                            'amount': int(payment.amount * 100),
                            'currency': 'INR',
                            'receipt': payment.transaction_id,
                            'notes': {
                                'payment_id': str(payment.id),
                                'user_id': str(request.user.id),
                            }
                        }
                        
                        razorpay_order = client.order.create(data=order_data)
                        payment.razorpay_order_id = razorpay_order['id']
                        payment.save()
                        print(f"✅ Created new Razorpay order: {razorpay_order['id']}")
                else:
                    # Create new order
                    order_data = {
                        'amount': int(payment.amount * 100),
                        'currency': 'INR',
                        'receipt': payment.transaction_id,
                        'notes': {
                            'payment_id': str(payment.id),
                            'user_id': str(request.user.id),
                        }
                    }
                    
                    razorpay_order = client.order.create(data=order_data)
                    payment.razorpay_order_id = razorpay_order['id']
                    payment.save()
                    print(f"✅ Created Razorpay order: {razorpay_order['id']}")
                
                return JsonResponse({
                    'success': True,
                    'razorpay_order_id': razorpay_order['id'],
                    'amount': payment.amount,
                    'payment_id': payment.id,
                })
            
            else:
                return JsonResponse({
                    'success': True,
                    'payment_id': payment.id,
                    'razorpay_order_id': None,
                })
            
        except Exception as e:
            print(f"❌ Error in create_payment: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def create_plan_payment(request, plan_id, payment_method, existing_payment, data):
    """Create payment for plan purchase"""
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    coupon_code = data.get('coupon_code')
    
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
    
    if not existing_payment:
        # Create new payment record
        payment = Payment.objects.create(
            user=request.user,
            plan=plan,
            amount=final_amount,
            payment_method=payment_method,
            payment_status='pending',
            transaction_id=f'TXN{uuid.uuid4().hex[:10].upper()}',
        )
    else:
        payment = existing_payment
        payment.amount = final_amount
        payment.payment_method = payment_method
        payment.save()
    
    return process_razorpay_payment(request, payment, 'plan')


def create_sim_replacement_payment(request, sim_replacement_id, payment_method, existing_payment, data):
    """Create payment for SIM replacement"""
    sim_request = get_object_or_404(
        SIMReplacementRequest, 
        id=sim_replacement_id, 
        user=request.user
    )
    
    final_amount = float(sim_request.amount_paid)
    
    if not existing_payment:
        # Create new payment record
        payment = Payment.objects.create(
            user=request.user,
            sim_replacement=sim_request,
            amount=final_amount,
            payment_method=payment_method,
            payment_status='pending',
            transaction_id=f'SIM{uuid.uuid4().hex[:10].upper()}',
        )
    else:
        payment = existing_payment
        payment.amount = final_amount
        payment.payment_method = payment_method
        payment.save()
    
    return process_razorpay_payment(request, payment, 'sim_replacement')


def process_existing_payment(request, payment, payment_method):
    """Process an existing payment record"""
    payment.payment_method = payment_method
    payment.save()
    
    payment_type = 'plan' if payment.plan else 'sim_replacement' if payment.sim_replacement else 'unknown'
    
    return process_razorpay_payment(request, payment, payment_type)


def process_razorpay_payment(request, payment, payment_type):
    """Create Razorpay order for payment"""
    razorpay_order = None
    
    try:
        order_data = {
            'amount': int(float(payment.amount) * 100),
            'currency': 'INR',
            'receipt': payment.transaction_id,
            'notes': {
                'payment_id': str(payment.id),
                'payment_type': payment_type,
                'user_id': str(request.user.id),
            }
        }
        
        if payment.plan:
            order_data['notes']['plan_id'] = str(payment.plan.id)
        elif payment.sim_replacement:
            order_data['notes']['sim_replacement_id'] = str(payment.sim_replacement.id)
        
        razorpay_order = client.order.create(data=order_data)
        
        # Update payment with Razorpay order ID
        payment.razorpay_order_id = razorpay_order['id']
        payment.save()
        
        return JsonResponse({
            'success': True,
            'payment_id': payment.id,
            'razorpay_order_id': razorpay_order['id'],
            'amount': float(payment.amount),
            'transaction_id': payment.transaction_id,
        })
        
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        
        # Return success even without Razorpay for COD
        if payment.payment_method == 'cash':
            return JsonResponse({
                'success': True,
                'payment_id': payment.id,
                'razorpay_order_id': None,
                'amount': float(payment.amount),
                'transaction_id': payment.transaction_id,
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Payment gateway error: ' + str(e)
        })

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