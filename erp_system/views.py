# views.py - Authentication and Dashboard Views

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from .models import (
    User, PriceEntry, Outlet, PricePeriod, Invoice, 
    Department, Zone, Product, AuditLog, Notification
)


def user_login(request):
    """Custom login view using email instead of username"""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        try:
            # Get user by email
            user = User.objects.get(email=email, is_active=True, is_deleted=False)
            
            # Check if account is locked
            if user.account_locked_until and user.account_locked_until > timezone.now():
                messages.error(request, 'Your account is temporarily locked. Please try again later.')
                return render(request, 'auth/login.html')
            
            # Authenticate using username (Django's default) but we got user by email
            auth_user = authenticate(request, username=user.username, password=password)
            
            if auth_user is not None:
                # Reset failed login attempts
                user.failed_login_attempts = 0
                user.account_locked_until = None
                user.last_login_ip = get_client_ip(request)
                user.save()
                
                # Login user
                login(request, auth_user)
                
                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                # Log the action
                AuditLog.objects.create(
                    user=auth_user,
                    action='login',
                    model_name='User',
                    object_id=auth_user.id,
                    description=f'User {auth_user.email} logged in',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
                )
                
                messages.success(request, f'Welcome back, {auth_user.get_full_name() or auth_user.username}!')
                return redirect('dashboard_redirect')
            else:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = timezone.now() + timedelta(minutes=30)
                    messages.error(request, 'Account locked due to multiple failed login attempts. Please try again in 30 minutes.')
                else:
                    messages.error(request, f'Invalid password. {5 - user.failed_login_attempts} attempts remaining.')
                user.save()
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'auth/login.html')


@login_required
def dashboard_redirect(request):
    """Redirect users to their role-specific dashboard"""
    user = request.user
    
    role_redirects = {
        'super_admin': 'admin_dashboard',
        'admin': 'admin_dashboard',
        'supervisor': 'supervisor_dashboard',
        'data_entry': 'data_entry_dashboard',
        'field_officer': 'field_officer_dashboard',
        'analyst': 'analyst_dashboard',
        'accountant': 'accountant_dashboard',
        'auditor': 'auditor_dashboard',
        'manager': 'manager_dashboard',
        'viewer': 'viewer_dashboard',
    }
    
    dashboard_url = role_redirects.get(user.role, 'viewer_dashboard')
    return redirect(dashboard_url)


@login_required
def user_logout(request):
    """Logout view"""
    # Log the action
    AuditLog.objects.create(
        user=request.user,
        action='logout',
        model_name='User',
        object_id=request.user.id,
        description=f'User {request.user.email} logged out',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
    )
    
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


@login_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive analytics"""
    if request.user.role not in ['super_admin', 'admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard_redirect')
    
    # Get current period
    current_period = PricePeriod.objects.filter(status='open').first()
    
    # Date range for analytics (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # === KEY STATISTICS ===
    total_outlets = Outlet.objects.filter(is_active=True, is_deleted=False).count()
    total_products = Product.objects.filter(is_active=True, is_deleted=False).count()
    total_users = User.objects.filter(is_active=True, is_deleted=False).count()
    
    # Price collection stats
    total_prices_collected = PriceEntry.objects.filter(
        created_at__range=[start_date, end_date]
    ).count()
    
    pending_approvals = PriceEntry.objects.filter(status='submitted').count()
    
    # Financial stats
    total_invoices_amount = Invoice.objects.filter(
        status='approved',
        invoice_date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    pending_payments = Invoice.objects.filter(
        status__in=['pending', 'approved']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # === LINE CHART DATA: Price Collection Trend (Last 30 Days) ===
    price_trend_data = []
    for i in range(30, -1, -1):
        date = (end_date - timedelta(days=i)).date()
        count = PriceEntry.objects.filter(collected_date=date).count()
        price_trend_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # === BAR CHART DATA: Prices by Status ===
    status_data = PriceEntry.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    status_labels = [item['status'].replace('_', ' ').title() for item in status_data]
    status_counts = [item['count'] for item in status_data]
    
    # === DONUT CHART DATA: Outlet Types Distribution ===
    outlet_types = Outlet.objects.filter(
        is_active=True, 
        is_deleted=False
    ).values('outlet_type__name').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    outlet_type_labels = [item['outlet_type__name'] or 'Unknown' for item in outlet_types]
    outlet_type_counts = [item['count'] for item in outlet_types]
    
    # === BAR CHART DATA: Top 10 Zones by Outlet Count ===
    top_zones = Zone.objects.filter(
        is_active=True,
        is_deleted=False
    ).annotate(
        outlet_count=Count('outlets', filter=Q(outlets__is_active=True))
    ).order_by('-outlet_count')[:10]
    
    zone_labels = [zone.name for zone in top_zones]
    zone_counts = [zone.outlet_count for zone in top_zones]
    
    # === DONUT CHART DATA: User Roles Distribution ===
    user_roles = User.objects.filter(
        is_active=True,
        is_deleted=False
    ).values('role').annotate(
        count=Count('id')
    ).order_by('-count')
    
    role_labels = [
    str(dict(User.ROLE_CHOICES).get(item['role'], item['role']))
    for item in user_roles
    ]

    role_counts = [item['count'] for item in user_roles]
    
    # === LINE CHART DATA: Invoice Trends (Monthly) ===
    invoice_trend = []
    for i in range(6, -1, -1):
        month_start = (end_date - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        amount = Invoice.objects.filter(
            invoice_date__range=[month_start, month_end],
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        invoice_trend.append({
            'month': month_start.strftime('%b %Y'),
            'amount': float(amount)
        })
    
    # === RECENT ACTIVITIES ===
    recent_activities = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    # === PENDING APPROVALS ===
    pending_price_entries = PriceEntry.objects.filter(
        status='submitted'
    ).select_related('outlet_product__outlet', 'outlet_product__product', 'collected_by')[:10]
    
    # === UNREAD NOTIFICATIONS ===
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'total_outlets': total_outlets,
        'total_products': total_products,
        'total_users': total_users,
        'total_prices_collected': total_prices_collected,
        'pending_approvals': pending_approvals,
        'total_invoices_amount': total_invoices_amount,
        'pending_payments': pending_payments,
        
        # Chart data
        'price_trend_data': json.dumps(price_trend_data),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'outlet_type_labels': json.dumps(outlet_type_labels),
        'outlet_type_counts': json.dumps(outlet_type_counts),
        'zone_labels': json.dumps(zone_labels),
        'zone_counts': json.dumps(zone_counts),
        'role_labels': json.dumps(role_labels),
        'role_counts': json.dumps(role_counts),
        'invoice_trend': json.dumps(invoice_trend),
        
        # Recent data
        'recent_activities': recent_activities,
        'pending_price_entries': pending_price_entries,
        'unread_notifications': unread_notifications,
        'current_period': current_period,
    }
    
    return render(request, 'dashboard/admin.html', context)


# Helper function to get client IP
def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Additional role-specific dashboard views (simplified versions)
@login_required
def supervisor_dashboard(request):
    """Supervisor dashboard"""
    # Add supervisor-specific logic here
    return render(request, 'dashboard/supervisor.html', {})


@login_required
def data_entry_dashboard(request):
    """Data entry dashboard"""
    # Add data entry-specific logic here
    return render(request, 'dashboard/data_entry.html', {})


@login_required
def field_officer_dashboard(request):
    """Field officer dashboard"""
    # Add field officer-specific logic here
    return render(request, 'dashboard/field_officer.html', {})


@login_required
def analyst_dashboard(request):
    """Analyst dashboard"""
    # Add analyst-specific logic here
    return render(request, 'dashboard/analyst.html', {})


@login_required
def accountant_dashboard(request):
    """Accountant dashboard"""
    # Add accountant-specific logic here
    return render(request, 'dashboard/accountant.html', {})


@login_required
def auditor_dashboard(request):
    """Auditor dashboard"""
    # Add auditor-specific logic here
    return render(request, 'dashboard/auditor.html', {})


@login_required
def manager_dashboard(request):
    """Manager dashboard"""
    # Add manager-specific logic here
    return render(request, 'dashboard/manager.html', {})


@login_required
def viewer_dashboard(request):
    """Viewer dashboard"""
    # Add viewer-specific logic here
    return render(request, 'dashboard/viewer.html', {})



from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from .models import *
import csv

# ====================
# DASHBOARD VIEWS
# ====================

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_prices'] = PriceEntry.objects.filter(status='approved').order_by('-collected_date')[:10]
        context['pending_approvals'] = PriceEntry.objects.filter(status='submitted').count()
        context['active_periods'] = PricePeriod.objects.filter(status='open')
        return context

# ====================
# PRICE MANAGEMENT VIEWS
# ====================

class PriceEntryListView(LoginRequiredMixin, ListView):
    model = PriceEntry
    template_name = 'prices/priceentry_list.html'
    paginate_by = 20
    ordering = ['-collected_date']

class PriceEvidenceListView(LoginRequiredMixin, ListView):
    model = PriceEvidence
    template_name = 'prices/evidence_list.html'

class PricePeriodListView(LoginRequiredMixin, ListView):
    model = PricePeriod
    template_name = 'prices/period_list.html'

class OutletProductListView(LoginRequiredMixin, ListView):
    model = OutletProduct
    template_name = 'prices/outletproduct_list.html'

# ====================
# OUTLET MANAGEMENT VIEWS
# ====================

class OutletListView(LoginRequiredMixin, ListView):
    model = Outlet
    template_name = 'outlets/outlet_list.html'
    paginate_by = 25

class OutletTypeListView(LoginRequiredMixin, ListView):
    model = OutletType
    template_name = 'outlets/type_list.html'

class ZoneListView(LoginRequiredMixin, ListView):
    model = Zone
    template_name = 'outlets/zone_list.html'

class BasketListView(LoginRequiredMixin, ListView):
    model = Basket
    template_name = 'outlets/basket_list.html'

# ====================
# PRODUCT CATALOG VIEWS
# ====================

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    paginate_by = 30

class COICOPCategoryListView(LoginRequiredMixin, ListView):
    model = COICOPCategory
    template_name = 'products/coicop_list.html'

class DivisionListView(LoginRequiredMixin, ListView):
    model = Division
    template_name = 'products/division_list.html'

# ====================
# DOCUMENT MANAGEMENT VIEWS
# ====================

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    paginate_by = 20

class DocumentCategoryListView(LoginRequiredMixin, ListView):
    model = DocumentCategory
    template_name = 'documents/category_list.html'

# ====================
# FINANCIAL MANAGEMENT VIEWS
# ====================

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'financial/invoice_list.html'

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'financial/budget_list.html'

class PaymentReportView(LoginRequiredMixin, TemplateView):
    template_name = 'financial/payment_report.html'

# ====================
# WORKFLOW VIEWS
# ====================

class WorkflowListView(LoginRequiredMixin, ListView):
    model = WorkflowInstance
    template_name = 'workflows/workflow_list.html'

# ====================
# REPORTS VIEWS
# ====================

class GeneratedReportListView(LoginRequiredMixin, ListView):
    model = GeneratedReport
    template_name = 'reports/report_list.html'

# ====================
# TRAINING VIEWS
# ====================

class TrainingModuleListView(LoginRequiredMixin, ListView):
    model = TrainingModule
    template_name = 'training/module_list.html'

class UserTrainingListView(LoginRequiredMixin, ListView):
    model = UserTraining
    template_name = 'training/user_training.html'
    
    def get_queryset(self):
        return UserTraining.objects.filter(user=self.request.user)

# ====================
# USER MANAGEMENT VIEWS
# ====================

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    paginate_by = 25

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'

class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'users/department_list.html'

class RolePermissionView(LoginRequiredMixin, TemplateView):
    template_name = 'users/role_permissions.html'

class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'users/audit_log.html'
    paginate_by = 50

# ====================
# SYSTEM CONFIGURATION VIEWS
# ====================

class SystemConfigurationView(LoginRequiredMixin, TemplateView):
    template_name = 'system/configuration.html'

class DataQualityCheckListView(LoginRequiredMixin, ListView):
    model = DataQualityCheck
    template_name = 'system/data_quality.html'

class ExternalIntegrationListView(LoginRequiredMixin, ListView):
    model = ExternalIntegration
    template_name = 'system/integrations.html'

class APIKeyListView(LoginRequiredMixin, ListView):
    model = APIKey
    template_name = 'system/api_keys.html'

# ====================
# OTHER VIEWS
# ====================

class UserSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'settings/user_settings.html'

class HelpSupportView(LoginRequiredMixin, TemplateView):
    template_name = 'help/help_support.html'

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class MessageListView(LoginRequiredMixin, TemplateView):
    template_name = 'messages/message_list.html'

# ====================
# CRUD VIEWS
# ====================

class PriceEntryCreateView(LoginRequiredMixin, CreateView):
    model = PriceEntry
    template_name = 'prices/priceentry_form.html'
    fields = ['outlet_product', 'period', 'price', 'collected_date', 'notes']
    success_url = reverse_lazy('price_entry_list')

class PriceEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = PriceEntry
    template_name = 'prices/priceentry_form.html'
    fields = ['price', 'status', 'notes']
    success_url = reverse_lazy('price_entry_list')

class OutletCreateView(LoginRequiredMixin, CreateView):
    model = Outlet
    template_name = 'outlets/outlet_form.html'
    fields = '__all__'
    success_url = reverse_lazy('outlet_list')

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    fields = '__all__'
    success_url = reverse_lazy('product_list')

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    template_name = 'users/user_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'role', 'department']
    success_url = reverse_lazy('user_list')

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    template_name = 'documents/document_form.html'
    fields = ['title', 'document_type', 'category', 'file', 'description']
    success_url = reverse_lazy('document_list')
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    template_name = 'financial/invoice_form.html'
    fields = ['invoice_type', 'outlet', 'amount', 'description', 'invoice_date']
    success_url = reverse_lazy('invoice_list')

# ====================
# EXPORT VIEWS
# ====================

@login_required
def export_prices_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="prices_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Outlet', 'Product', 'Price', 'Period', 'Collected Date', 'Status'])
    
    prices = PriceEntry.objects.filter(status='approved')[:1000]
    for price in prices:
        writer.writerow([
            price.outlet_product.outlet.name,
            price.outlet_product.product.product_name,
            price.price,
            price.period.period_name,
            price.collected_date,
            price.get_status_display()
        ])
    
    return response

@login_required
def export_outlets_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="outlets_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Outlet Code', 'Name', 'Type', 'Zone', 'Contact Person', 'Phone', 'Status'])
    
    outlets = Outlet.objects.filter(is_active=True)[:1000]
    for outlet in outlets:
        writer.writerow([
            outlet.outlet_code,
            outlet.name,
            outlet.outlet_type.name,
            outlet.zone.name,
            outlet.contact_person,
            outlet.contact_phone,
            outlet.verification_status
        ])
    
    return response

@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    document.download_count += 1
    document.save()
    
    response = HttpResponse(document.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{document.title}.{document.file.name.split(".")[-1]}"'
    return response