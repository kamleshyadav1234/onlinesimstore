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
    
    # Agent specific fields
    agent_id = models.CharField(max_length=20, blank=True, unique=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

class UserPlanHistory(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    plan = models.ForeignKey('plans.Plan', on_delete=models.SET_NULL, null=True)
    purchased_on = models.DateTimeField(auto_now_add=True)
    activated_on = models.DateTimeField(null=True, blank=True)
    expires_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-purchased_on']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"
    
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