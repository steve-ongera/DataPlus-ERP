# urls.py - URL Configuration

from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    
    # Role-specific Dashboard URLs
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/supervisor/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/data-entry/', views.data_entry_dashboard, name='data_entry_dashboard'),
    path('dashboard/field-officer/', views.field_officer_dashboard, name='field_officer_dashboard'),
    path('dashboard/analyst/', views.analyst_dashboard, name='analyst_dashboard'),
    path('dashboard/accountant/', views.accountant_dashboard, name='accountant_dashboard'),
    path('dashboard/auditor/', views.auditor_dashboard, name='auditor_dashboard'),
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/viewer/', views.viewer_dashboard, name='viewer_dashboard'),
    
    
    # Price Management URLs
    path('prices/', views.PriceEntryListView.as_view(), name='price_entry_list'),
    path('prices/evidence/', views.PriceEvidenceListView.as_view(), name='price_evidence_list'),
    path('prices/periods/', views.PricePeriodListView.as_view(), name='price_period_list'),
    path('prices/outlet-products/', views.OutletProductListView.as_view(), name='outlet_product_list'),
    
    # Outlet Management URLs
    path('outlets/', views.OutletListView.as_view(), name='outlet_list'),
    path('outlets/types/', views.OutletTypeListView.as_view(), name='outlet_type_list'),
    path('zones/', views.ZoneListView.as_view(), name='zone_list'),
    path('baskets/', views.BasketListView.as_view(), name='basket_list'),
    
    # Product Catalog URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/coicop/', views.COICOPCategoryListView.as_view(), name='coicop_category_list'),
    path('products/divisions/', views.DivisionListView.as_view(), name='division_list'),
    
    # Document Management URLs
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('documents/categories/', views.DocumentCategoryListView.as_view(), name='document_category_list'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    #path('contracts/', views.ContractListView.as_view(), name='contract_list'),
    
    # Financial Management URLs
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('financial/payments/', views.PaymentReportView.as_view(), name='payment_report'),
    
    # Workflow & Approvals
    path('workflows/', views.WorkflowListView.as_view(), name='workflow_list'),
    
    # Reports & Analytics
    path('reports/', views.GeneratedReportListView.as_view(), name='report_list'),
    
    # Training
    path('training/', views.TrainingModuleListView.as_view(), name='training_list'),
    path('training/my/', views.UserTrainingListView.as_view(), name='user_training'),
    
    # User Management URLs
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_profile'),
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('roles/', views.RolePermissionView.as_view(), name='role_permissions'),
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_logs'),
    
    # System Configuration URLs
    path('system/config/', views.SystemConfigurationView.as_view(), name='system_configuration'),
    path('system/data-quality/', views.DataQualityCheckListView.as_view(), name='data_quality_checks'),
    path('system/integrations/', views.ExternalIntegrationListView.as_view(), name='external_integrations'),
    path('system/api-keys/', views.APIKeyListView.as_view(), name='api_keys'),
    
    # Other URLs
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('help/', views.HelpSupportView.as_view(), name='help'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('messages/', views.MessageListView.as_view(), name='messages'),
    
    # CRUD Operation URLs (for completeness)
    # Price Entry CRUD
    path('prices/create/', views.PriceEntryCreateView.as_view(), name='price_entry_create'),
    #path('prices/<int:pk>/', views.PriceEntryDetailView.as_view(), name='price_entry_detail'),
    path('prices/<int:pk>/update/', views.PriceEntryUpdateView.as_view(), name='price_entry_update'),
    #path('prices/<int:pk>/delete/', views.PriceEntryDeleteView.as_view(), name='price_entry_delete'),
    
    # Outlet CRUD
    path('outlets/create/', views.OutletCreateView.as_view(), name='outlet_create'),
    # path('outlets/<int:pk>/', views.OutletDetailView.as_view(), name='outlet_detail'),
    # path('outlets/<int:pk>/update/', views.OutletUpdateView.as_view(), name='outlet_update'),
    # path('outlets/<int:pk>/delete/', views.OutletDeleteView.as_view(), name='outlet_delete'),
    
    # Product CRUD
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    # path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    # path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    # path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # User CRUD
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    # path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    # path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Document CRUD
    path('documents/upload/', views.DocumentCreateView.as_view(), name='document_upload'),
    #path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),
    
    # Invoice CRUD
    path('invoices/create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    #path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    
    # Export URLs
    path('export/prices/csv/', views.export_prices_csv, name='export_prices_csv'),
    path('export/outlets/csv/', views.export_outlets_csv, name='export_outlets_csv'),
    #path('export/users/csv/', views.export_users_csv, name='export_users_csv'),
     
]