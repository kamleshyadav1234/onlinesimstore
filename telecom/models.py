from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class TelecomOperator(models.Model):
    OPERATOR_TYPES = [
        ('mobile', 'Mobile Network'),
        ('broadband', 'Broadband'),
        ('dth', 'DTH'),
        ('landline', 'Landline'),
    ]
    
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='operator_logos/')
    operator_type = models.CharField(max_length=20, choices=OPERATOR_TYPES)
    description = models.TextField()
    website = models.URLField()
    customer_care = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


from django.utils import timezone
from django.db import models
from django.db import models
from django.utils import timezone

class ServiceArea(models.Model):
    STATE_CHOICES = [
        ('MH', 'Maharashtra'),
        ('DL', 'Delhi'),
        ('KA', 'Karnataka'),
        ('TN', 'Tamil Nadu'),
        ('UP', 'Uttar Pradesh'),
        ('GJ', 'Gujarat'),
        ('RJ', 'Rajasthan'),
        ('WB', 'West Bengal'),
        ('AP', 'Andhra Pradesh'),
        ('TS', 'Telangana'),
        ('KL', 'Kerala'),
        ('PB', 'Punjab'),
        ('HR', 'Haryana'),
        ('MP', 'Madhya Pradesh'),
        ('BR', 'Bihar'),
        ('OR', 'Odisha'),
        ('AS', 'Assam'),
    ]
    
    operator = models.ForeignKey(TelecomOperator, on_delete=models.CASCADE, related_name='service_areas')
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    city = models.CharField(max_length=100)
    pincodes = models.TextField(help_text="Comma separated pincodes (e.g., 400001,400002,400003)")
    availability = models.BooleanField(default=True)
    
    # CORRECT: Use either auto_now_add OR default, not both
    created_at = models.DateTimeField(auto_now_add=True)  # Remove 'default' parameter
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Service Area'
        verbose_name_plural = 'Service Areas'
        ordering = ['state', 'city']
    
    def __str__(self):
        return f"{self.operator.name} - {self.get_state_display()}, {self.city}"
    
    def get_pincode_list(self):
        """Return list of pincodes"""
        return [p.strip() for p in self.pincodes.split(',') if p.strip()]