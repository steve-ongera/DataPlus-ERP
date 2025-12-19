"""
Django Management Command: seed_data.py
Location: erp_system/management/commands/seed_data.py

Generates comprehensive seed data for DataPlus ERP system with wide time range
for statistical analysis and testing purposes.

Usage:
    python manage.py seed_data
    python manage.py seed_data --years 5
    python manage.py seed_data --clear (clears existing data first)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from erp_system.models import (
    Department, User, Basket, Zone, OutletType, Outlet,
    Division, COICOPCategory, Product, PricePeriod, OutletProduct,
    PriceEntry, DocumentCategory, Document, Invoice, Budget,
    WorkflowTemplate, TrainingModule, SystemConfiguration,
    DataQualityCheck
)
from datetime import datetime, timedelta, date
from decimal import Decimal
import random
import string


class Command(BaseCommand):
    help = 'Seeds the database with comprehensive test data spanning multiple years'

    def add_arguments(self, parser):
        parser.add_argument(
            '--years',
            type=int,
            default=1,
            help='Number of years of historical data to generate (default: 1)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        years = options['years']
        clear_data = options['clear']

        self.stdout.write(self.style.WARNING(
            f'Starting seed data generation for {years} years...'
        ))

        try:
            with transaction.atomic():
                if clear_data:
                    self.clear_data()

                # Seed data in logical order
                self.seed_departments()
                self.seed_users()
                self.seed_baskets()
                self.seed_zones()
                self.seed_outlet_types()
                self.seed_outlets()
                self.seed_divisions()
                self.seed_coicop_categories()
                self.seed_products()
                self.seed_price_periods(years)
                self.seed_outlet_products()
                self.seed_price_entries(years)
                self.seed_document_categories()
                self.seed_documents()
                self.seed_invoices(years)
                self.seed_budgets(years)
                self.seed_workflow_templates()
                self.seed_training_modules()
                self.seed_system_configuration()
                self.seed_data_quality_checks()

                self.stdout.write(self.style.SUCCESS(
                    f'\n✓ Successfully seeded database with {years} years of data!'
                ))
                self.print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error: {str(e)}'))
            raise

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        
        # Clear in reverse order of dependencies
        PriceEntry.objects.all().delete()
        OutletProduct.objects.all().delete()
        PricePeriod.objects.all().delete()
        Product.objects.all().delete()
        COICOPCategory.objects.all().delete()
        Division.objects.all().delete()
        Outlet.objects.all().delete()
        OutletType.objects.all().delete()
        Zone.objects.all().delete()
        Basket.objects.all().delete()
        Invoice.objects.all().delete()
        Budget.objects.all().delete()
        Document.objects.all().delete()
        DocumentCategory.objects.all().delete()
        WorkflowTemplate.objects.all().delete()
        TrainingModule.objects.all().delete()
        DataQualityCheck.objects.all().delete()
        SystemConfiguration.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

    def seed_departments(self):
        """Seed departments"""
        self.stdout.write('Seeding departments...')
        
        departments_data = [
            {'name': 'Executive Management', 'code': 'EXEC', 'description': 'Executive leadership and strategic planning'},
            {'name': 'Data Collection', 'code': 'DATA', 'description': 'Field data collection operations'},
            {'name': 'Data Analysis', 'code': 'ANLYS', 'description': 'Statistical analysis and research'},
            {'name': 'Finance', 'code': 'FIN', 'description': 'Financial management and accounting'},
            {'name': 'IT & Systems', 'code': 'IT', 'description': 'Information technology and systems'},
            {'name': 'Human Resources', 'code': 'HR', 'description': 'Human resource management'},
            {'name': 'Procurement', 'code': 'PROC', 'description': 'Procurement and supply chain'},
            {'name': 'Quality Assurance', 'code': 'QA', 'description': 'Quality control and validation'},
        ]
        
        for dept_data in departments_data:
            dept_data['budget'] = Decimal(random.randint(500000, 5000000))
            Department.objects.create(**dept_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(departments_data)} departments'))

    def seed_users(self):
        """Seed users with various roles"""
        self.stdout.write('Seeding users...')
        
        departments = list(Department.objects.all())
        roles = ['super_admin', 'admin', 'supervisor', 'data_entry', 'field_officer', 
                 'analyst', 'accountant', 'auditor', 'manager', 'viewer']
        
        users_data = [
            # Super Admin
            {
                'username': 'admin',
                'email': 'admin@dataplus.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'employee_id': 'EMP001',
                'role': 'super_admin',
                'is_staff': True,
                'is_superuser': True,
                'can_approve_prices': True,
                'can_generate_reports': True,
                'can_export_data': True,
                'can_manage_users': True,
                'can_manage_finances': True,
            },
            # Regional Managers
            {
                'username': 'james.mwangi',
                'email': 'james.mwangi@dataplus.com',
                'first_name': 'James',
                'last_name': 'Mwangi',
                'employee_id': 'EMP002',
                'role': 'manager',
                'phone_number': '+254712345001',
                'can_approve_prices': True,
                'can_generate_reports': True,
            },
            {
                'username': 'sarah.akinyi',
                'email': 'sarah.akinyi@dataplus.com',
                'first_name': 'Sarah',
                'last_name': 'Akinyi',
                'employee_id': 'EMP003',
                'role': 'manager',
                'phone_number': '+254712345002',
                'can_approve_prices': True,
                'can_generate_reports': True,
            },
            # Supervisors
            {
                'username': 'peter.kamau',
                'email': 'peter.kamau@dataplus.com',
                'first_name': 'Peter',
                'last_name': 'Kamau',
                'employee_id': 'EMP004',
                'role': 'supervisor',
                'phone_number': '+254712345003',
                'can_approve_prices': True,
            },
            {
                'username': 'mary.njeri',
                'email': 'mary.njeri@dataplus.com',
                'first_name': 'Mary',
                'last_name': 'Njeri',
                'employee_id': 'EMP005',
                'role': 'supervisor',
                'phone_number': '+254712345004',
                'can_approve_prices': True,
            },
            # Analysts
            {
                'username': 'david.ochieng',
                'email': 'david.ochieng@dataplus.com',
                'first_name': 'David',
                'last_name': 'Ochieng',
                'employee_id': 'EMP006',
                'role': 'analyst',
                'phone_number': '+254712345005',
                'can_generate_reports': True,
                'can_export_data': True,
            },
            {
                'username': 'grace.wanjiru',
                'email': 'grace.wanjiru@dataplus.com',
                'first_name': 'Grace',
                'last_name': 'Wanjiru',
                'employee_id': 'EMP007',
                'role': 'analyst',
                'phone_number': '+254712345006',
                'can_generate_reports': True,
                'can_export_data': True,
            },
        ]
        
        # Add field officers
        first_names = ['John', 'Jane', 'Michael', 'Lucy', 'Daniel', 'Faith', 'Patrick', 'Ann']
        last_names = ['Kipchoge', 'Wambui', 'Otieno', 'Mutua', 'Kimani', 'Adhiambo', 'Mulei', 'Chebet']
        
        for i in range(8, 28):  # 20 field officers
            users_data.append({
                'username': f'field.officer{i}',
                'email': f'field{i}@dataplus.com',
                'first_name': random.choice(first_names),
                'last_name': random.choice(last_names),
                'employee_id': f'EMP{str(i).zfill(3)}',
                'role': 'field_officer',
                'phone_number': f'+2547123450{str(i).zfill(2)}',
            })
        
        # Create users
        created_users = []
        for user_data in users_data:
            user_data['password'] = make_password('password123')
            user_data['department'] = random.choice(departments)
            user_data['date_joined_company'] = date.today() - timedelta(days=random.randint(365, 1825))
            user_data['gender'] = random.choice(['M', 'F'])
            user_data['salary'] = Decimal(random.randint(30000, 150000))
            
            user = User.objects.create(**user_data)
            created_users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(created_users)} users'))
        return created_users

    def seed_baskets(self):
        """Seed baskets (top-level geographical grouping)"""
        self.stdout.write('Seeding baskets...')
        
        users = list(User.objects.filter(role__in=['manager', 'supervisor']))
        
        baskets_data = [
            {'name': 'Nairobi Metropolitan', 'code': 'NRB', 'description': 'Nairobi and surrounding areas'},
            {'name': 'Central Region', 'code': 'CEN', 'description': 'Central Kenya region'},
            {'name': 'Coast Region', 'code': 'CST', 'description': 'Coastal region'},
            {'name': 'Western Region', 'code': 'WST', 'description': 'Western Kenya region'},
            {'name': 'Rift Valley', 'code': 'RFT', 'description': 'Rift Valley region'},
            {'name': 'Eastern Region', 'code': 'EST', 'description': 'Eastern Kenya region'},
        ]
        
        admin_user = User.objects.filter(role='super_admin').first()
        
        for basket_data in baskets_data:
            basket_data['coordinator'] = random.choice(users) if users else admin_user
            basket_data['annual_budget'] = Decimal(random.randint(5000000, 20000000))
            basket_data['target_outlets'] = random.randint(50, 200)
            basket_data['created_by'] = admin_user
            Basket.objects.create(**basket_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(baskets_data)} baskets'))

    def seed_zones(self):
        """Seed zones within baskets"""
        self.stdout.write('Seeding zones...')
        
        baskets = Basket.objects.all()
        supervisors = list(User.objects.filter(role__in=['supervisor', 'manager']))
        admin_user = User.objects.filter(role='super_admin').first()
        
        counties = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Machakos', 
                   'Kiambu', 'Nyeri', 'Meru', 'Kisii', 'Kakamega', 'Garissa']
        
        zone_counter = 1
        for basket in baskets:
            for i in range(random.randint(3, 6)):  # 3-6 zones per basket
                Zone.objects.create(
                    basket=basket,
                    name=f'{basket.name} Zone {i+1}',
                    zone_code=f'{basket.code}Z{str(zone_counter).zfill(3)}',
                    region=basket.name,
                    county=random.choice(counties),
                    supervisor=random.choice(supervisors) if supervisors else None,
                    latitude=Decimal(str(random.uniform(-4.5, 4.5))),
                    longitude=Decimal(str(random.uniform(33.5, 42.0))),
                    created_by=admin_user
                )
                zone_counter += 1
        
        zone_count = Zone.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {zone_count} zones'))

    def seed_outlet_types(self):
        """Seed outlet types"""
        self.stdout.write('Seeding outlet types...')
        
        admin_user = User.objects.filter(role='super_admin').first()
        
        outlet_types_data = [
            {'code': 'SPMKT', 'name': 'Supermarket', 'description': 'Large retail supermarket', 
             'category': 'Retail', 'is_formal': True, 'requires_license': True, 'min_items': 50, 'max_items': 500},
            {'code': 'MINI', 'name': 'Mini Market', 'description': 'Small retail shop', 
             'category': 'Retail', 'is_formal': True, 'requires_license': True, 'min_items': 20, 'max_items': 200},
            {'code': 'KIOSK', 'name': 'Kiosk', 'description': 'Small kiosk or stall', 
             'category': 'Retail', 'is_formal': False, 'requires_license': False, 'min_items': 10, 'max_items': 100},
            {'code': 'PHARM', 'name': 'Pharmacy', 'description': 'Pharmaceutical outlet', 
             'category': 'Healthcare', 'is_formal': True, 'requires_license': True, 'min_items': 30, 'max_items': 300},
            {'code': 'REST', 'name': 'Restaurant', 'description': 'Food service establishment', 
             'category': 'Food Service', 'is_formal': True, 'requires_license': True, 'min_items': 15, 'max_items': 150},
            {'code': 'HOTEL', 'name': 'Hotel', 'description': 'Accommodation facility', 
             'category': 'Hospitality', 'is_formal': True, 'requires_license': True, 'min_items': 25, 'max_items': 250},
            {'code': 'WHLSL', 'name': 'Wholesale', 'description': 'Wholesale distributor', 
             'category': 'Wholesale', 'is_formal': True, 'requires_license': True, 'min_items': 100, 'max_items': 1000},
            {'code': 'MARKET', 'name': 'Open Market', 'description': 'Open air market vendor', 
             'category': 'Market', 'is_formal': False, 'requires_license': False, 'min_items': 5, 'max_items': 50},
        ]
        
        for ot_data in outlet_types_data:
            ot_data['created_by'] = admin_user
            OutletType.objects.create(**ot_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(outlet_types_data)} outlet types'))

    def seed_outlets(self):
        """Seed outlets across zones"""
        self.stdout.write('Seeding outlets...')
        
        zones = Zone.objects.all()
        outlet_types = list(OutletType.objects.all())
        field_officers = list(User.objects.filter(role='field_officer'))
        admin_user = User.objects.filter(role='super_admin').first()
        
        outlet_names = [
            'Naivas', 'Quickmart', 'Carrefour', 'Tuskys', 'Chandarana', 'Eastmatt',
            'Metro Supermarket', 'City Market', 'Fresh Foods', 'Value Store',
            'Junction Mall', 'Prestige Plaza', 'Town Center', 'Main Street',
            'Central Business', 'Shopping Complex', 'Trade Center'
        ]
        
        verification_statuses = ['verified', 'verified', 'verified', 'pending']
        
        outlet_counter = 1
        for zone in zones:
            num_outlets = random.randint(10, 25)  # 10-25 outlets per zone
            
            for i in range(num_outlets):
                outlet_type = random.choice(outlet_types)
                
                Outlet.objects.create(
                    zone=zone,
                    outlet_type=outlet_type,
                    outlet_number=f'OUT{str(outlet_counter).zfill(5)}',
                    outlet_code=f'{zone.zone_code}O{str(i+1).zfill(3)}',
                    name=f'{random.choice(outlet_names)} - {zone.name}',
                    address=f'{random.randint(1, 999)} Main Street, {zone.county}',
                    contact_person=f'Manager {i+1}',
                    contact_phone=f'+2547{random.randint(10000000, 99999999)}',
                    contact_email=f'outlet{outlet_counter}@example.com',
                    business_registration_number=f'BRN{random.randint(100000, 999999)}',
                    max_items=outlet_type.max_items,
                    opening_hours='8:00 AM - 8:00 PM',
                    operating_days='Monday - Sunday',
                    average_monthly_revenue=Decimal(random.randint(100000, 5000000)),
                    assigned_officer=random.choice(field_officers) if field_officers else None,
                    latitude=Decimal(str(random.uniform(-4.5, 4.5))),
                    longitude=Decimal(str(random.uniform(33.5, 42.0))),
                    verification_status=random.choice(verification_statuses),
                    last_visited_date=date.today() - timedelta(days=random.randint(1, 90)),
                    created_by=admin_user
                )
                outlet_counter += 1
        
        outlet_count = Outlet.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {outlet_count} outlets'))

    def seed_divisions(self):
        """Seed product divisions"""
        self.stdout.write('Seeding divisions...')
        
        admin_user = User.objects.filter(role='super_admin').first()
        
        divisions_data = [
            {'code': '01', 'name': 'Food and Non-Alcoholic Beverages', 'name_local': 'Chakula na Vinywaji', 'sort_order': 1},
            {'code': '02', 'name': 'Alcoholic Beverages and Tobacco', 'name_local': 'Pombe na Tumbaku', 'sort_order': 2},
            {'code': '03', 'name': 'Clothing and Footwear', 'name_local': 'Nguo na Viatu', 'sort_order': 3},
            {'code': '04', 'name': 'Housing, Water, Electricity, Gas and Other Fuels', 'name_local': 'Nyumba na Nishati', 'sort_order': 4},
            {'code': '05', 'name': 'Furnishings, Household Equipment', 'name_local': 'Samani za Nyumbani', 'sort_order': 5},
            {'code': '06', 'name': 'Health', 'name_local': 'Afya', 'sort_order': 6},
            {'code': '07', 'name': 'Transport', 'name_local': 'Usafiri', 'sort_order': 7},
            {'code': '08', 'name': 'Communication', 'name_local': 'Mawasiliano', 'sort_order': 8},
            {'code': '09', 'name': 'Recreation and Culture', 'name_local': 'Burudani na Utamaduni', 'sort_order': 9},
            {'code': '10', 'name': 'Education', 'name_local': 'Elimu', 'sort_order': 10},
            {'code': '11', 'name': 'Restaurants and Hotels', 'name_local': 'Migahawa na Hoteli', 'sort_order': 11},
            {'code': '12', 'name': 'Miscellaneous Goods and Services', 'name_local': 'Bidhaa na Huduma Mbalimbali', 'sort_order': 12},
        ]
        
        for div_data in divisions_data:
            div_data['created_by'] = admin_user
            Division.objects.create(**div_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(divisions_data)} divisions'))

    def seed_coicop_categories(self):
        """Seed COICOP categories"""
        self.stdout.write('Seeding COICOP categories...')
        
        divisions = Division.objects.all()
        admin_user = User.objects.filter(role='super_admin').first()
        
        # Sample categories for each division
        for division in divisions:
            for i in range(5):  # 5 categories per division
                COICOPCategory.objects.create(
                    division=division,
                    new_coicop=f'{division.code}.{str(i+1).zfill(2)}',
                    old_coicop=f'OLD{division.code}{i+1}',
                    coicop_26=f'C26{division.code}{i+1}',
                    description=f'Category {i+1} for {division.name}',
                    level=2,
                    created_by=admin_user
                )
        
        category_count = COICOPCategory.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {category_count} COICOP categories'))

    def seed_products(self):
        """Seed products"""
        self.stdout.write('Seeding products...')
        
        categories = COICOPCategory.objects.all()
        admin_user = User.objects.filter(role='super_admin').first()
        
        # Common product templates
        product_templates = [
            {'name': 'Rice', 'unit': 'Kg', 'quantity': 1, 'price_range': (80, 200)},
            {'name': 'Maize Flour', 'unit': 'Kg', 'quantity': 2, 'price_range': (100, 180)},
            {'name': 'Wheat Flour', 'unit': 'Kg', 'quantity': 2, 'price_range': (120, 200)},
            {'name': 'Sugar', 'unit': 'Kg', 'quantity': 1, 'price_range': (120, 180)},
            {'name': 'Cooking Oil', 'unit': 'Ltr', 'quantity': 1, 'price_range': (200, 400)},
            {'name': 'Milk', 'unit': 'Ltr', 'quantity': 1, 'price_range': (50, 120)},
            {'name': 'Bread', 'unit': 'Pcs', 'quantity': 1, 'price_range': (40, 80)},
            {'name': 'Tea Leaves', 'unit': 'Grams', 'quantity': 250, 'price_range': (80, 200)},
            {'name': 'Salt', 'unit': 'Kg', 'quantity': 1, 'price_range': (30, 60)},
            {'name': 'Tomatoes', 'unit': 'Kg', 'quantity': 1, 'price_range': (40, 120)},
        ]
        
        brands = ['Premium', 'Quality', 'Fresh', 'Super', 'Best', 'Top', 'Choice', 'Select']
        
        product_counter = 1
        for category in categories[:20]:  # Limit to first 20 categories for reasonable data size
            for template in product_templates[:random.randint(5, 10)]:
                brand = random.choice(brands)
                
                Product.objects.create(
                    coicop_category=category,
                    item_code=f'ITM{str(product_counter).zfill(5)}',
                    barcode=f'{random.randint(1000000000000, 9999999999999)}',
                    product_name=f'{brand} {template["name"]}',
                    specification=f'{template["quantity"]} {template["unit"]} pack',
                    brand=brand,
                    unit_of_measurement=template['unit'],
                    quantity=Decimal(str(template['quantity'])),
                    reference_price=Decimal(str(random.uniform(*template['price_range']))),
                    min_expected_price=Decimal(str(template['price_range'][0] * 0.8)),
                    max_expected_price=Decimal(str(template['price_range'][1] * 1.2)),
                    is_seasonal=random.choice([False, False, False, True]),
                    created_by=admin_user
                )
                product_counter += 1
        
        product_count = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {product_count} products'))

    def seed_price_periods(self, years):
        """Seed price periods spanning multiple years"""
        self.stdout.write(f'Seeding price periods for {years} years...')
        
        admin_user = User.objects.filter(role='super_admin').first()
        current_date = date.today()
        start_date = current_date - timedelta(days=years * 365)
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        period_date = start_date.replace(day=1)
        statuses = ['closed', 'closed', 'closed', 'open']
        
        while period_date <= current_date:
            year = period_date.year
            month = period_date.month
            
            # Calculate period dates
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            # Determine status based on how recent the period is
            months_ago = (current_date.year - year) * 12 + (current_date.month - month)
            if months_ago > 2:
                status = 'closed'
            elif months_ago == 1:
                status = 'review'
            else:
                status = 'open'
            
            PricePeriod.objects.create(
                year=year,
                month=month,
                period_name=f'{month_names[month-1]} {year}',
                start_date=period_date,
                end_date=end_date,
                status=status,
                target_outlets=random.randint(400, 600),
                target_prices=random.randint(5000, 8000),
                collected_prices=random.randint(4500, 7500) if status == 'closed' else random.randint(2000, 5000),
                approved_prices=random.randint(4000, 7000) if status == 'closed' else random.randint(1500, 4000),
                allocated_budget=Decimal(random.randint(1000000, 3000000)),
                created_by=admin_user,
                closed_at=datetime.now() if status == 'closed' else None,
                closed_by=admin_user if status == 'closed' else None
            )
            
            # Move to next month
            if month == 12:
                period_date = date(year + 1, 1, 1)
            else:
                period_date = date(year, month + 1, 1)
        
        period_count = PricePeriod.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {period_count} price periods'))

    def seed_outlet_products(self):
        """Seed outlet-product relationships"""
        self.stdout.write('Seeding outlet-product relationships...')
        
        outlets = Outlet.objects.filter(is_active=True)
        products = list(Product.objects.all())
        admin_user = User.objects.filter(role='super_admin').first()
        
        availability_statuses = ['regular', 'regular', 'regular', 'seasonal']
        
        created_count = 0
        for outlet in outlets:
            # Each outlet carries 30-80% of available products
            num_products = int(len(products) * random.uniform(0.3, 0.8))
            selected_products = random.sample(products, num_products)
            
            for idx, product in enumerate(selected_products, 1):
                OutletProduct.objects.create(
                    outlet=outlet,
                    product=product,
                    item_number=idx,
                    is_available=random.choice([True, True, True, False]),
                    availability_status=random.choice(availability_statuses),
                    last_seen_date=date.today() - timedelta(days=random.randint(1, 60)),
                    last_price_date=date.today() - timedelta(days=random.randint(1, 90)),
                    created_by=admin_user
                )
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} outlet-product relationships'))

    def seed_price_entries(self, years):
        """Seed price entries with realistic variations over time"""
        self.stdout.write(f'Seeding price entries for {years} years...')
        
        periods = PricePeriod.objects.all().order_by('year', 'month')
        outlet_products = OutletProduct.objects.filter(is_available=True)
        field_officers = list(User.objects.filter(role='field_officer'))
        supervisors = list(User.objects.filter(role__in=['supervisor', 'manager']))
        
        if not field_officers:
            field_officers = [User.objects.filter(role='super_admin').first()]
        
        statuses_with_weights = [
            ('approved', 70),
            ('verified', 15),
            ('submitted', 10),
            ('draft', 5),
        ]
        
        created_count = 0
        for period in periods:
            # Sample 60-90% of outlet products for each period
            sample_size = int(len(outlet_products) * random.uniform(0.6, 0.9))
            sampled_ops = random.sample(list(outlet_products), min(sample_size, len(outlet_products)))
            
            for op in sampled_ops:
                # Calculate price with inflation and seasonal variation
                base_price = op.product.reference_price or Decimal('100')
                
                # Add inflation (2-8% per year)
                years_passed = period.year - (date.today().year - years)
                inflation_rate = Decimal(str(random.uniform(0.02, 0.08) * years_passed))
                inflated_price = base_price * (1 + inflation_rate)
                
                # Add seasonal variation (-10% to +15%)
                seasonal_factor = Decimal(str(random.uniform(0.9, 1.15)))
                final_price = inflated_price * seasonal_factor
                
                # Random variation (-5% to +5%)
                final_price *= Decimal(str(random.uniform(0.95, 1.05)))
                
                # Round to 2 decimal places
                final_price = final_price.quantize(Decimal('0.01'))
                
                # Weighted random status
                status = random.choices(
                    [s[0] for s in statuses_with_weights],
                    weights=[s[1] for s in statuses_with_weights]
                )[0]
                
                collected_by = random.choice(field_officers)
                collected_date = period.start_date + timedelta(days=random.randint(0, 25))
                
                price_entry = PriceEntry.objects.create(
                    outlet_product=op,
                    period=period,
                    price=final_price,
                    status=status,
                    collected_date=collected_date,
                    collected_by=collected_by,
                )
                
                # Add verification for approved/verified entries
                if status in ['approved', 'verified']:
                    price_entry.verified_by = random.choice(supervisors) if supervisors else collected_by
                    price_entry.verified_at = datetime.now()
                    price_entry.save()
                
                created_count += 1
                
                if created_count % 1000 == 0:
                    self.stdout.write(f'  Created {created_count} price entries...')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} price entries'))

    def seed_document_categories(self):
        """Seed document categories"""
        self.stdout.write('Seeding document categories...')
        
        categories_data = [
            {'name': 'Invoices', 'code': 'INV', 'description': 'Invoice documents', 'icon': 'receipt', 'color': '#3498db'},
            {'name': 'Contracts', 'code': 'CNT', 'description': 'Contract documents', 'icon': 'file-contract', 'color': '#2ecc71'},
            {'name': 'Reports', 'code': 'RPT', 'description': 'Generated reports', 'icon': 'chart-bar', 'color': '#e74c3c'},
            {'name': 'Policies', 'code': 'POL', 'description': 'Policy documents', 'icon': 'book', 'color': '#9b59b6'},
            {'name': 'Certificates', 'code': 'CRT', 'description': 'Certificates and licenses', 'icon': 'certificate', 'color': '#f39c12'},
            {'name': 'Evidence', 'code': 'EVD', 'description': 'Price evidence photos', 'icon': 'camera', 'color': '#1abc9c'},
        ]
        
        for cat_data in categories_data:
            DocumentCategory.objects.create(**cat_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories_data)} document categories'))

    def seed_documents(self):
        """Seed sample documents"""
        self.stdout.write('Seeding documents...')
        
        categories = DocumentCategory.objects.all()
        users = list(User.objects.all())
        admin_user = User.objects.filter(role='super_admin').first()
        
        doc_counter = 1
        for category in categories:
            for i in range(random.randint(10, 30)):
                Document.objects.create(
                    title=f'{category.name} Document {i+1}',
                    document_number=f'DOC{str(doc_counter).zfill(6)}',
                    document_type=category.code.lower(),
                    category=category,
                    file_size=random.randint(10000, 5000000),
                    mime_type='application/pdf',
                    description=f'Sample document for {category.name}',
                    version='1.0',
                    status=random.choice(['approved', 'approved', 'pending_review']),
                    document_date=date.today() - timedelta(days=random.randint(1, 730)),
                    uploaded_by=random.choice(users),
                    is_confidential=random.choice([False, False, False, True]),
                )
                doc_counter += 1
        
        doc_count = Document.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {doc_count} documents'))

    def seed_invoices(self, years):
        """Seed invoices over time period"""
        self.stdout.write(f'Seeding invoices for {years} years...')
        
        outlets = list(Outlet.objects.all()[:100])  # Limit for performance
        users = list(User.objects.filter(role__in=['accountant', 'manager', 'admin']))
        admin_user = User.objects.filter(role='super_admin').first()
        
        if not users:
            users = [admin_user]
        
        current_date = date.today()
        start_date = current_date - timedelta(days=years * 365)
        
        invoice_counter = 1
        invoice_date = start_date
        
        while invoice_date <= current_date:
            # Create 20-50 invoices per month
            for _ in range(random.randint(20, 50)):
                outlet = random.choice(outlets)
                amount = Decimal(random.randint(5000, 50000))
                tax_amount = amount * Decimal('0.16')  # 16% VAT
                
                Invoice.objects.create(
                    invoice_number=f'INV{invoice_date.year}{str(invoice_counter).zfill(6)}',
                    invoice_type=random.choice(['payment', 'expense', 'allowance']),
                    outlet=outlet if random.choice([True, False]) else None,
                    vendor_name=outlet.name if outlet else f'Vendor {invoice_counter}',
                    amount=amount,
                    currency='KES',
                    tax_amount=tax_amount,
                    total_amount=amount + tax_amount,
                    invoice_date=invoice_date,
                    due_date=invoice_date + timedelta(days=30),
                    payment_date=invoice_date + timedelta(days=random.randint(1, 45)) if random.choice([True, False]) else None,
                    description=f'Payment for services - Period {invoice_date.strftime("%B %Y")}',
                    status=random.choice(['paid', 'paid', 'approved', 'pending']),
                    payment_method=random.choice(['bank_transfer', 'mpesa', 'cheque']),
                    created_by=random.choice(users)
                )
                invoice_counter += 1
            
            # Move to next month
            if invoice_date.month == 12:
                invoice_date = date(invoice_date.year + 1, 1, 1)
            else:
                invoice_date = date(invoice_date.year, invoice_date.month + 1, 1)
        
        invoice_count = Invoice.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {invoice_count} invoices'))

    def seed_budgets(self, years):
        """Seed budgets"""
        self.stdout.write(f'Seeding budgets for {years} years...')
        
        departments = Department.objects.all()
        admin_user = User.objects.filter(role='super_admin').first()
        
        current_year = date.today().year
        
        for year in range(current_year - years, current_year + 1):
            for dept in departments:
                allocated = Decimal(random.randint(500000, 5000000))
                spent = allocated * Decimal(str(random.uniform(0.5, 0.95))) if year < current_year else allocated * Decimal(str(random.uniform(0.1, 0.4)))
                
                Budget.objects.create(
                    name=f'{dept.name} Budget FY{year}',
                    budget_type='departmental',
                    fiscal_year=year,
                    department=dept,
                    allocated_amount=allocated,
                    spent_amount=spent,
                    committed_amount=Decimal(random.randint(10000, 100000)),
                    start_date=date(year, 1, 1),
                    end_date=date(year, 12, 31),
                    description=f'Annual budget for {dept.name} - FY {year}',
                    is_active=(year == current_year),
                    created_by=admin_user
                )
        
        budget_count = Budget.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {budget_count} budgets'))

    def seed_workflow_templates(self):
        """Seed workflow templates"""
        self.stdout.write('Seeding workflow templates...')
        
        admin_user = User.objects.filter(role='super_admin').first()
        
        workflows_data = [
            {
                'name': 'Price Entry Approval',
                'code': 'PRICE_APPROVAL',
                'applies_to': 'price_entry',
                'steps': [
                    {'step': 1, 'name': 'Field Officer Collection', 'role': 'field_officer'},
                    {'step': 2, 'name': 'Supervisor Verification', 'role': 'supervisor'},
                    {'step': 3, 'name': 'Manager Approval', 'role': 'manager'},
                ]
            },
            {
                'name': 'Document Approval',
                'code': 'DOC_APPROVAL',
                'applies_to': 'document',
                'steps': [
                    {'step': 1, 'name': 'Upload', 'role': 'data_entry'},
                    {'step': 2, 'name': 'Review', 'role': 'supervisor'},
                    {'step': 3, 'name': 'Approval', 'role': 'manager'},
                ]
            },
            {
                'name': 'Invoice Processing',
                'code': 'INV_PROCESS',
                'applies_to': 'invoice',
                'steps': [
                    {'step': 1, 'name': 'Creation', 'role': 'accountant'},
                    {'step': 2, 'name': 'Verification', 'role': 'manager'},
                    {'step': 3, 'name': 'Payment', 'role': 'accountant'},
                ]
            },
        ]
        
        for wf_data in workflows_data:
            wf_data['created_by'] = admin_user
            WorkflowTemplate.objects.create(**wf_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(workflows_data)} workflow templates'))

    def seed_training_modules(self):
        """Seed training modules"""
        self.stdout.write('Seeding training modules...')
        
        admin_user = User.objects.filter(role='super_admin').first()
        
        modules_data = [
            {'title': 'System Introduction', 'code': 'SYS101', 'category': 'system_basics', 'duration': 60, 'mandatory': True},
            {'title': 'Data Collection Basics', 'code': 'DATA101', 'category': 'data_collection', 'duration': 90, 'mandatory': True},
            {'title': 'Price Entry Methods', 'code': 'DATA201', 'category': 'data_collection', 'duration': 120, 'mandatory': True},
            {'title': 'Data Quality Assurance', 'code': 'DATA301', 'category': 'data_collection', 'duration': 90, 'mandatory': False},
            {'title': 'Statistical Analysis', 'code': 'ANLYS101', 'category': 'analysis', 'duration': 180, 'mandatory': False},
            {'title': 'Report Generation', 'code': 'RPT101', 'category': 'reporting', 'duration': 120, 'mandatory': False},
            {'title': 'System Administration', 'code': 'ADMIN101', 'category': 'administration', 'duration': 150, 'mandatory': False},
        ]
        
        for mod_data in modules_data:
            TrainingModule.objects.create(
                title=mod_data['title'],
                code=mod_data['code'],
                category=mod_data['category'],
                description=f'Training module for {mod_data["title"]}',
                content=f'Detailed content for {mod_data["title"]} will be provided here.',
                duration_minutes=mod_data['duration'],
                is_mandatory=mod_data['mandatory'],
                created_by=admin_user
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(modules_data)} training modules'))

    def seed_system_configuration(self):
        """Seed system configuration"""
        self.stdout.write('Seeding system configuration...')
        
        admin_user = User.objects.filter(role='super_admin').first()
        
        configs_data = [
            {'key': 'SYSTEM_NAME', 'value': 'DataPlus ERP', 'category': 'general', 'description': 'System name'},
            {'key': 'CURRENCY', 'value': 'KES', 'category': 'general', 'description': 'Default currency'},
            {'key': 'TIMEZONE', 'value': 'Africa/Nairobi', 'category': 'general', 'description': 'System timezone'},
            {'key': 'MAX_LOGIN_ATTEMPTS', 'value': '5', 'category': 'security', 'description': 'Maximum login attempts'},
            {'key': 'SESSION_TIMEOUT', 'value': '3600', 'category': 'security', 'description': 'Session timeout in seconds'},
            {'key': 'ENABLE_EMAIL_NOTIFICATIONS', 'value': 'true', 'category': 'email', 'description': 'Enable email notifications'},
            {'key': 'ENABLE_SMS_NOTIFICATIONS', 'value': 'false', 'category': 'sms', 'description': 'Enable SMS notifications'},
            {'key': 'MAX_FILE_SIZE', 'value': '5242880', 'category': 'storage', 'description': 'Max file upload size (5MB)'},
        ]
        
        for config_data in configs_data:
            config_data['updated_by'] = admin_user
            SystemConfiguration.objects.create(**config_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(configs_data)} system configurations'))

    def seed_data_quality_checks(self):
        """Seed data quality checks"""
        self.stdout.write('Seeding data quality checks...')
        
        admin_user = User.objects.filter(role='super_admin').first()
        
        checks_data = [
            {
                'name': 'Price Outlier Detection',
                'check_type': 'outlier',
                'applies_to_model': 'PriceEntry',
                'rule_definition': {'method': 'iqr', 'multiplier': 1.5},
                'threshold': Decimal('2.0'),
                'severity': 'high'
            },
            {
                'name': 'Missing Price Check',
                'check_type': 'completeness',
                'applies_to_model': 'OutletProduct',
                'rule_definition': {'field': 'last_price_date', 'max_days': 90},
                'severity': 'medium'
            },
            {
                'name': 'Duplicate Entry Check',
                'check_type': 'consistency',
                'applies_to_model': 'PriceEntry',
                'rule_definition': {'fields': ['outlet_product', 'period']},
                'severity': 'critical'
            },
            {
                'name': 'Price Range Validation',
                'check_type': 'accuracy',
                'applies_to_model': 'PriceEntry',
                'rule_definition': {'compare_to': 'reference_price', 'tolerance': 0.5},
                'threshold': Decimal('50.0'),
                'severity': 'high'
            },
        ]
        
        for check_data in checks_data:
            check_data['created_by'] = admin_user
            DataQualityCheck.objects.create(**check_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(checks_data)} data quality checks'))

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('DATA SEEDING SUMMARY'))
        self.stdout.write('='*60)
        
        summary = [
            ('Departments', Department.objects.count()),
            ('Users', User.objects.count()),
            ('Baskets', Basket.objects.count()),
            ('Zones', Zone.objects.count()),
            ('Outlet Types', OutletType.objects.count()),
            ('Outlets', Outlet.objects.count()),
            ('Divisions', Division.objects.count()),
            ('COICOP Categories', COICOPCategory.objects.count()),
            ('Products', Product.objects.count()),
            ('Price Periods', PricePeriod.objects.count()),
            ('Outlet Products', OutletProduct.objects.count()),
            ('Price Entries', PriceEntry.objects.count()),
            ('Document Categories', DocumentCategory.objects.count()),
            ('Documents', Document.objects.count()),
            ('Invoices', Invoice.objects.count()),
            ('Budgets', Budget.objects.count()),
            ('Workflow Templates', WorkflowTemplate.objects.count()),
            ('Training Modules', TrainingModule.objects.count()),
            ('System Configurations', SystemConfiguration.objects.count()),
            ('Data Quality Checks', DataQualityCheck.objects.count()),
        ]
        
        for label, count in summary:
            self.stdout.write(f'{label:.<40} {count:>10,}')
        
        self.stdout.write('='*60)
        self.stdout.write('\nDefault login credentials:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: password123')
        self.stdout.write('\nAll other users also use password: password123')
        self.stdout.write('='*60 + '\n')