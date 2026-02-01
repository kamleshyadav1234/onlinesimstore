# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser

# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
import random
import string
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 10-digit mobile number'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) != 10:
                raise ValidationError('Please enter a valid 10-digit Indian mobile number')
            # Check if phone already exists
            if CustomUser.objects.filter(phone=phone).exists():
                raise ValidationError('This phone number is already registered')
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError('This email is already registered')
        return email
    
    def generate_agent_id(self):
        """Generate a unique agent ID for customer users"""
        while True:
            # Generate a random 8-character ID starting with 'CUST' for customers
            agent_id = f"CUST{''.join(random.choices(string.digits, k=4))}"
            if not CustomUser.objects.filter(agent_id=agent_id).exists():
                return agent_id
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.country = 'IN'  # Default to India
        user.user_type = 'customer'  # Default user type
        
        # Generate a unique agent_id for customers (even though they're not agents)
        if not user.agent_id:
            user.agent_id = self.generate_agent_id()
        
        if commit:
            user.save()
            # Set password properly
            user.set_password(self.cleaned_data["password1"])
            user.save()
        
        return user


class CustomUserChangeForm(UserChangeForm):
    # Remove password field
    password = None
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'alternate_phone',
            'date_of_birth', 'profile_picture', 'address', 'city', 'state',
            'pincode', 'country'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.NumberInput, forms.DateInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control-file'})


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})