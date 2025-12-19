# DataPlus ERP - Enterprise Resource Planning System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-red.svg)

**DataPlus ERP** is a comprehensive enterprise resource planning system designed for advanced statistical data collection and analysis, with specialized features for price monitoring, outlet management, and multi-level organizational workflows.

## 🌟 Key Features

### Core Capabilities
- **Role-Based Access Control** - Multi-level permission system with 10 distinct user roles
- **Document Management** - Complete version control, digital signatures, and approval workflows
- **Price Collection System** - Comprehensive price monitoring with photo evidence and GPS tracking
- **Outlet Management** - Full outlet lifecycle management with verification workflows
- **Financial Management** - Invoice processing, budget tracking, and payment management
- **Workflow Engine** - Configurable approval processes with multi-step workflows
- **Training & Capacity Building** - Integrated learning management with certificates
- **Advanced Analytics** - Real-time reporting with customizable dashboards
- **Audit Trail** - Complete system activity tracking and compliance monitoring
- **Multi-Currency & Multi-Language** - International support built-in

### Technical Highlights
- Built on Django 4.2+ with Python 3.10+
- PostgreSQL/MySQL database support
- RESTful API with comprehensive endpoints
- Cloud-ready architecture
- Real-time notifications (Email & SMS)
- Advanced file management with CDN integration
- Data quality validation engine
- Scheduled report generation

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Models Overview](#models-overview)
- [Admin Interface](#admin-interface)
- [User Roles & Permissions](#user-roles--permissions)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites
```bash
- Python 3.10 or higher
- PostgreSQL 13+ or MySQL 8.0+
- Redis (for caching and task queue)
- Node.js & npm (for frontend assets)
```

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourorg/dataplus-erp.git
cd dataplus-erp
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=dataplus_erp
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SMS Gateway
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=DATAPLUS

# File Storage
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static
USE_S3=False  # Set to True for AWS S3

# AWS S3 (if USE_S3=True)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### Step 5: Database Setup
```bash
# Create database
createdb dataplus_erp

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata initial_data.json
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000/admin/` to access the admin interface.

## ⚙️ Configuration

### Initial System Setup

1. **Create Departments**
   ```python
   from myapp.models import Department
   
   dept = Department.objects.create(
       code='IT',
       name='Information Technology',
       description='IT Department'
   )
   ```

2. **Create User Roles**
   ```python
   from myapp.models import User
   
   user = User.objects.create_user(
       username='john.doe',
       email='john@example.com',
       employee_id='EMP001',
       role='data_entry',
       department=dept
   )
   ```

3. **Configure System Settings**
   ```python
   from myapp.models import SystemConfiguration
   
   SystemConfiguration.objects.create(
       key='max_file_upload_size',
       value='10485760',  # 10MB in bytes
       category='storage'
   )
   ```

## 📊 Models Overview

### User Management
- **User** - Extended Django user with comprehensive profile
- **Department** - Organizational structure with hierarchy
- **Role-Based Permissions** - Granular access control

### Geographical Hierarchy
- **Basket** - Top-level geographical grouping
- **Zone** - Geographical zones within baskets
- **Outlet** - Physical locations for data collection

### Product Classification
- **Division** - Product classification hierarchy
- **COICOPCategory** - International standard classification
- **Product** - Master product catalog with full specifications

### Price Collection
- **PricePeriod** - Survey periods with tracking
- **OutletProduct** - Junction table with availability
- **PriceEntry** - Individual price observations
- **PriceEvidence** - Photo evidence with GPS

### Document Management
- **DocumentCategory** - Document organization
- **Document** - Universal document storage with versioning
- **DocumentVersion** - Version control system

### Financial Management
- **Invoice** - Comprehensive invoice management
- **Budget** - Budget planning and tracking

### Workflow & Approvals
- **WorkflowTemplate** - Configurable workflow definitions
- **WorkflowInstance** - Active workflow executions
- **ApprovalAction** - Individual approval steps

### Training & Capacity
- **TrainingModule** - Training content management
- **UserTraining** - User training completion tracking

### Analytics & Reporting
- **GeneratedReport** - Stored report files
- **SavedReport** - Reusable report templates

### Audit & Compliance
- **AuditLog** - Complete system activity log
- **DataQualityCheck** - Validation rules
- **DataQualityIssue** - Detected quality issues

## 🎛️ Admin Interface

The Django admin interface provides comprehensive management capabilities:

### Dashboard Features
- **Statistics Overview** - Real-time system metrics
- **Quick Actions** - Common administrative tasks
- **Recent Activity** - Latest system changes
- **Notifications** - Important alerts and reminders

### Advanced Features
- **Bulk Operations** - Process multiple records simultaneously
- **Export Functions** - CSV, Excel, PDF exports
- **Import Tools** - Bulk data import with validation
- **Advanced Filters** - Multi-field filtering and search
- **Inline Editing** - Edit related objects on the same page
- **Custom Actions** - Role-specific administrative actions

### Accessing the Admin
```
URL: http://yourdomain.com/admin/
Username: Your superuser username
Password: Your superuser password
```

## 👥 User Roles & Permissions

### Role Hierarchy

1. **Super Administrator**
   - Full system access
   - User management
   - System configuration
   - All data operations

2. **Administrator**
   - User management (limited)
   - Department management
   - Report generation
   - Data approval

3. **Supervisor**
   - Zone management
   - User supervision
   - Data verification
   - Report access

4. **Data Entry Officer**
   - Price entry
   - Outlet updates
   - Document uploads
   - Basic reporting

5. **Field Officer**
   - Mobile data collection
   - Outlet verification
   - Photo evidence upload
   - GPS tracking

6. **Data Analyst**
   - Report generation
   - Data analysis
   - Export capabilities
   - Read-only access

7. **Accountant**
   - Financial management
   - Invoice processing
   - Budget tracking
   - Payment approval

8. **Auditor**
   - Audit log access
   - Compliance checking
   - Quality assurance
   - Read-only system access

9. **Manager**
   - Department oversight
   - Budget management
   - Staff management
   - Strategic reporting

10. **Viewer**
    - Read-only access
    - Basic reporting
    - Dashboard access
    - No edit capabilities

### Custom Permissions
```python
# In your User model
user.can_approve_prices = True
user.can_generate_reports = True
user.can_export_data = True
user.can_manage_users = False
user.can_manage_finances = False
user.save()
```

## 🔌 API Documentation

### Authentication
```bash
# Token-based authentication
POST /api/auth/login/
{
  "username": "john.doe",
  "password": "secure_password"
}

Response:
{
  "token": "your-auth-token",
  "user": {...}
}
```

### Common Endpoints

#### Users
```bash
GET    /api/users/              # List users
POST   /api/users/              # Create user
GET    /api/users/{id}/         # Get user details
PUT    /api/users/{id}/         # Update user
DELETE /api/users/{id}/         # Delete user
```

#### Outlets
```bash
GET    /api/outlets/            # List outlets
POST   /api/outlets/            # Create outlet
GET    /api/outlets/{id}/       # Get outlet details
PUT    /api/outlets/{id}/       # Update outlet
```

#### Prices
```bash
GET    /api/prices/             # List price entries
POST   /api/prices/             # Create price entry
GET    /api/prices/{id}/        # Get price details
PUT    /api/prices/{id}/        # Update price
POST   /api/prices/{id}/approve/ # Approve price
```

#### Documents
```bash
GET    /api/documents/          # List documents
POST   /api/documents/          # Upload document
GET    /api/documents/{id}/     # Get document
DELETE /api/documents/{id}/     # Delete document
GET    /api/documents/{id}/download/ # Download file
```

## 💡 Usage Examples

### Creating a Price Entry
```python
from myapp.models import PriceEntry, OutletProduct, PricePeriod

# Get references
outlet_product = OutletProduct.objects.get(id=1)
period = PricePeriod.objects.get(period_name='January 2025')
user = User.objects.get(username='field_officer')

# Create price entry
price = PriceEntry.objects.create(
    outlet_product=outlet_product,
    period=period,
    price=150.00,
    collected_date='2025-01-15',
    collected_by=user,
    status='submitted',
    notes='Regular collection'
)
```

### Uploading Document with Version Control
```python
from myapp.models import Document, DocumentCategory

category = DocumentCategory.objects.get(code='REPORT')

doc = Document.objects.create(
    title='Q4 2024 Report',
    document_number='DOC-2024-001',
    document_type='report',
    category=category,
    file=uploaded_file,
    document_date='2024-12-31',
    uploaded_by=request.user,
    status='pending_review'
)
```

### Creating Workflow
```python
from myapp.models import WorkflowTemplate, WorkflowInstance

# Create template
template = WorkflowTemplate.objects.create(
    name='Price Approval Workflow',
    code='PRICE_APPROVAL',
    applies_to='price_entry',
    steps=[
        {'step': 1, 'role': 'supervisor', 'action': 'review'},
        {'step': 2, 'role': 'manager', 'action': 'approve'}
    ]
)

# Create instance
instance = WorkflowInstance.objects.create(
    workflow_template=template,
    content_type=ContentType.objects.get_for_model(PriceEntry),
    object_id=price.id,
    initiated_by=user
)
```

## 🛠️ Development

### Project Structure
```
dataplus-erp/
├── myapp/
│   ├── models.py           # Database models
│   ├── admin.py            # Admin configuration
│   ├── views.py            # View logic
│   ├── serializers.py      # API serializers
│   ├── urls.py             # URL routing
│   ├── forms.py            # Django forms
│   ├── signals.py          # Django signals
│   ├── tasks.py            # Celery tasks
│   ├── utils.py            # Utility functions
│   └── tests/              # Test suite
├── templates/              # HTML templates
├── static/                 # Static files
├── media/                  # User uploads
├── config/                 # Configuration files
├── requirements.txt        # Python dependencies
├── manage.py               # Django management
└── README.md               # This file
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test myapp.tests.test_models

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Style
```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🧪 Testing

### Unit Tests
```python
from django.test import TestCase
from myapp.models import User, Department

class UserModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            code='IT',
            name='IT Department'
        )
    
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            employee_id='EMP001',
            department=self.dept
        )
        self.assertEqual(user.username, 'testuser')
```

### Integration Tests
```python
from django.test import Client, TestCase

class PriceEntryTest(TestCase):
    def test_create_price_entry(self):
        client = Client()
        response = client.post('/api/prices/', {
            'outlet_product': 1,
            'period': 1,
            'price': 150.00
        })
        self.assertEqual(response.status_code, 201)
```

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up SSL/HTTPS
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure email settings
- [ ] Set up backup strategy
- [ ] Configure logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure static file serving
- [ ] Set up CDN for media files

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=dataplus_erp
      - POSTGRES_USER=dataplus
      - POSTGRES_PASSWORD=secure_password

  redis:
    image: redis:6-alpine

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Running with Docker
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 📝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Add docstrings to functions
- Keep commits atomic and descriptive

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support and questions:

- **Email**: support@dataplus-erp.com
- **Documentation**: https://docs.dataplus-erp.com
- **Issue Tracker**: https://github.com/yourorg/dataplus-erp/issues
- **Slack Community**: [Join our Slack](https://slack.dataplus-erp.com)

## 🙏 Acknowledgments

- Django Software Foundation
- All contributors and maintainers
- Open source community

## 📊 Changelog

### Version 1.0.0 (2025-01-15)
- Initial release
- Complete ERP functionality
- Admin interface
- API endpoints
- Documentation

---

**Made with ❤️ by the DataPlus Team**