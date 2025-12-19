"""
DataPlus ERP - Enterprise Resource Planning System
Advanced Statistical Data Collection & Analysis Platform

Features:
- Role-based access control with multi-level permissions
- Complete document management with version control
- Real-time data validation and quality assurance
- Advanced reporting and analytics engine
- Comprehensive audit trail and compliance tracking
- Multi-currency and multi-language support
- Automated workflow and approval processes
- Cloud-ready with scalable architecture
- Enterprise-grade file management system
- Digital signature and approval workflows
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import os
from datetime import datetime


# ====================
# FILE UPLOAD HANDLERS
# ====================

def user_profile_upload_path(instance, filename):
    """Generate upload path for user profile photos"""
    ext = filename.split('.')[-1]
    filename = f"user_{instance.employee_id}_profile.{ext}"
    return os.path.join('users', 'profiles', filename)


def document_upload_path(instance, filename):
    """Generate upload path for general documents"""
    date_path = datetime.now().strftime('%Y/%m/%d')
    return os.path.join('documents', instance.document_type, date_path, filename)


def invoice_upload_path(instance, filename):
    """Generate upload path for invoices"""
    outlet = instance.outlet.outlet_code if instance.outlet else 'general'
    date_path = datetime.now().strftime('%Y/%m')
    return os.path.join('invoices', outlet, date_path, filename)


def report_upload_path(instance, filename):
    """Generate upload path for reports"""
    return os.path.join('reports', instance.period.period_name, filename)


def evidence_upload_path(instance, filename):
    """Generate upload path for price evidence photos"""
    outlet_code = instance.price_entry.outlet_product.outlet.outlet_code
    period = instance.price_entry.period.period_name
    return os.path.join('evidence', outlet_code, period, filename)


def contract_upload_path(instance, filename):
    """Generate upload path for contracts"""
    return os.path.join('contracts', str(instance.year), filename)


def training_material_upload_path(instance, filename):
    """Generate upload path for training materials"""
    return os.path.join('training', instance.category, filename)


def tender_upload_path(instance, filename):
    """Generate upload path for tender documents"""
    return os.path.join('tenders', instance.tender_number, filename)


# ====================
# ABSTRACT BASE MODELS
# ====================

class TimeStampedModel(models.Model):
    """Abstract model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        abstract = True


class AuditedModel(TimeStampedModel):
    """Abstract model with full audit trail"""
    created_by = models.ForeignKey(
        'User', 
        on_delete=models.PROTECT, 
        related_name='%(class)s_created',
        verbose_name=_("Created By"),
        null=True
    )
    updated_by = models.ForeignKey(
        'User', 
        on_delete=models.PROTECT, 
        related_name='%(class)s_updated',
        verbose_name=_("Updated By"),
        null=True,
        blank=True
    )
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Abstract model with soft delete capability"""
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Deleted"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Deleted At"))
    deleted_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name=_("Deleted By")
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user):
        """Soft delete the record"""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = datetime.now()
        self.deleted_by = user
        self.save()
    
    def restore(self):
        """Restore a soft-deleted record"""
        self.is_deleted = False
        self.is_active = True
        self.deleted_at = None
        self.deleted_by = None
        self.save()


# ====================
# USER MANAGEMENT
# ====================

class Department(AuditedModel, SoftDeleteModel):
    """Organization departments"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Department Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Department Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    manager = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("Department Manager")
    )
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments',
        verbose_name=_("Parent Department")
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Annual Budget")
    )
    
    class Meta:
        db_table = 'departments'
        ordering = ['code']
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class User(AbstractUser, SoftDeleteModel):
    """Enterprise user model with comprehensive features"""
    
    ROLE_CHOICES = [
        ('super_admin', _('Super Administrator')),
        ('admin', _('Administrator')),
        ('supervisor', _('Supervisor')),
        ('data_entry', _('Data Entry Officer')),
        ('field_officer', _('Field Officer')),
        ('analyst', _('Data Analyst')),
        ('accountant', _('Accountant')),
        ('auditor', _('Auditor')),
        ('manager', _('Manager')),
        ('viewer', _('Viewer')),
    ]
    
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    ]
    
    # Professional Information
    employee_id = models.CharField(max_length=20, unique=True, verbose_name=_("Employee ID"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer', verbose_name=_("User Role"))
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
        verbose_name=_("Department")
    )
    
    # Contact Information
    phone_number = models.CharField(max_length=15, blank=True, verbose_name=_("Phone Number"))
    alternative_phone = models.CharField(max_length=15, blank=True, verbose_name=_("Alternative Phone"))
    national_id = models.CharField(max_length=20, blank=True, unique=True, null=True, verbose_name=_("National ID"))
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name=_("Gender"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    profile_photo = models.ImageField(
        upload_to=user_profile_upload_path,
        blank=True,
        null=True,
        verbose_name=_("Profile Photo")
    )
    
    # Employment Details
    date_joined_company = models.DateField(null=True, blank=True, verbose_name=_("Date Joined"))
    job_title = models.CharField(max_length=100, blank=True, verbose_name=_("Job Title"))
    salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_("Salary")
    )
    
    # Access Control
    assigned_zones = models.ManyToManyField(
        'Zone', 
        blank=True, 
        related_name='assigned_users',
        verbose_name=_("Assigned Zones")
    )
    can_approve_prices = models.BooleanField(default=False, verbose_name=_("Can Approve Prices"))
    can_generate_reports = models.BooleanField(default=False, verbose_name=_("Can Generate Reports"))
    can_export_data = models.BooleanField(default=False, verbose_name=_("Can Export Data"))
    can_manage_users = models.BooleanField(default=False, verbose_name=_("Can Manage Users"))
    can_manage_finances = models.BooleanField(default=False, verbose_name=_("Can Manage Finances"))
    
    # Session Management
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Last Login IP"))
    failed_login_attempts = models.IntegerField(default=0, verbose_name=_("Failed Login Attempts"))
    account_locked_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Account Locked Until"))
    
    # Settings
    language_preference = models.CharField(max_length=10, default='en', verbose_name=_("Language"))
    timezone = models.CharField(max_length=50, default='Africa/Nairobi', verbose_name=_("Timezone"))
    email_notifications = models.BooleanField(default=True, verbose_name=_("Email Notifications"))
    sms_notifications = models.BooleanField(default=False, verbose_name=_("SMS Notifications"))
    
    # Digital Signature
    digital_signature = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        verbose_name=_("Digital Signature")
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()} ({self.get_role_display()})"
    
    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.pk})


# ====================
# GEOGRAPHICAL HIERARCHY
# ====================

class Basket(AuditedModel, SoftDeleteModel):
    """Top-level geographical grouping"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Basket Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Basket Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    coordinator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_baskets',
        verbose_name=_("Basket Coordinator")
    )
    
    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Annual Budget")
    )
    target_outlets = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Target Outlets")
    )
    
    class Meta:
        db_table = 'baskets'
        ordering = ['code']
        verbose_name = _("Basket")
        verbose_name_plural = _("Baskets")
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Zone(AuditedModel, SoftDeleteModel):
    """Geographical zones"""
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='zones', verbose_name=_("Basket"))
    name = models.CharField(max_length=100, verbose_name=_("Zone Name"))
    zone_code = models.CharField(max_length=20, unique=True, verbose_name=_("Zone Code"))
    
    region = models.CharField(max_length=100, blank=True, verbose_name=_("Region"))
    county = models.CharField(max_length=100, blank=True, verbose_name=_("County"))
    constituency = models.CharField(max_length=100, blank=True, verbose_name=_("Constituency"))
    
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_zones',
        verbose_name=_("Zone Supervisor")
    )
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Longitude"))
    
    class Meta:
        db_table = 'zones'
        ordering = ['zone_code']
        unique_together = [['basket', 'zone_code']]
        verbose_name = _("Zone")
        verbose_name_plural = _("Zones")
    
    def __str__(self):
        return f"{self.zone_code} - {self.name}"


# ====================
# OUTLET MANAGEMENT
# ====================

class OutletType(AuditedModel, SoftDeleteModel):
    """Outlet type classification"""
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Type Code"))
    name = models.CharField(max_length=200, verbose_name=_("Type Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    category = models.CharField(max_length=50, blank=True, verbose_name=_("Category"))
    is_formal = models.BooleanField(default=True, verbose_name=_("Is Formal Establishment"))
    requires_license = models.BooleanField(default=False, verbose_name=_("Requires License"))
    min_items = models.IntegerField(default=1, verbose_name=_("Minimum Items"))
    max_items = models.IntegerField(default=100, verbose_name=_("Maximum Items"))
    
    class Meta:
        db_table = 'outlet_types'
        ordering = ['code']
        verbose_name = _("Outlet Type")
        verbose_name_plural = _("Outlet Types")
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Outlet(AuditedModel, SoftDeleteModel):
    """Comprehensive outlet management"""
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='outlets', verbose_name=_("Zone"))
    outlet_type = models.ForeignKey(OutletType, on_delete=models.PROTECT, related_name='outlets', verbose_name=_("Outlet Type"))
    
    outlet_number = models.CharField(max_length=50, unique=True, verbose_name=_("Outlet Number"))
    outlet_code = models.CharField(max_length=50, unique=True, verbose_name=_("Outlet Code"))
    name = models.CharField(max_length=200, verbose_name=_("Outlet Name"))
    
    address = models.TextField(blank=True, verbose_name=_("Physical Address"))
    postal_address = models.CharField(max_length=100, blank=True, verbose_name=_("Postal Address"))
    contact_person = models.CharField(max_length=100, blank=True, verbose_name=_("Contact Person"))
    contact_phone = models.CharField(max_length=15, blank=True, verbose_name=_("Contact Phone"))
    contact_email = models.EmailField(blank=True, verbose_name=_("Contact Email"))
    
    business_registration_number = models.CharField(max_length=50, blank=True, verbose_name=_("Business Registration Number"))
    tax_identification_number = models.CharField(max_length=50, blank=True, verbose_name=_("Tax Identification Number"))
    
    max_items = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name=_("Maximum Items"))
    opening_hours = models.CharField(max_length=100, blank=True, verbose_name=_("Opening Hours"))
    operating_days = models.CharField(max_length=50, blank=True, verbose_name=_("Operating Days"))
    
    average_monthly_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Average Monthly Revenue")
    )
    
    assigned_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_outlets',
        verbose_name=_("Assigned Officer")
    )
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Longitude"))
    
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending Verification')),
            ('verified', _('Verified')),
            ('rejected', _('Rejected')),
        ],
        default='pending',
        verbose_name=_("Verification Status")
    )
    last_visited_date = models.DateField(null=True, blank=True, verbose_name=_("Last Visited"))
    
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        db_table = 'outlets'
        ordering = ['outlet_number']
        verbose_name = _("Outlet")
        verbose_name_plural = _("Outlets")
        indexes = [
            models.Index(fields=['zone', 'outlet_type']),
            models.Index(fields=['is_active', 'verification_status']),
        ]
    
    def __str__(self):
        return f"{self.outlet_number} - {self.name}"


# ====================
# PRODUCT CLASSIFICATION
# ====================

class Division(AuditedModel, SoftDeleteModel):
    """Top-level product classification"""
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Division Code"))
    name = models.CharField(max_length=100, verbose_name=_("Division Name"))
    name_local = models.CharField(max_length=100, blank=True, verbose_name=_("Local Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subdivisions',
        verbose_name=_("Parent Division")
    )
    
    sort_order = models.IntegerField(default=0, verbose_name=_("Sort Order"))
    
    class Meta:
        db_table = 'divisions'
        ordering = ['sort_order', 'code']
        verbose_name = _("Division")
        verbose_name_plural = _("Divisions")
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class COICOPCategory(AuditedModel, SoftDeleteModel):
    """COICOP classification system"""
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='coicop_categories', verbose_name=_("Division"))
    
    new_coicop = models.CharField(max_length=50, verbose_name=_("New COICOP"))
    old_coicop = models.CharField(max_length=50, blank=True, verbose_name=_("Old COICOP"))
    coicop_26 = models.CharField(max_length=50, blank=True, verbose_name=_("COICOP 26"))
    icp_code = models.CharField(max_length=50, blank=True, verbose_name=_("ICP Code"))
    eac_code = models.CharField(max_length=50, blank=True, verbose_name=_("EAC Code"))
    
    description = models.TextField(blank=True, verbose_name=_("Description"))
    description_local = models.TextField(blank=True, verbose_name=_("Local Description"))
    
    level = models.IntegerField(default=1, verbose_name=_("Classification Level"))
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("Parent Category")
    )
    
    class Meta:
        db_table = 'coicop_categories'
        ordering = ['new_coicop']
        verbose_name = _("COICOP Category")
        verbose_name_plural = _("COICOP Categories")
    
    def __str__(self):
        return f"{self.new_coicop}"


class Product(AuditedModel, SoftDeleteModel):
    """Enterprise product master data"""
    coicop_category = models.ForeignKey(COICOPCategory, on_delete=models.PROTECT, related_name='products', verbose_name=_("COICOP Category"))
    
    item_code = models.CharField(max_length=50, unique=True, verbose_name=_("Item Code"))
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True, verbose_name=_("Barcode"))
    sku = models.CharField(max_length=50, blank=True, verbose_name=_("SKU"))
    
    product_name = models.CharField(max_length=200, verbose_name=_("Product Name"))
    product_name_local = models.CharField(max_length=200, blank=True, verbose_name=_("Local Name"))
    specification = models.TextField(blank=True, verbose_name=_("Specification"))
    brand = models.CharField(max_length=100, blank=True, verbose_name=_("Brand"))
    manufacturer = models.CharField(max_length=200, blank=True, verbose_name=_("Manufacturer"))
    
    unit_of_measurement = models.CharField(max_length=50, verbose_name=_("Unit of Measurement"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Quantity"))
    pack_size = models.CharField(max_length=50, blank=True, verbose_name=_("Pack Size"))
    
    is_non_standard = models.BooleanField(default=False, verbose_name=_("Non-Standard Item"))
    is_seasonal = models.BooleanField(default=False, verbose_name=_("Seasonal Item"))
    is_imported = models.BooleanField(default=False, verbose_name=_("Imported Item"))
    country_of_origin = models.CharField(max_length=100, blank=True, verbose_name=_("Country of Origin"))
    
    reference_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Reference Price"))
    min_expected_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Min Expected Price"))
    max_expected_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Max Expected Price"))
    
    product_image = models.ImageField(upload_to='products/images/', blank=True, null=True, verbose_name=_("Product Image"))
    
    requires_quality_check = models.BooleanField(default=False, verbose_name=_("Requires Quality Check"))
    quality_standards = models.TextField(blank=True, verbose_name=_("Quality Standards"))
    
    tags = models.CharField(max_length=200, blank=True, verbose_name=_("Tags"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        db_table = 'products'
        ordering = ['item_code']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
    
    def __str__(self):
        return f"{self.item_code} - {self.product_name}"


# ====================
# PRICE COLLECTION
# ====================

class PricePeriod(AuditedModel, SoftDeleteModel):
    """Survey periods with comprehensive tracking"""
    year = models.IntegerField(verbose_name=_("Year"))
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name=_("Month"))
    period_name = models.CharField(max_length=50, verbose_name=_("Period Name"))
    
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('open', _('Open for Collection')),
        ('review', _('Under Review')),
        ('closed', _('Closed')),
        ('archived', _('Archived')),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Status"))
    
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Closed At"))
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='periods_closed', verbose_name=_("Closed By"))
    
    target_outlets = models.IntegerField(default=0, verbose_name=_("Target Outlets"))
    target_prices = models.IntegerField(default=0, verbose_name=_("Target Prices"))
    collected_prices = models.IntegerField(default=0, verbose_name=_("Collected Prices"))
    approved_prices = models.IntegerField(default=0, verbose_name=_("Approved Prices"))
    
    allocated_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Allocated Budget"))
    
    description = models.TextField(blank=True, verbose_name=_("Description"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        db_table = 'price_periods'
        ordering = ['-year', '-month']
        unique_together = [['year', 'month']]
        verbose_name = _("Price Period")
        verbose_name_plural = _("Price Periods")
    
    def __str__(self):
        return f"{self.period_name}"
    
    @property
    def completion_percentage(self):
        if self.target_prices == 0:
            return 0
        return (self.collected_prices / self.target_prices) * 100


class OutletProduct(AuditedModel, SoftDeleteModel):
    """Junction table with availability tracking"""
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='outlet_products', verbose_name=_("Outlet"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='outlet_products', verbose_name=_("Product"))
    item_number = models.IntegerField(validators=[MinValueValidator(1)], verbose_name=_("Item Number"))
    
    is_available = models.BooleanField(default=True, verbose_name=_("Is Available"))
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ('regular', _('Regular Stock')),
            ('seasonal', _('Seasonal')),
            ('discontinued', _('Discontinued')),
            ('out_of_stock', _('Out of Stock')),
        ],
        default='regular',
        verbose_name=_("Availability Status")
    )
    
    last_seen_date = models.DateField(null=True, blank=True, verbose_name=_("Last Seen Date"))
    last_price_date = models.DateField(null=True, blank=True, verbose_name=_("Last Price Date"))
    local_brand = models.CharField(max_length=100, blank=True, verbose_name=_("Local Brand Name"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        db_table = 'outlet_products'
        unique_together = [['outlet', 'product', 'item_number']]
        ordering = ['outlet', 'item_number']
        verbose_name = _("Outlet Product")
        verbose_name_plural = _("Outlet Products")
    
    def __str__(self):
        return f"{self.outlet.name} - {self.product.product_name}"


class PriceEntry(models.Model):
    """Individual price observations"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    outlet_product = models.ForeignKey(OutletProduct, on_delete=models.CASCADE, related_name='prices')
    period = models.ForeignKey(PricePeriod, on_delete=models.CASCADE, related_name='price_entries')
    
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Audit trail
    collected_date = models.DateField()
    collected_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='prices_collected')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='prices_verified')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'price_entries'
        unique_together = [['outlet_product', 'period']]
        ordering = ['-period', 'outlet_product']
        indexes = [
            models.Index(fields=['period', 'status']),
            models.Index(fields=['collected_by', 'status']),
            models.Index(fields=['collected_date']),
        ]
    
    def __str__(self):
        return f"{self.outlet_product.outlet.name} - {self.outlet_product.product.product_name} - {self.period.period_name}: {self.price}"


"""
DataPlus ERP - Part 2: Document Management & Advanced Features
Includes: Document Management, Financial Management, Workflow, Training, and Analytics
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import os
from datetime import datetime


# ====================
# DOCUMENT MANAGEMENT SYSTEM
# ====================

class DocumentCategory(models.Model):
    """Categories for organizing documents"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Category Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("Parent Category")
    )
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon Class"))
    color = models.CharField(max_length=7, default='#3498db', verbose_name=_("Color"))
    
    class Meta:
        db_table = 'document_categories'
        ordering = ['code']
        verbose_name = _("Document Category")
        verbose_name_plural = _("Document Categories")
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Document(models.Model):
    """Universal document management system"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('invoice', _('Invoice')),
        ('receipt', _('Receipt')),
        ('contract', _('Contract')),
        ('report', _('Report')),
        ('policy', _('Policy Document')),
        ('manual', _('Manual')),
        ('form', _('Form')),
        ('certificate', _('Certificate')),
        ('license', _('License')),
        ('permit', _('Permit')),
        ('letter', _('Official Letter')),
        ('memo', _('Memorandum')),
        ('evidence', _('Price Evidence')),
        ('tender', _('Tender Document')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending_review', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('archived', _('Archived')),
        ('expired', _('Expired')),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255, verbose_name=_("Document Title"))
    document_number = models.CharField(max_length=50, unique=True, verbose_name=_("Document Number"))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, verbose_name=_("Document Type"))
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        related_name='documents',
        verbose_name=_("Category")
    )
    
    # File Storage
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip']
            )
        ],
        verbose_name=_("File")
    )
    file_size = models.BigIntegerField(default=0, verbose_name=_("File Size (bytes)"))
    mime_type = models.CharField(max_length=100, blank=True, verbose_name=_("MIME Type"))
    
    # Metadata
    description = models.TextField(blank=True, verbose_name=_("Description"))
    tags = models.CharField(max_length=255, blank=True, verbose_name=_("Tags"))
    version = models.CharField(max_length=20, default='1.0', verbose_name=_("Version"))
    
    # Status and Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Status"))
    
    # Related Objects (Generic Foreign Key for flexibility)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Dates
    document_date = models.DateField(verbose_name=_("Document Date"))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_("Expiry Date"))
    
    # Access Control
    is_confidential = models.BooleanField(default=False, verbose_name=_("Confidential"))
    is_public = models.BooleanField(default=False, verbose_name=_("Public"))
    allowed_roles = models.JSONField(default=list, blank=True, verbose_name=_("Allowed Roles"))
    
    # Audit Trail
    uploaded_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='documents_uploaded', verbose_name=_("Uploaded By"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
    
    reviewed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_reviewed',
        verbose_name=_("Reviewed By")
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reviewed At"))
    
    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_approved',
        verbose_name=_("Approved By")
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    
    # Download Tracking
    download_count = models.IntegerField(default=0, verbose_name=_("Download Count"))
    last_downloaded_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Downloaded"))
    
    # Full Text Search
    search_vector = models.TextField(blank=True, verbose_name=_("Search Vector"))
    
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        db_table = 'documents'
        ordering = ['-uploaded_at']
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        indexes = [
            models.Index(fields=['document_type', 'status']),
            models.Index(fields=['uploaded_by', 'uploaded_at']),
            models.Index(fields=['document_date']),
        ]
    
    def __str__(self):
        return f"{self.document_number} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('document-detail', kwargs={'pk': self.pk})


class DocumentVersion(models.Model):
    """Document version control"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions', verbose_name=_("Document"))
    version_number = models.CharField(max_length=20, verbose_name=_("Version Number"))
    file = models.FileField(upload_to='documents/versions/', verbose_name=_("File"))
    
    changes_description = models.TextField(blank=True, verbose_name=_("Changes Description"))
    
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='document_versions_created')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    file_size = models.BigIntegerField(default=0, verbose_name=_("File Size"))
    
    class Meta:
        db_table = 'document_versions'
        ordering = ['-created_at']
        unique_together = [['document', 'version_number']]
        verbose_name = _("Document Version")
        verbose_name_plural = _("Document Versions")
    
    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"


# ====================
# FINANCIAL MANAGEMENT
# ====================

class Invoice(models.Model):
    """Invoice management for outlet payments and expenses"""
    
    INVOICE_TYPE_CHOICES = [
        ('payment', _('Payment to Outlet')),
        ('expense', _('Operating Expense')),
        ('salary', _('Salary Payment')),
        ('vendor', _('Vendor Payment')),
        ('allowance', _('Allowance Payment')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]
    
    # Identification
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name=_("Invoice Number"))
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, verbose_name=_("Invoice Type"))
    
    # Related Entity
    outlet = models.ForeignKey(
        'Outlet',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_("Outlet")
    )
    vendor_name = models.CharField(max_length=200, blank=True, verbose_name=_("Vendor Name"))
    
    # Financial Details
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Amount"))
    currency = models.CharField(max_length=3, default='KES', verbose_name=_("Currency"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("Tax Amount"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Total Amount"))
    
    # Dates
    invoice_date = models.DateField(verbose_name=_("Invoice Date"))
    due_date = models.DateField(verbose_name=_("Due Date"))
    payment_date = models.DateField(null=True, blank=True, verbose_name=_("Payment Date"))
    
    # Description
    description = models.TextField(verbose_name=_("Description"))
    items_description = models.JSONField(default=list, blank=True, verbose_name=_("Line Items"))
    
    # Status and Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Status"))
    
    # Payment Details
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('bank_transfer', _('Bank Transfer')),
            ('mpesa', _('M-Pesa')),
            ('cash', _('Cash')),
            ('cheque', _('Cheque')),
        ],
        blank=True,
        verbose_name=_("Payment Method")
    )
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name=_("Payment Reference"))
    
    # Document Attachment
    invoice_file = models.FileField(
        upload_to=invoice_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name=_("Invoice File")
    )
    
    # Audit
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='invoices_created', verbose_name=_("Created By"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_approved',
        verbose_name=_("Approved By")
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    
    paid_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_paid',
        verbose_name=_("Paid By")
    )
    
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-invoice_date']
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        indexes = [
            models.Index(fields=['status', 'invoice_date']),
            models.Index(fields=['outlet']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.vendor_name or self.outlet}"
    
    def save(self, *args, **kwargs):
        self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)


class Budget(models.Model):
    """Budget planning and tracking"""
    
    BUDGET_TYPE_CHOICES = [
        ('operational', _('Operational Budget')),
        ('capital', _('Capital Budget')),
        ('project', _('Project Budget')),
        ('departmental', _('Departmental Budget')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_("Budget Name"))
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPE_CHOICES, verbose_name=_("Budget Type"))
    
    fiscal_year = models.IntegerField(verbose_name=_("Fiscal Year"))
    
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='budgets',
        verbose_name=_("Department")
    )
    
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Allocated Amount"))
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("Spent Amount"))
    committed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("Committed Amount"))
    
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='budgets_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budgets'
        ordering = ['-fiscal_year', 'name']
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")
    
    def __str__(self):
        return f"{self.name} - FY {self.fiscal_year}"
    
    @property
    def available_amount(self):
        return self.allocated_amount - self.spent_amount - self.committed_amount
    
    @property
    def utilization_percentage(self):
        if self.allocated_amount == 0:
            return 0
        return (self.spent_amount / self.allocated_amount) * 100


# ====================
# WORKFLOW & APPROVALS
# ====================

class WorkflowTemplate(models.Model):
    """Workflow templates for approval processes"""
    
    name = models.CharField(max_length=200, verbose_name=_("Workflow Name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Applicable to
    applies_to = models.CharField(
        max_length=50,
        choices=[
            ('price_entry', _('Price Entry')),
            ('document', _('Document')),
            ('invoice', _('Invoice')),
            ('outlet', _('Outlet')),
            ('report', _('Report')),
        ],
        verbose_name=_("Applies To")
    )
    
    # Workflow steps (JSON structure)
    steps = models.JSONField(default=list, verbose_name=_("Workflow Steps"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='workflow_templates_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflow_templates'
        ordering = ['code']
        verbose_name = _("Workflow Template")
        verbose_name_plural = _("Workflow Templates")
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class WorkflowInstance(models.Model):
    """Active workflow instances"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]
    
    workflow_template = models.ForeignKey(WorkflowTemplate, on_delete=models.PROTECT, related_name='instances')
    
    # Related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')
    
    current_step = models.IntegerField(default=0, verbose_name=_("Current Step"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    
    initiated_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='workflows_initiated')
    initiated_at = models.DateTimeField(auto_now_add=True)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'workflow_instances'
        ordering = ['-initiated_at']
        verbose_name = _("Workflow Instance")
        verbose_name_plural = _("Workflow Instances")
    
    def __str__(self):
        return f"{self.workflow_template.name} - {self.get_status_display()}"


class ApprovalAction(models.Model):
    """Individual approval actions within workflows"""
    
    ACTION_CHOICES = [
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('returned', _('Returned for Revision')),
        ('forwarded', _('Forwarded')),
    ]
    
    workflow_instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name='actions')
    step_number = models.IntegerField(verbose_name=_("Step Number"))
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_("Action"))
    comments = models.TextField(blank=True, verbose_name=_("Comments"))
    
    actioned_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='approval_actions')
    actioned_at = models.DateTimeField(auto_now_add=True)
    
    # Digital signature
    signature_image = models.ImageField(
        upload_to='signatures/approvals/',
        blank=True,
        null=True,
        verbose_name=_("Digital Signature")
    )
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'approval_actions'
        ordering = ['-actioned_at']
        verbose_name = _("Approval Action")
        verbose_name_plural = _("Approval Actions")
    
    def __str__(self):
        return f"{self.actioned_by} - {self.get_action_display()}"


# ====================
# PRICE EVIDENCE & VALIDATION
# ====================

class PriceEvidence(models.Model):
    """Photo evidence for price entries"""
    
    price_entry = models.ForeignKey('PriceEntry', on_delete=models.CASCADE, related_name='evidence_photos')
    
    photo = models.ImageField(
        upload_to=evidence_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name=_("Evidence Photo")
    )
    
    caption = models.CharField(max_length=255, blank=True, verbose_name=_("Caption"))
    
    # GPS coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Metadata
    taken_at = models.DateTimeField(verbose_name=_("Photo Taken At"))
    uploaded_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='evidence_photos_uploaded')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    file_size = models.BigIntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidence_verified'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'price_evidence'
        ordering = ['-uploaded_at']
        verbose_name = _("Price Evidence")
        verbose_name_plural = _("Price Evidence")
    
    def __str__(self):
        return f"Evidence for {self.price_entry}"


# ====================
# TRAINING & CAPACITY BUILDING
# ====================

class TrainingModule(models.Model):
    """Training modules for system users"""
    
    title = models.CharField(max_length=200, verbose_name=_("Module Title"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Module Code"))
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('system_basics', _('System Basics')),
            ('data_collection', _('Data Collection')),
            ('analysis', _('Data Analysis')),
            ('reporting', _('Reporting')),
            ('administration', _('System Administration')),
        ],
        verbose_name=_("Category")
    )
    
    description = models.TextField(verbose_name=_("Description"))
    
    # Content
    content = models.TextField(blank=True, verbose_name=_("Content"))
    duration_minutes = models.IntegerField(default=60, verbose_name=_("Duration (minutes)"))
    
    # Materials
    training_file = models.FileField(
        upload_to=training_material_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'ppt', 'pptx', 'mp4'])],
        verbose_name=_("Training Material")
    )
    
    # Prerequisites
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, verbose_name=_("Prerequisites"))
    
    is_mandatory = models.BooleanField(default=False, verbose_name=_("Mandatory"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='training_modules_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'training_modules'
        ordering = ['code']
        verbose_name = _("Training Module")
        verbose_name_plural = _("Training Modules")
    
    def __str__(self):
        return f"{self.code} - {self.title}"


class UserTraining(models.Model):
    """Track user training completion"""
    
    STATUS_CHOICES = [
        ('not_started', _('Not Started')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='training_records')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='user_completions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Score (%)")
    )
    
    certificate_file = models.FileField(
        upload_to='training/certificates/',
        blank=True,
        null=True,
        verbose_name=_("Certificate")
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_training'
        ordering = ['-completed_at']
        unique_together = [['user', 'module']]
        verbose_name = _("User Training")
        verbose_name_plural = _("User Training Records")
    
    def __str__(self):
        return f"{self.user} - {self.module.title}"


# ====================
# REPORTS & ANALYTICS
# ====================

class GeneratedReport(models.Model):
    """Store generated reports"""
    
    REPORT_TYPE_CHOICES = [
        ('price_summary', _('Price Summary Report')),
        ('outlet_performance', _('Outlet Performance Report')),
        ('data_quality', _('Data Quality Report')),
        ('financial', _('Financial Report')),
        ('collection_status', _('Collection Status Report')),
        ('custom', _('Custom Report')),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, verbose_name=_("Report Type"))
    title = models.CharField(max_length=255, verbose_name=_("Report Title"))
    
    period = models.ForeignKey(
        'PricePeriod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name=_("Period")
    )
    
    # Filters used
    filters = models.JSONField(default=dict, blank=True, verbose_name=_("Applied Filters"))
    
    # Generated file
    report_file = models.FileField(
        upload_to=report_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'xlsx', 'csv'])],
        verbose_name=_("Report File")
    )
    
    file_format = models.CharField(
        max_length=10,
        choices=[
            ('pdf', 'PDF'),
            ('xlsx', 'Excel'),
            ('csv', 'CSV'),
        ],
        default='pdf',
        verbose_name=_("File Format")
    )
    
    file_size = models.BigIntegerField(default=0, verbose_name=_("File Size"))
    
    # Metadata
    generated_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='reports_generated')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    download_count = models.IntegerField(default=0)
    
    is_public = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'generated_reports'
        ordering = ['-generated_at']
        verbose_name = _("Generated Report")
        verbose_name_plural = _("Generated Reports")
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%Y-%m-%d')}"


# ====================
# AUDIT & HISTORY
# ====================

class AuditLog(models.Model):
    """Comprehensive system audit trail"""
    
    ACTION_CHOICES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('approve', _('Approve')),
        ('reject', _('Reject')),
        ('export', _('Export')),
        ('import', _('Import')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('download', _('Download')),
        ('upload', _('Upload')),
    ]
    
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.IntegerField(null=True, blank=True)
    
    description = models.TextField()
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.model_name} - {self.timestamp}"


# ====================
# NOTIFICATIONS & ALERTS
# ====================

class Notification(models.Model):
    """User notifications system"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('info', _('Information')),
        ('success', _('Success')),
        ('warning', _('Warning')),
        ('error', _('Error')),
        ('approval_required', _('Approval Required')),
        ('deadline', _('Deadline Alert')),
    ]
    
    recipient = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    message = models.TextField(verbose_name=_("Message"))
    
    # Related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    action_url = models.CharField(max_length=255, blank=True, verbose_name=_("Action URL"))
    
    is_read = models.BooleanField(default=False, verbose_name=_("Read"))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Read At"))
    
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient}"


# ====================
# SYSTEM CONFIGURATION
# ====================

class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    
    key = models.CharField(max_length=100, unique=True, verbose_name=_("Configuration Key"))
    value = models.TextField(verbose_name=_("Configuration Value"))
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('general', _('General')),
            ('security', _('Security')),
            ('email', _('Email')),
            ('sms', _('SMS')),
            ('storage', _('Storage')),
            ('api', _('API')),
        ],
        default='general',
        verbose_name=_("Category")
    )
    
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    is_encrypted = models.BooleanField(default=False, verbose_name=_("Encrypted"))
    is_public = models.BooleanField(default=False, verbose_name=_("Public"))
    
    updated_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='configurations_updated')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configuration'
        ordering = ['category', 'key']
        verbose_name = _("System Configuration")
        verbose_name_plural = _("System Configurations")
    
    def __str__(self):
        return f"{self.key}"


# ====================
# DATA QUALITY & VALIDATION
# ====================

class DataQualityCheck(models.Model):
    """Data quality validation rules"""
    
    CHECK_TYPE_CHOICES = [
        ('outlier', _('Outlier Detection')),
        ('consistency', _('Consistency Check')),
        ('completeness', _('Completeness Check')),
        ('timeliness', _('Timeliness Check')),
        ('accuracy', _('Accuracy Check')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_("Check Name"))
    check_type = models.CharField(max_length=20, choices=CHECK_TYPE_CHOICES)
    
    applies_to_model = models.CharField(max_length=50, verbose_name=_("Applies To Model"))
    
    rule_definition = models.JSONField(verbose_name=_("Rule Definition"))
    
    threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Threshold")
    )
    
    is_active = models.BooleanField(default=True)
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Low')),
            ('medium', _('Medium')),
            ('high', _('High')),
            ('critical', _('Critical')),
        ],
        default='medium'
    )
    
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='quality_checks_created')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_quality_checks'
        ordering = ['check_type', 'name']
        verbose_name = _("Data Quality Check")
        verbose_name_plural = _("Data Quality Checks")
    
    def __str__(self):
        return f"{self.name} ({self.get_check_type_display()})"


class DataQualityIssue(models.Model):
    """Detected data quality issues"""
    
    STATUS_CHOICES = [
        ('open', _('Open')),
        ('investigating', _('Investigating')),
        ('resolved', _('Resolved')),
        ('false_positive', _('False Positive')),
        ('ignored', _('Ignored')),
    ]
    
    quality_check = models.ForeignKey(DataQualityCheck, on_delete=models.CASCADE, related_name='issues')
    
    # Related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')
    
    issue_description = models.TextField(verbose_name=_("Issue Description"))
    
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Low')),
            ('medium', _('Medium')),
            ('high', _('High')),
            ('critical', _('Critical')),
        ]
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quality_issues_resolved'
    )
    
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'data_quality_issues'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['detected_at']),
        ]
        verbose_name = _("Data Quality Issue")
        verbose_name_plural = _("Data Quality Issues")
    
    def __str__(self):
        return f"{self.quality_check.name} - {self.get_severity_display()}"


# ====================
# SAVED QUERIES & FILTERS
# ====================

class SavedReport(models.Model):
    """User-saved reports and filters for reuse"""
    
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='saved_reports')
    name = models.CharField(max_length=200, verbose_name=_("Report Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    report_type = models.CharField(max_length=50, verbose_name=_("Report Type"))
    filters = models.JSONField(verbose_name=_("Filter Parameters"))
    
    is_public = models.BooleanField(default=False, verbose_name=_("Share with Others"))
    is_scheduled = models.BooleanField(default=False, verbose_name=_("Schedule Generation"))
    
    # Scheduling
    schedule_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
        ],
        blank=True,
        verbose_name=_("Schedule Frequency")
    )
    
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'saved_reports'
        ordering = ['-created_at']
        verbose_name = _("Saved Report")
        verbose_name_plural = _("Saved Reports")
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


# ====================
# API & INTEGRATION
# ====================

class APIKey(models.Model):
    """API keys for external integrations"""
    
    name = models.CharField(max_length=200, verbose_name=_("Key Name"))
    key = models.CharField(max_length=64, unique=True, verbose_name=_("API Key"))
    
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='api_keys')
    
    permissions = models.JSONField(default=list, verbose_name=_("Permissions"))
    
    is_active = models.BooleanField(default=True)
    
    rate_limit = models.IntegerField(default=1000, verbose_name=_("Rate Limit (requests/hour)"))
    
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")
    
    def __str__(self):
        return f"{self.name} ({self.user})"


class ExternalIntegration(models.Model):
    """External system integrations"""
    
    INTEGRATION_TYPE_CHOICES = [
        ('mpesa', _('M-Pesa Payment')),
        ('email', _('Email Service')),
        ('sms', _('SMS Gateway')),
        ('cloud_storage', _('Cloud Storage')),
        ('erp', _('External ERP')),
        ('api', _('Custom API')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_("Integration Name"))
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPE_CHOICES)
    
    configuration = models.JSONField(verbose_name=_("Configuration"))
    
    is_active = models.BooleanField(default=True)
    
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=50, blank=True)
    
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='integrations_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'external_integrations'
        ordering = ['name']
        verbose_name = _("External Integration")
        verbose_name_plural = _("External Integrations")
    
    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"