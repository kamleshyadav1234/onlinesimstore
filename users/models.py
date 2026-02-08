from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from datetime import date

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
    phone = models.CharField(max_length=15, unique=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    country = CountryField(blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    kyc_completed = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.phone} - {self.get_user_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f'user_{self.phone}'
        
        if self.user_type == 'agent' and not self.agent_id:
            import uuid
            self.agent_id = f'AGT{str(uuid.uuid4().int)[:8].upper()}'
        
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}".strip()
            return self.first_name.strip()
        return self.phone
    
    @property
    def short_phone(self):
        if len(self.phone) > 6:
            return f"{self.phone[:3]}****{self.phone[-3:]}"
        return self.phone


class UserPlanHistory(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    plan = models.ForeignKey('plans.Plan', on_delete=models.SET_NULL, null=True)
    purchased_on = models.DateTimeField(auto_now_add=True)
    activated_on = models.DateTimeField(null=True, blank=True)
    expires_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True)  # Make it blank=True

    class Meta:
        ordering = ['-purchased_on']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"
    

    def save(self, *args, **kwargs):
        # Set default values if not provided
        if not self.transaction_id:
            import uuid
            self.transaction_id = f"TXN{uuid.uuid4().hex[:10].upper()}"
        if not self.gateway_transaction_id and hasattr(self, 'payment'):
            self.gateway_transaction_id = self.payment.transaction_id
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        if not self.expires_on:
            return False
        return self.status == 'active' and date.today() <= self.expires_on.date()
    
    @property
    def days_remaining(self):
        if not self.expires_on:
            return None
        today = date.today()
        expires_date = self.expires_on.date()
        return (expires_date - today).days
    
    @property
    def is_expired(self):
        if self.days_remaining is None:
            return False
        return self.days_remaining < 0

class UserFavouritePlan(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    plan = models.ForeignKey('plans.Plan', on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'plan']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"



from django.utils import timezone
from datetime import timedelta
import random
import string

class OTP(models.Model):
    OTP_TYPES = [
        ('login', 'Login'),
        ('signup', 'Signup'),
        ('password_reset', 'Password Reset'),
        ('phone_verification', 'Phone Verification'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES, default='login')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        index_together = ['phone', 'otp_type', 'is_used']
    
    def __str__(self):
        return f"{self.phone} - {self.otp} - {self.otp_type}"
    
    @classmethod
    def generate_otp(cls, length=6):
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    @classmethod
    def create_otp(cls, phone, otp_type='login', user=None):
        """Create a new OTP entry"""
        # Deactivate any existing OTPs for this phone and type
        cls.objects.filter(
            phone=phone, 
            otp_type=otp_type, 
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        # Generate new OTP
        otp = cls.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        
        return cls.objects.create(
            user=user,
            phone=phone,
            otp=otp,
            otp_type=otp_type,
            expires_at=expires_at,
            is_used=False
        )
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save()
    
    @classmethod
    def verify_otp(cls, phone, otp, otp_type='login'):
        """Verify OTP"""
        try:
            otp_obj = cls.objects.get(
                phone=phone,
                otp=otp,
                otp_type=otp_type,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            otp_obj.mark_as_used()
            return True, otp_obj
        except cls.DoesNotExist:
            return False, None