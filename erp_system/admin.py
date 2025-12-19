"""
DataPlus ERP - Django Admin Configuration
Comprehensive admin interface with advanced features
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django import forms
from .models import *


# ====================
# CUSTOM ADMIN FILTERS
# ====================

class ActiveFilter(admin.SimpleListFilter):
    """Filter for active/inactive records"""
    title = _('Status')
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active')),
            ('inactive', _('Inactive')),
            ('deleted', _('Deleted')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True, is_deleted=False)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False, is_deleted=False)
        if self.value() == 'deleted':
            return queryset.filter(is_deleted=True)


class DateRangeFilter(admin.SimpleListFilter):
    """Filter for date ranges"""
    title = _('Date Range')
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('week', _('This Week')),
            ('month', _('This Month')),
            ('year', _('This Year')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        if self.value() == 'week':
            return queryset.filter(created_at__week=now.isocalendar()[1])
        if self.value() == 'month':
            return queryset.filter(created_at__month=now.month)
        if self.value() == 'year':
            return queryset.filter(created_at__year=now.year)


# ====================
# INLINE ADMIN CLASSES
# ====================

class SubDepartmentInline(admin.TabularInline):
    model = Department
    fk_name = 'parent_department'
    extra = 0
    fields = ('code', 'name', 'manager', 'is_active')


class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0
    fields = ('zone_code', 'name', 'supervisor', 'is_active')


class OutletProductInline(admin.TabularInline):
    model = OutletProduct
    extra = 0
    fields = ('product', 'item_number', 'is_available', 'availability_status')
    autocomplete_fields = ['product']


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ('version_number', 'created_by', 'created_at', 'file_size')
    fields = ('version_number', 'file', 'changes_description', 'created_by', 'created_at')


class PriceEvidenceInline(admin.TabularInline):
    model = PriceEvidence
    extra = 0
    readonly_fields = ('uploaded_at', 'uploaded_by', 'file_size')
    fields = ('photo', 'caption', 'taken_at', 'is_verified')


class ApprovalActionInline(admin.TabularInline):
    model = ApprovalAction
    extra = 0
    readonly_fields = ('actioned_by', 'actioned_at', 'ip_address')
    fields = ('step_number', 'action', 'comments', 'actioned_by', 'actioned_at')


# ====================
# USER MANAGEMENT ADMIN
# ====================

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminForm
    list_display = (
        'employee_id', 'username', 'get_full_name', 'email', 
        'role', 'department', 'is_active', 'last_login'
    )
    list_filter = ('role', 'department', 'is_active', 'is_staff', 'gender', ActiveFilter)
    search_fields = ('employee_id', 'username', 'first_name', 'last_name', 'email', 'national_id')
    ordering = ('employee_id',)
    
    fieldsets = (
        (_('Authentication'), {
            'fields': ('username', 'password', 'email')
        }),
        (_('Personal Information'), {
            'fields': (
                'employee_id', 'first_name', 'last_name', 'date_of_birth', 
                'gender', 'national_id', 'profile_photo', 'digital_signature'
            )
        }),
        (_('Contact Information'), {
            'fields': ('phone_number', 'alternative_phone', 'address')
        }),
        (_('Employment Details'), {
            'fields': (
                'department', 'job_title', 'role', 'salary', 
                'date_joined_company'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'can_approve_prices', 'can_generate_reports', 
                'can_export_data', 'can_manage_users', 'can_manage_finances',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Assigned Zones'), {
            'fields': ('assigned_zones',)
        }),
        (_('Settings'), {
            'fields': (
                'language_preference', 'timezone', 
                'email_notifications', 'sms_notifications'
            ),
            'classes': ('collapse',)
        }),
        (_('Session & Security'), {
            'fields': (
                'last_login', 'last_login_ip', 'failed_login_attempts', 
                'account_locked_until'
            ),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_deleted', 'deleted_at', 'deleted_by')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'email', 
                'employee_id', 'first_name', 'last_name', 'role', 'department'
            ),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions', 'assigned_zones')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager', 'budget', 'parent_department', 'is_active')
    list_filter = ('is_active', ActiveFilter)
    search_fields = ('code', 'name', 'description')
    inlines = [SubDepartmentInline]
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'name', 'description', 'parent_department')
        }),
        (_('Management'), {
            'fields': ('manager', 'budget')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
        (_('Audit Trail'), {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ====================
# GEOGRAPHICAL ADMIN
# ====================

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'coordinator', 'annual_budget', 'target_outlets', 'is_active')
    list_filter = ('is_active', ActiveFilter)
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = [ZoneInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'name', 'description')
        }),
        (_('Management'), {
            'fields': ('coordinator', 'annual_budget', 'target_outlets')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
        (_('Audit Trail'), {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_code', 'name', 'basket', 'supervisor', 'region', 'county', 'is_active')
    list_filter = ('basket', 'is_active', 'region', ActiveFilter)
    search_fields = ('zone_code', 'name', 'county', 'constituency')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('basket', 'zone_code', 'name')
        }),
        (_('Location'), {
            'fields': ('region', 'county', 'constituency', 'latitude', 'longitude')
        }),
        (_('Management'), {
            'fields': ('supervisor',)
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
        (_('Audit Trail'), {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ====================
# OUTLET MANAGEMENT ADMIN
# ====================

@admin.register(OutletType)
class OutletTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'is_formal', 'requires_license', 'is_active')
    list_filter = ('is_formal', 'requires_license', 'category', ActiveFilter)
    search_fields = ('code', 'name', 'category')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = (
        'outlet_number', 'name', 'outlet_type', 'zone', 
        'verification_status', 'assigned_officer', 'is_active'
    )
    list_filter = (
        'outlet_type', 'zone__basket', 'verification_status', 
        'is_active', ActiveFilter
    )
    search_fields = (
        'outlet_number', 'outlet_code', 'name', 
        'contact_person', 'contact_phone'
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'last_visited_date')
    inlines = [OutletProductInline]
    autocomplete_fields = ['zone', 'outlet_type', 'assigned_officer']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'outlet_number', 'outlet_code', 'name', 
                'zone', 'outlet_type'
            )
        }),
        (_('Contact Information'), {
            'fields': (
                'address', 'postal_address', 'contact_person', 
                'contact_phone', 'contact_email'
            )
        }),
        (_('Business Details'), {
            'fields': (
                'business_registration_number', 'tax_identification_number',
                'average_monthly_revenue'
            )
        }),
        (_('Operations'), {
            'fields': (
                'max_items', 'opening_hours', 'operating_days'
            )
        }),
        (_('Location'), {
            'fields': ('latitude', 'longitude')
        }),
        (_('Management'), {
            'fields': (
                'assigned_officer', 'verification_status', 
                'last_visited_date', 'notes'
            )
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
        (_('Audit Trail'), {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_verified', 'mark_pending', 'assign_to_me']
    
    def mark_verified(self, request, queryset):
        queryset.update(verification_status='verified')
    mark_verified.short_description = _("Mark selected outlets as verified")
    
    def mark_pending(self, request, queryset):
        queryset.update(verification_status='pending')
    mark_pending.short_description = _("Mark selected outlets as pending")
    
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_officer=request.user)
    assign_to_me.short_description = _("Assign selected outlets to me")


# ====================
# PRODUCT CLASSIFICATION ADMIN
# ====================

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'sort_order', 'is_active')
    list_filter = ('is_active', ActiveFilter)
    search_fields = ('code', 'name', 'name_local')
    ordering = ('sort_order', 'code')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


@admin.register(COICOPCategory)
class COICOPCategoryAdmin(admin.ModelAdmin):
    list_display = ('new_coicop', 'division', 'level', 'parent_category', 'is_active')
    list_filter = ('division', 'level', 'is_active', ActiveFilter)
    search_fields = ('new_coicop', 'old_coicop', 'coicop_26', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'item_code', 'product_name', 'brand', 'coicop_category', 
        'unit_of_measurement', 'quantity', 'is_active'
    )
    list_filter = (
        'coicop_category__division', 'is_non_standard', 
        'is_seasonal', 'is_imported', 'is_active', ActiveFilter
    )
    search_fields = (
        'item_code', 'barcode', 'sku', 'product_name', 
        'product_name_local', 'brand', 'manufacturer'
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    autocomplete_fields = ['coicop_category']
    
    fieldsets = (
        (_('Identification'), {
            'fields': ('item_code', 'barcode', 'sku')
        }),
        (_('Product Details'), {
            'fields': (
                'coicop_category', 'product_name', 'product_name_local',
                'specification', 'brand', 'manufacturer'
            )
        }),
        (_('Measurement'), {
            'fields': (
                'unit_of_measurement', 'quantity', 'pack_size'
            )
        }),
        (_('Classification'), {
            'fields': (
                'is_non_standard', 'is_seasonal', 'is_imported', 
                'country_of_origin', 'requires_quality_check', 'quality_standards'
            )
        }),
        (_('Pricing'), {
            'fields': (
                'reference_price', 'min_expected_price', 'max_expected_price'
            )
        }),
        (_('Media & Notes'), {
            'fields': ('product_image', 'tags', 'notes')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_deleted')
        }),
        (_('Audit Trail'), {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ====================
# PRICE COLLECTION ADMIN
# ====================

@admin.register(PricePeriod)
class PricePeriodAdmin(admin.ModelAdmin):
    list_display = (
        'period_name', 'year', 'month', 'status', 
        'start_date', 'end_date', 'completion_rate'
    )
    list_filter = ('status', 'year', 'month')
    search_fields = ('period_name',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'completion_percentage')
    
    fieldsets = (
        (_('Period Information'), {
            'fields': ('year', 'month', 'period_name', 'start_date', 'end_date')
        }),
        (_('Status'), {
            'fields': ('status', 'closed_at', 'closed_by')
        }),
        (_('Targets & Progress'), {
            'fields': (
                'target_outlets', 'target_prices', 
                'collected_prices', 'approved_prices', 'completion_percentage'
            )
        }),
        (_('Budget'), {
            'fields': ('allocated_budget',)
        }),
        (_('Notes'), {
            'fields': ('description', 'notes')
        }),
        (_('Audit Trail'), {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def completion_rate(self, obj):
        return f"{obj.completion_percentage:.1f}%"
    completion_rate.short_description = _("Completion")


@admin.register(OutletProduct)
class OutletProductAdmin(admin.ModelAdmin):
    list_display = (
        'outlet', 'product', 'item_number', 
        'is_available', 'availability_status', 'last_price_date'
    )
    list_filter = ('is_available', 'availability_status', 'is_active', ActiveFilter)
    search_fields = ('outlet__name', 'product__product_name', 'local_brand')
    autocomplete_fields = ['outlet', 'product']
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


@admin.register(PriceEntry)
class PriceEntryAdmin(admin.ModelAdmin):
    list_display = (
        'get_outlet', 'get_product', 'period', 
        'price', 'status', 'collected_date', 'collected_by'
    )
    list_filter = ('status', 'period', 'collected_date')
    search_fields = (
        'outlet_product__outlet__name', 
        'outlet_product__product__product_name'
    )
    readonly_fields = ('created_at', 'updated_at', 'verified_at', 'verified_by')
    autocomplete_fields = ['outlet_product', 'period', 'collected_by']
    inlines = [PriceEvidenceInline]
    
    fieldsets = (
        (_('Price Information'), {
            'fields': ('outlet_product', 'period', 'price')
        }),
        (_('Collection Details'), {
            'fields': ('collected_date', 'collected_by', 'status')
        }),
        (_('Verification'), {
            'fields': ('verified_by', 'verified_at')
        }),
        (_('Notes & Rejection'), {
            'fields': ('notes', 'rejection_reason')
        }),
    )
    
    def get_outlet(self, obj):
        return obj.outlet_product.outlet.name
    get_outlet.short_description = _("Outlet")
    
    def get_product(self, obj):
        return obj.outlet_product.product.product_name
    get_product.short_description = _("Product")
    
    actions = ['approve_prices', 'verify_prices', 'reject_prices']
    
    def approve_prices(self, request, queryset):
        queryset.update(status='approved')
    approve_prices.short_description = _("Approve selected prices")
    
    def verify_prices(self, request, queryset):
        queryset.update(status='verified', verified_by=request.user, verified_at=timezone.now())
    verify_prices.short_description = _("Verify selected prices")
    
    def reject_prices(self, request, queryset):
        queryset.update(status='rejected')
    reject_prices.short_description = _("Reject selected prices")


# ====================
# DOCUMENT MANAGEMENT ADMIN
# ====================

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'color_badge')
    list_filter = ('parent',)
    search_fields = ('code', 'name')
    
    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.name
        )
    color_badge.short_description = _("Color")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'document_number', 'title', 'document_type', 
        'status', 'uploaded_by', 'uploaded_at', 'download_count'
    )
    list_filter = (
        'document_type', 'status', 'category', 
        'is_confidential', 'is_public', 'uploaded_at'
    )
    search_fields = ('document_number', 'title', 'description', 'tags')
    readonly_fields = (
        'uploaded_at', 'file_size', 'mime_type', 
        'download_count', 'last_downloaded_at'
    )
    inlines = [DocumentVersionInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'document_number', 'title', 'document_type', 
                'category', 'description', 'tags'
            )
        }),
        (_('File'), {
            'fields': ('file', 'file_size', 'mime_type', 'version')
        }),
        (_('Status & Dates'), {
            'fields': ('status', 'document_date', 'expiry_date')
        }),
        (_('Access Control'), {
            'fields': ('is_confidential', 'is_public', 'allowed_roles')
        }),
        (_('Related Object'), {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        (_('Workflow'), {
            'fields': (
                'uploaded_by', 'uploaded_at',
                'reviewed_by', 'reviewed_at',
                'approved_by', 'approved_at'
            ),
            'classes': ('collapse',)
        }),
        (_('Usage Statistics'), {
            'fields': ('download_count', 'last_downloaded_at'),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
    )


# ====================
# FINANCIAL ADMIN
# ====================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'invoice_type', 'vendor_outlet', 
        'total_amount', 'status', 'invoice_date', 'due_date'
    )
    list_filter = ('invoice_type', 'status', 'invoice_date', 'payment_method')
    search_fields = ('invoice_number', 'vendor_name', 'outlet__name')
    readonly_fields = ('created_at', 'total_amount')
    autocomplete_fields = ['outlet', 'created_by', 'approved_by', 'paid_by']
    
    fieldsets = (
        (_('Invoice Details'), {
            'fields': (
                'invoice_number', 'invoice_type', 
                'outlet', 'vendor_name'
            )
        }),
        (_('Financial Information'), {
            'fields': (
                'amount', 'tax_amount', 'total_amount', 
                'currency', 'items_description'
            )
        }),
        (_('Dates'), {
            'fields': ('invoice_date', 'due_date', 'payment_date')
        }),
        (_('Description'), {
            'fields': ('description',)
        }),
        (_('Status & Payment'), {
            'fields': (
                'status', 'payment_method', 'payment_reference'
            )
        }),
        (_('Attachment'), {
            'fields': ('invoice_file',)
        }),
        (_('Approval Workflow'), {
            'fields': (
                'created_by', 'created_at',
                'approved_by', 'approved_at',
                'paid_by'
            ),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
    )
    
    def vendor_outlet(self, obj):
        return obj.vendor_name or (obj.outlet.name if obj.outlet else '-')
    vendor_outlet.short_description = _("Vendor/Outlet")


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'budget_type', 'fiscal_year', 
        'allocated_amount', 'spent_amount', 'utilization', 'is_active'
    )
    list_filter = ('budget_type', 'fiscal_year', 'is_active', 'department')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'available_amount', 'utilization_percentage')
    
    def utilization(self, obj):
        return f"{obj.utilization_percentage:.1f}%"
    utilization.short_description = _("Utilization")


# ====================
# WORKFLOW ADMIN
# ====================

@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'applies_to', 'is_active')
    list_filter = ('applies_to', 'is_active')
    search_fields = ('code', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'workflow_template', 'current_step', 'status', 
        'initiated_by', 'initiated_at'
    )
    list_filter = ('status', 'workflow_template', 'initiated_at')
    readonly_fields = ('initiated_at', 'completed_at')
    inlines = [ApprovalActionInline]


# ====================
# TRAINING ADMIN
# ====================

@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'title', 'category', 'duration_minutes', 
        'is_mandatory', 'is_active'
    )
    list_filter = ('category', 'is_mandatory', 'is_active')
    search_fields = ('code', 'title', 'description')
    filter_horizontal = ('prerequisites',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserTraining)
class UserTrainingAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'module', 'status', 'score', 
        'started_at', 'completed_at'
    )
    list_filter = ('status', 'module__category')
    search_fields = ('user__username', 'module__title')
    autocomplete_fields = ['user', 'module']


# ====================
# REPORTS & ANALYTICS ADMIN
# ====================

@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'report_type', 'period', 
        'file_format', 'generated_by', 'generated_at', 'download_count'
    )
    list_filter = ('report_type', 'file_format', 'is_public', 'generated_at')
    search_fields = ('title',)
    readonly_fields = ('generated_at', 'file_size', 'download_count')


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'report_type', 'user', 'is_public', 
        'is_scheduled', 'last_run_at'
    )
    list_filter = ('report_type', 'is_public', 'is_scheduled', 'schedule_frequency')
    search_fields = ('name', 'description')


# ====================
# AUDIT & SYSTEM ADMIN
# ====================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name', 'description')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient', 'notification_type', 'title', 
        'is_read', 'created_at'
    )
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at', 'read_at')

