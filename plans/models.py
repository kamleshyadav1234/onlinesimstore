from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from telecom.models import TelecomOperator
from telecompedia import settings
from users.models import CustomUser

class PlanCategory(models.Model):
    CATEGORY_TYPES = [
        ('prepaid', 'Prepaid'),
        ('postpaid', 'Postpaid'),
        ('data', 'Data Pack'),
        ('roaming', 'Roaming'),
        ('international', 'International'),
        ('special', 'Special Offers'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField()
    
    def __str__(self):
        return self.name

# plans/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# Update Plan model to be generic
class Plan(models.Model):
    VALIDITY_UNITS = [
        ('days', 'Days'),
        ('months', 'Months'),
        ('year', 'Year'),
    ]
    
    PLAN_TYPE_CHOICES = [
        ('general', 'General Plan'),
        ('new_connection', 'New Connection Plan'),
        ('port_in', 'Port-in (MNP) Plan'),
    ]
    
    operator = models.ForeignKey(TelecomOperator, on_delete=models.CASCADE)
    category = models.ForeignKey(PlanCategory, on_delete=models.SET_NULL, null=True)
    
    # Plan Type - THIS IS THE KEY FIELD
    plan_type = models.CharField(
        max_length=20, 
        choices=PLAN_TYPE_CHOICES, 
        default='general',
        help_text="Is this for new connection or port-in?"
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    validity = models.PositiveIntegerField()
    validity_unit = models.CharField(max_length=10, choices=VALIDITY_UNITS, default='days')
    
    # Special benefits based on plan type
    port_in_bonus = models.CharField(max_length=200, blank=True, 
                                    help_text="Special bonus for port-in customers")
    new_connection_bonus = models.CharField(max_length=200, blank=True,
                                          help_text="Welcome bonus for new connections")
    
    # Plan Features
    data_allowance = models.CharField(max_length=100, blank=True)
    voice_calls = models.CharField(max_length=100, blank=True)
    sms = models.CharField(max_length=100, blank=True)
    ott_benefits = models.TextField(blank=True)
    other_benefits = models.TextField(blank=True)
    
    # Plan Details
    is_popular = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.operator.name} - {self.name} ({self.get_plan_type_display()})"
    
    def get_full_validity(self):
        return f"{self.validity} {self.get_validity_unit_display()}"
    
    # Helper methods
    @property
    def is_new_connection_plan(self):
        return self.plan_type == 'new_connection'
    
    @property
    def is_port_in_plan(self):
        return self.plan_type == 'port_in'
    
    @property
    def get_special_bonus(self):
        if self.plan_type == 'new_connection':
            return self.new_connection_bonus
        elif self.plan_type == 'port_in':
            return self.port_in_bonus
        return ""

# NEW: Port Request Model for MNP
class PortRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('upc_sent', 'UPC Sent'),
        ('documents_uploaded', 'Documents Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Ported Successfully'),
        ('failed', 'Porting Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='port_requests')
    current_operator = models.ForeignKey(TelecomOperator, on_delete=models.PROTECT, 
                                       related_name='current_port_requests')
    new_operator = models.ForeignKey(TelecomOperator, on_delete=models.PROTECT, 
                                   related_name='new_port_requests')
    mobile_number = models.CharField(max_length=10)
    selected_plan = models.ForeignKey(Plan, on_delete=models.PROTECT, 
                                    limit_choices_to={'plan_type': 'port_in', 'is_active': True})
    
    # Porting Details
    upc_code = models.CharField(max_length=15, blank=True, verbose_name="Unique Porting Code")
    upc_expiry = models.DateTimeField(null=True, blank=True)
    porting_date = models.DateField(null=True, blank=True)
    
    # Personal Details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    
    # Documents
    aadhaar_card = models.FileField(upload_to='porting/aadhaar/', blank=True)
    address_proof = models.FileField(upload_to='porting/address/', blank=True)
    current_sim_photo = models.FileField(upload_to='porting/sim/', blank=True, 
                                       help_text="Photo of current SIM card")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tracking_id = models.CharField(max_length=20, unique=True, editable=False)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"MNP-{self.tracking_id} - {self.mobile_number}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            date_str = timezone.now().strftime('%y%m%d')
            last_id = PortRequest.objects.filter(
                tracking_id__startswith=f"MNP{date_str}"
            ).count() + 1
            self.tracking_id = f"MNP{date_str}{str(last_id).zfill(4)}"
        super().save(*args, **kwargs)
    
    @property
    def can_generate_upc(self):
        """Check if UPC can be generated"""
        return self.status == 'pending'
    
    @property
    def is_active(self):
        """Check if port request is still active"""
        active_statuses = ['draft', 'pending', 'upc_sent', 'documents_uploaded', 'processing']
        return self.status in active_statuses

# NEW: New Connection Request Model
class NewConnectionRequest(models.Model):

    CONNECTION_TYPE_CHOICES = [
        ('prepaid', 'Prepaid'),
        ('postpaid', 'Postpaid'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('document_verification', 'Document Verification'),
        ('sim_dispatch', 'SIM Dispatch'),
        ('sim_delivered', 'SIM Delivered'),
        ('activated', 'Activated'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='new_connection_requests')
 
    operator = models.ForeignKey(TelecomOperator, on_delete=models.PROTECT)
    selected_plan = models.ForeignKey(Plan, on_delete=models.PROTECT,
                                    limit_choices_to={'plan_type': 'new_connection', 'is_active': True})
    
    date_of_birth = models.DateField(null=True, blank=True)  # ADD THIS LINE

    

    connection_type = models.CharField(  # ADD THIS SECTION
        max_length=20,
        choices=CONNECTION_TYPE_CHOICES,
        default='prepaid'
    )
    
    # New Number Preference (optional)
    number_preference = models.CharField(max_length=100, blank=True,
                                       help_text="Preferred number series or pattern")
    
    # Personal Details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=10, blank=True, help_text="Alternate contact number")
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    
    # Documents
    aadhaar_card = models.FileField(upload_to='new_connection/aadhaar/', blank=True)
    pan_card = models.FileField(upload_to='new_connection/pan/', blank=True)
    photograph = models.ImageField(upload_to='new_connection/photos/', blank=True)
    address_proof = models.FileField(upload_to='new_connection/address/', blank=True)
    
    # Delivery Details
    preferred_delivery_date = models.DateField()
    preferred_delivery_time = models.TimeField()
    delivery_address = models.TextField(blank=True, help_text="If different from above")
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    tracking_id = models.CharField(max_length=20, unique=True, editable=False)
    new_mobile_number = models.CharField(max_length=10, blank=True, verbose_name="Assigned Number")
    activation_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"NEW-{self.tracking_id} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            date_str = timezone.now().strftime('%y%m%d')
            last_id = NewConnectionRequest.objects.filter(
                tracking_id__startswith=f"NEW{date_str}"
            ).count() + 1
            self.tracking_id = f"NEW{date_str}{str(last_id).zfill(4)}"
        super().save(*args, **kwargs)
    
    @property
    def can_assign_number(self):
        """Check if number can be assigned"""
        return self.status in ['document_verification', 'sim_dispatch']

class PlanComparison(models.Model):
    plan1 = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='comparison_plan1')
    plan2 = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='comparison_plan2')
    comparison_points = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.plan1.name} vs {self.plan2.name}"
    


# your_app/models.py
from django.db import models
from django.contrib.auth.models import User

class SIMReplacementRequest(models.Model):
    REASON_CHOICES = [
        ('lost', 'Lost SIM'),
        ('stolen', 'Stolen SIM'),
        ('damaged', 'Damaged SIM'),
        ('upgrade', 'Upgrade to eSIM'),
    ]
    
    OPERATOR_CHOICES = [
        ('airtel', 'Airtel'),
        ('jio', 'Jio'),
        ('vi', 'Vi (Vodafone Idea)'),
        ('bsnl', 'BSNL'),
        ('mtnl', 'MTNL'),
    ]
    
    SIM_TYPE_CHOICES = [
        ('regular', 'Regular SIM'),
        ('micro', 'Micro SIM'),
        ('nano', 'Nano SIM'),
        ('esim', 'eSIM'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('standard', 'Standard (₹99) - 24-48 hours'),
        ('fast', 'Fast Track (₹199) - 2-4 hours'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]
    
    # Request Information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    request_id = models.CharField(max_length=20, unique=True, editable=False)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    
    # Operator Details
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES)
    mobile_number = models.CharField(max_length=10)
    old_sim_type = models.CharField(max_length=20, choices=SIM_TYPE_CHOICES, default='nano')
    new_sim_type = models.CharField(max_length=20, choices=SIM_TYPE_CHOICES, default='nano')
    
    # Customer Details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    alternate_contact = models.CharField(max_length=10)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address Details
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    
    # Document Paths
    id_proof = models.FileField(upload_to='sim_replacement/id_proof/')
    address_proof = models.FileField(upload_to='sim_replacement/address_proof/')
    declaration_form = models.FileField(upload_to='sim_replacement/declaration/', blank=True)
    photo = models.ImageField(upload_to='sim_replacement/photos/', blank=True)
    
    # Service Details
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='standard')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=99.00)
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=50, blank=True)
    courier_partner = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    # Additional Info
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.request_id} - {self.mobile_number}"
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            import uuid
            self.request_id = f"SIM{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'SIM Replacement Request'
        verbose_name_plural = 'SIM Replacement Requests'