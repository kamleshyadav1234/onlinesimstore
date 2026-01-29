import uuid
from django import forms

from payments.models import Payment
from telecom.models import TelecomOperator
from .models import NewConnectionRequest, Plan, PlanComparison

class PlanFilterForm(forms.Form):
    operator = forms.ChoiceField(choices=[], required=False)
    category = forms.ChoiceField(choices=[], required=False)
    min_price = forms.DecimalField(required=False, decimal_places=2)
    max_price = forms.DecimalField(required=False, decimal_places=2)
    validity = forms.IntegerField(required=False, min_value=1)
    sort_by = forms.ChoiceField(choices=[
        ('price', 'Price: Low to High'),
        ('price_desc', 'Price: High to Low'),
        ('validity', 'Validity'),
        ('popularity', 'Popularity'),
    ], required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from telecom.models import TelecomOperator
        from .models import PlanCategory
        
        operator_choices = [('', 'All Operators')] + [
            (op.id, op.name) for op in TelecomOperator.objects.filter(is_active=True)
        ]
        category_choices = [('', 'All Categories')] + [
            (cat.id, cat.name) for cat in PlanCategory.objects.all()
        ]
        
        self.fields['operator'].choices = operator_choices
        self.fields['category'].choices = category_choices

class PlanComparisonForm(forms.ModelForm):
    class Meta:
        model = PlanComparison
        fields = ['plan1', 'plan2', 'comparison_points']
        widgets = {
            'comparison_points': forms.Textarea(attrs={'rows': 4}),
        }


# # plans/forms.py
# from django import forms
# from .models import Plan, PortRequest, NewConnectionRequest

# class PortNumberForm(forms.ModelForm):
#     """Form for porting existing number"""
#     class Meta:
#         model = PortRequest
#         fields = ['current_operator', 'new_operator', 'mobile_number', 
#                  'selected_plan', 'full_name', 'email', 'address', 
#                  'city', 'state', 'pincode']
#         widgets = {
#             'mobile_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': '98XXXXXX98',
#                 'pattern': '[6-9][0-9]{9}',
#                 'maxlength': '10'
#             }),
#             'current_operator': forms.Select(attrs={'class': 'form-control'}),
#             'new_operator': forms.Select(attrs={'class': 'form-control'}),
#             'selected_plan': forms.Select(attrs={'class': 'form-control'}),
#             'full_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'city': forms.TextInput(attrs={'class': 'form-control'}),
#             'state': forms.TextInput(attrs={'class': 'form-control'}),
#             'pincode': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '6'}),
#         }

# class NewConnectionForm(forms.ModelForm):
#     """Form for new mobile connection"""
#     class Meta:
#         model = NewConnectionRequest
#         fields = ['operator', 'selected_plan', 'number_preference',
#                  'full_name', 'email', 'mobile', 'address',
#                  'city', 'state', 'pincode', 'preferred_delivery_date',
#                  'preferred_delivery_time', 'delivery_address']
#         widgets = {
#             'operator': forms.Select(attrs={'class': 'form-control'}),
#             'selected_plan': forms.Select(attrs={'class': 'form-control'}),
#             'number_preference': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., 98XX98XX98 or VIP series'
#             }),
#             'full_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'mobile': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Alternate contact number'
#             }),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'city': forms.TextInput(attrs={'class': 'form-control'}),
#             'state': forms.TextInput(attrs={'class': 'form-control'}),
#             'pincode': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '6'}),
#             'preferred_delivery_date': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date',
#                 'min': 'today'
#             }),
#             'preferred_delivery_time': forms.Select(attrs={'class': 'form-control'}, choices=[
#                 ('09:00-12:00', '9 AM - 12 PM'),
#                 ('12:00-15:00', '12 PM - 3 PM'),
#                 ('15:00-18:00', '3 PM - 6 PM'),
#                 ('18:00-21:00', '6 PM - 9 PM'),
#             ]),
#             'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
#         }


# forms.py
from django import forms
from .models import PortRequest, Plan, TelecomOperator

# forms.py
class PortNumberForm(forms.ModelForm):
    """Form for porting existing number"""
    
    class Meta:
        model = PortRequest
        fields = [
            'mobile_number',
            'current_operator',
            'selected_plan',  # new_operator will be derived from this
            'full_name',
            'email',
            'address',
            'city',
            'state',
            'pincode',
        ]
        widgets = {
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control fancy-form-control',
                'placeholder': '98XXXXXX98',
                'pattern': '[6-9][0-9]{9}',
                'autocomplete': 'tel',
            }),
            'current_operator': forms.Select(attrs={
                'class': 'form-control fancy-form-control',
                'autocomplete': 'organization',
            }),
            'selected_plan': forms.HiddenInput(attrs={
                'id': 'selectedPlanId',
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control fancy-form-control',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control fancy-form-control',
                'autocomplete': 'email',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control fancy-form-control',
                'rows': 3,
                'autocomplete': 'street-address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control fancy-form-control',
                'autocomplete': 'address-level2',
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control fancy-form-control',
                'autocomplete': 'address-level1',
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control fancy-form-control',
                'maxlength': 6,
                'autocomplete': 'postal-code',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial querysets
        self.fields['current_operator'].queryset = TelecomOperator.objects.filter(is_active=True)
        self.fields['selected_plan'].queryset = Plan.objects.filter(
            plan_type='port_in', 
            is_active=True
        )

# forms.py
from django import forms
from django.utils import timezone
from .models import NewConnectionRequest, TelecomOperator, Plan

# forms.py
from django import forms
from django.utils import timezone
from .models import NewConnectionRequest, TelecomOperator, Plan

# class NewConnectionForm(forms.ModelForm):
#     # These are form fields that might not be in the model or need special handling
#     alternate_mobile = forms.CharField(
#         max_length=10,
#         required=True,
#         help_text="For delivery updates"
#     )
    
#     connection_type = forms.ChoiceField(
#         choices=[('prepaid', 'Prepaid'), ('postpaid', 'Postpaid')],
#         widget=forms.RadioSelect(),
#         initial='prepaid',
#         required=True
#     )
    
#     preferred_delivery_time = forms.ChoiceField(
#         choices=[
#             ('09:00-12:00', '9:00 AM - 12:00 PM'),
#             ('12:00-15:00', '12:00 PM - 3:00 PM'),
#             ('15:00-18:00', '3:00 PM - 6:00 PM'),
#             ('18:00-21:00', '6:00 PM - 9:00 PM'),
#         ],
#         required=True
#     )
    
#     class Meta:
#         model = NewConnectionRequest
#         fields = [
#             'full_name', 'email', 'alternate_mobile', 'date_of_birth',
#             'operator', 'selected_plan', 'connection_type', 'number_preference',
#             'address', 'city', 'state', 'pincode',
#             'preferred_delivery_date', 'preferred_delivery_time', 'delivery_address'
#         ]
#         widgets = {
#             'full_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'alternate_mobile': forms.TextInput(attrs={'class': 'form-control'}),
#             'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'operator': forms.Select(attrs={'class': 'form-control'}),
#             'selected_plan': forms.HiddenInput(),
#             'number_preference': forms.TextInput(attrs={'class': 'form-control'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'city': forms.TextInput(attrs={'class': 'form-control'}),
#             'state': forms.TextInput(attrs={'class': 'form-control'}),
#             'pincode': forms.TextInput(attrs={'class': 'form-control'}),
#             'preferred_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
#             'connection_type': forms.RadioSelect(),
#         }
    
#     def clean_alternate_mobile(self):
#         mobile = self.cleaned_data.get('alternate_mobile')
#         if mobile:
#             # Remove any non-digits
#             mobile = ''.join(filter(str.isdigit, mobile))
#             if len(mobile) != 10:
#                 raise forms.ValidationError("Please enter a valid 10-digit mobile number.")
#             if not mobile.startswith(('6', '7', '8', '9')):
#                 raise forms.ValidationError("Mobile number should start with 6, 7, 8, or 9.")
#         return mobile
    
#     def clean_pincode(self):
#         pincode = self.cleaned_data.get('pincode')
#         if pincode:
#             # Remove any non-digits
#             pincode = ''.join(filter(str.isdigit, pincode))
#             if len(pincode) != 6:
#                 raise forms.ValidationError("Please enter a valid 6-digit pincode.")
#         return pincode
    
#     def clean_preferred_delivery_date(self):
#         date = self.cleaned_data.get('preferred_delivery_date')
#         if date and date < timezone.now().date():
#             raise forms.ValidationError("Delivery date cannot be in the past.")
#         return date
    
#     def save(self, commit=True):
#         """Save the form, mapping alternate_mobile to mobile field"""
#         # Get the instance but don't save yet
#         instance = super().save(commit=False)
        
#         # Map alternate_mobile form field to mobile model field
#         if 'alternate_mobile' in self.cleaned_data:
#             instance.mobile = self.cleaned_data['alternate_mobile']
        
#         # Map connection_type if needed (if it's not a model field)
#         # If connection_type is not in the model, you might need to store it elsewhere
        
#         if commit:
#             instance.save()
#             self.save_m2m()  # Save many-to-many relationships if any
        
#         return instance



class NewConnectionForm(forms.ModelForm):
    # These are form fields that might not be in the model or need special handling
    alternate_mobile = forms.CharField(
        max_length=10,
        required=True,
        help_text="For delivery updates"
    )
    
    connection_type = forms.ChoiceField(
        choices=[('prepaid', 'Prepaid'), ('postpaid', 'Postpaid')],
        widget=forms.RadioSelect(),
        initial='prepaid',
        required=True
    )
    
    preferred_delivery_time = forms.ChoiceField(
        choices=[
            ('09:00-12:00', '9:00 AM - 12:00 PM'),
            ('12:00-15:00', '12:00 PM - 3:00 PM'),
            ('15:00-18:00', '3:00 PM - 6:00 PM'),
            ('18:00-21:00', '6:00 PM - 9:00 PM'),
        ],
        required=True
    )
    
    # Add payment method field
    payment_method = forms.ChoiceField(
        choices=[('online', 'Online Payment'), ('cod', 'Cash on Delivery')],
        widget=forms.RadioSelect,
        initial='online',
        required=True,
        label="Payment Method"
    )
    
    class Meta:
        model = NewConnectionRequest
        fields = [
            'full_name', 'email', 'alternate_mobile', 'date_of_birth',
            'operator', 'selected_plan', 'connection_type', 'number_preference',
            'address', 'city', 'state', 'pincode',
            'preferred_delivery_date', 'preferred_delivery_time', 'delivery_address',
            'payment_method'  # Add this
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'alternate_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'operator': forms.Select(attrs={'class': 'form-control'}),
            'selected_plan': forms.HiddenInput(),  # Important: This will be set from session
            'number_preference': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'connection_type': forms.RadioSelect(),
            'payment_method': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Get request object
        super().__init__(*args, **kwargs)
        
        # Set the selected_plan from session if available
        if self.request:
            plan_id = self.request.session.get('new_connection_plan_id')
            if plan_id:
                try:
                    plan = Plan.objects.get(id=plan_id)
                    self.fields['selected_plan'].initial = plan_id
                    # You can also set the plan amount for display
                    self.plan_amount = plan.price
                except Plan.DoesNotExist:
                    self.plan_amount = 0
            else:
                self.plan_amount = 0
    
    def clean_alternate_mobile(self):
        mobile = self.cleaned_data.get('alternate_mobile')
        if mobile:
            # Remove any non-digits
            mobile = ''.join(filter(str.isdigit, mobile))
            if len(mobile) != 10:
                raise forms.ValidationError("Please enter a valid 10-digit mobile number.")
            if not mobile.startswith(('6', '7', '8', '9')):
                raise forms.ValidationError("Mobile number should start with 6, 7, 8, or 9.")
        return mobile
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            # Remove any non-digits
            pincode = ''.join(filter(str.isdigit, pincode))
            if len(pincode) != 6:
                raise forms.ValidationError("Please enter a valid 6-digit pincode.")
        return pincode
    
    def clean_preferred_delivery_date(self):
        date = self.cleaned_data.get('preferred_delivery_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Delivery date cannot be in the past.")
        return date
    
    def clean(self):
        """Validate payment method and plan selection"""
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        selected_plan = cleaned_data.get('selected_plan')
        
        # Check if plan is selected
        if not selected_plan:
            raise forms.ValidationError("Please select a plan first.")
        
        # If online payment selected, check if payment is completed
        if payment_method == 'online' and self.request:
            payment_id = self.request.session.get('new_connection_payment_id')
            if not payment_id:
                raise forms.ValidationError("Please complete online payment first.")
            
            # Verify payment status
            try:
                payment = Payment.objects.get(id=payment_id, user=self.request.user)
                if payment.payment_status != 'completed':
                    raise forms.ValidationError("Please complete your online payment first.")
            except Payment.DoesNotExist:
                raise forms.ValidationError("Payment not found. Please complete payment first.")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the form, mapping alternate_mobile to mobile field and linking payment"""
        # Get the instance but don't save yet
        instance = super().save(commit=False)
        
        # Map alternate_mobile form field to mobile model field
        if 'alternate_mobile' in self.cleaned_data:
            instance.mobile = self.cleaned_data['alternate_mobile']
        
        # Set user from request
        if self.request:
            instance.user = self.request.user
        
        # Link payment if online payment was made
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method == 'online' and self.request:
            payment_id = self.request.session.get('new_connection_payment_id')
            if payment_id:
                try:
                    payment = Payment.objects.get(id=payment_id, user=self.request.user)
                    instance.payment = payment
                    
                    # Clear session after linking
                    if 'new_connection_payment_id' in self.request.session:
                        del self.request.session['new_connection_payment_id']
                    if 'new_connection_plan_id' in self.request.session:
                        del self.request.session['new_connection_plan_id']
                except Payment.DoesNotExist:
                    pass
        
        # For Cash on Delivery, create a pending payment record
        elif payment_method == 'cod' and self.request and instance.selected_plan:
            # Create COD payment record
            payment = Payment.objects.create(
                user=self.request.user,
                plan=instance.selected_plan,
                amount=float(instance.selected_plan.price),
                payment_method='cash',
                transaction_id=f'COD_{uuid.uuid4().hex[:10]}',
                payment_status='pending',
                purpose='new_connection_cod',
            )
            instance.payment = payment
        
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships if any
        
        return instance


# your_app/forms.py
from django import forms
from .models import SIMReplacementRequest
from django.core.validators import RegexValidator

class SIMReplacementForm(forms.ModelForm):
    # Custom validation for mobile numbers
    mobile_number = forms.CharField(
        max_length=10,
        min_length=10,
        validators=[RegexValidator(r'^[0-9]{10}$', 'Enter a valid 10-digit mobile number')],
        widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number'})
    )
    
    alternate_contact = forms.CharField(
        max_length=10,
        min_length=10,
        validators=[RegexValidator(r'^[0-9]{10}$', 'Enter a valid 10-digit mobile number')],
        widget=forms.TextInput(attrs={'placeholder': '10-digit alternate number'})
    )
    
    pincode = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r'^[0-9]{6}$', 'Enter a valid 6-digit pincode')],
        widget=forms.TextInput(attrs={'placeholder': '6-digit pincode'})
    )
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the terms and conditions'}
    )
    
    declaration_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the declaration'}
    )
    
    class Meta:
        model = SIMReplacementRequest
        fields = [
           'reason',
            'operator', 
            'mobile_number',
            'old_sim_type',
            'new_sim_type',
            'full_name',
            'email',
            'alternate_contact',
            'date_of_birth',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'pincode',
            'service_type',
        ]
        widgets = {
            'address_line1': forms.TextInput(attrs={'placeholder': 'House No, Building, Street'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Area, Locality'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        self.fields['reason'].required = True
        self.fields['operator'].required = True
        self.fields['mobile_number'].required = True
        self.fields['full_name'].required = True
        self.fields['email'].required = True
        self.fields['alternate_contact'].required = True
        self.fields['address_line1'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['pincode'].required = True

# forms.py
from django import forms

class DocumentUploadForm(forms.Form):
    id_proof = forms.FileField(
        label='ID Proof',
        required=True,
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png',
            'class': 'form-control'
        })
    )
    
    address_proof = forms.FileField(
        label='Address Proof',
        required=True,
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png',
            'class': 'form-control'
        })
    )
    
    declaration_form = forms.FileField(
        required=False,
        label='Self Declaration Form',
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png',
            'class': 'form-control'
        })
    )
    
    photo = forms.ImageField(
        required=False,
        label='Passport Photo',
        widget=forms.FileInput(attrs={
            'accept': '.jpg,.jpeg,.png',
            'class': 'form-control'
        })
    )

# your_app/forms.py (continued)
class DocumentUploadForm(forms.Form):
    id_proof = forms.FileField(
        label='ID Proof',
        help_text='Upload Aadhaar, PAN, Passport, Voter ID or Driving License (PDF/JPEG/PNG)',
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    
    address_proof = forms.FileField(
        label='Address Proof',
        help_text='Upload Aadhaar, Utility Bill, Passport or Bank Statement (PDF/JPEG/PNG)',
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    
    declaration_form = forms.FileField(
        required=False,
        label='Self Declaration Form',
        help_text='Download template, fill and upload (Optional)',
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    
    photo = forms.ImageField(
        required=False,
        label='Passport Size Photo',
        help_text='Recent passport size photo (Optional)',
        widget=forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png'})
    )



# class SIMReplacementForm(forms.ModelForm):
#     class Meta:
#         model = SIMReplacementRequest
#         fields = [
            
#         ]
    
#     terms_accepted = forms.BooleanField(required=True)
#     declaration_accepted = forms.BooleanField(required=True)