# Dastyor Backend - Project Structure

```
DastyorMenuBackend/
│
├── config/                          # Project configuration
│   ├── __init__.py                 # Celery app import
│   ├── asgi.py                     # ASGI config for WebSocket
│   ├── wsgi.py                     # WSGI config
│   ├── celery.py                   # Celery configuration
│   ├── routing.py                  # WebSocket URL routing
│   ├── urls.py                     # Main URL configuration
│   ├── exceptions.py               # Custom exception handler
│   └── settings/
│       ├── __init__.py
│       ├── base.py                 # Base settings
│       ├── development.py          # Development settings
│       └── production.py           # Production settings
│
├── apps/                           # Django applications
│   │
│   ├── organizations/              # Tenant management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Organization model
│   │   ├── serializers.py         # Organization serializers
│   │   ├── views.py               # Organization ViewSet
│   │   ├── urls.py
│   │   ├── signals.py             # Trial period setup
│   │   └── admin.py
│   │
│   ├── users/                      # Authentication & user profiles
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # UserProfile model
│   │   ├── serializers.py         # User, Login, PIN serializers
│   │   ├── views.py               # Auth views, UserProfile ViewSet
│   │   ├── urls.py
│   │   ├── permissions.py         # Custom permission classes
│   │   └── admin.py
│   │
│   ├── menu/                       # Menu & categories
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Category, Menu models
│   │   ├── serializers.py         # Menu serializers
│   │   ├── views.py               # Category, Menu ViewSets
│   │   ├── urls.py
│   │   ├── mixins.py              # OrganizationMixin (tenant isolation)
│   │   ├── public_views.py        # Public menu endpoint (QR)
│   │   └── admin.py
│   │
│   ├── tables/                     # Tables & QR codes
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Table model with QR generation
│   │   ├── serializers.py         # Table serializers
│   │   ├── views.py               # Table ViewSet
│   │   ├── urls.py
│   │   ├── signals.py             # Auto QR generation
│   │   └── admin.py
│   │
│   ├── orders/                     # Order management
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Order, OrderItem models
│   │   ├── serializers.py         # Order serializers (public & private)
│   │   ├── views.py               # Order ViewSet, public endpoints
│   │   ├── urls.py
│   │   ├── consumers.py           # OrderConsumer (WebSocket)
│   │   ├── signals.py             # Order status change handlers
│   │   └── admin.py
│   │
│   ├── payments/                   # Payment processing
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Payment model
│   │   ├── serializers.py         # Payment serializers
│   │   ├── views.py               # Payment ViewSet
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── notifications/              # Notification system
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Notification model
│   │   ├── serializers.py         # Notification serializers
│   │   ├── views.py               # Notification ViewSet
│   │   ├── urls.py
│   │   ├── consumers.py           # NotificationConsumer (WebSocket)
│   │   └── admin.py
│   │
│   └── subscriptions/              # Billing & subscriptions
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py              # Subscription model
│       ├── serializers.py         # Subscription serializers
│       ├── views.py               # Subscription ViewSet
│       ├── urls.py
│       ├── tasks.py               # Celery tasks (expiration check)
│       └── admin.py
│
├── scripts/
│   └── setup.sh                    # Setup script for Docker
│
├── media/                          # User uploaded files
├── staticfiles/                    # Collected static files
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker services configuration
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
└── STRUCTURE.md                    # This file

```

## Key Components

### 1. Multi-Tenancy (Tenant Isolation)
- **OrganizationMixin** (`apps/menu/mixins.py`): Ensures data isolation between organizations
- All models have `organization` ForeignKey
- ViewSets filter by user's organization automatically

### 2. Authentication
- **Email/Password**: Standard Django auth for managers
- **PIN Login**: 4-digit PIN for chefs/waiters (bcrypt hashed)
- **JWT Tokens**: djangorestframework-simplejwt

### 3. Real-Time Features (WebSocket)
- **OrderConsumer**: Kitchen receives real-time order updates
- **NotificationConsumer**: Staff receives notifications
- JWT authentication via query params

### 4. QR Code System
- Each table has unique QR code
- QR links to: `https://dastyor.uz/menu?qr={qr_code_id}`
- Auto-generated on table creation
- Can be regenerated if needed

### 5. Order Flow
1. Customer scans QR → Gets menu
2. Customer creates order → Saved to DB
3. Signal triggers → WebSocket broadcast to kitchen
4. Chef updates status → Waiter notified
5. Order completed → Payment created

### 6. Celery Tasks
- **check_expired_subscriptions**: Daily task to deactivate expired subscriptions
- Runs at midnight via Celery Beat

### 7. Permissions
- `IsSuperAdmin`: Full access
- `IsManagerOrAbove`: Manager + Super Admin
- `IsChefOrAbove`: Chef + Manager + Super Admin
- `IsWaiterOrAbove`: All authenticated staff
- `IsOwnOrganization`: Object-level permission

## Database Models

### Core Models
- **Organization**: Restaurant/cafe (tenant)
- **UserProfile**: Extended user with role & organization
- **Category**: Menu category
- **Menu**: Menu item (dish)
- **Table**: Restaurant table with QR
- **Order**: Customer order
- **OrderItem**: Items in order
- **Payment**: Payment record
- **Notification**: User notification
- **Subscription**: Subscription history

### Relationships
```
Organization (1) ──→ (N) UserProfile
Organization (1) ──→ (N) Category
Organization (1) ──→ (N) Menu
Organization (1) ──→ (N) Table
Organization (1) ──→ (N) Order

Category (1) ──→ (N) Menu
Table (1) ──→ (N) Order
UserProfile (1) ──→ (N) Order (as waiter)
Order (1) ──→ (N) OrderItem
Order (1) ──→ (N) Payment
```

## API Architecture

### REST Endpoints
- Standard CRUD via ViewSets
- Pagination: 20 items per page
- Filtering: django-filter
- Search: DRF SearchFilter
- Documentation: drf-spectacular (Swagger)

### WebSocket Endpoints
- `/ws/orders/` - Real-time order updates
- `/ws/notifications/` - Real-time notifications

### Public Endpoints (No Auth)
- `/api/public/menu/` - Get menu via QR
- `/api/public/orders/` - Create order
- `/api/public/orders/{id}/status/` - Check order status

## Deployment

### Docker Services
- **web**: Django + Daphne (ASGI)
- **celery**: Background task worker
- **celery-beat**: Periodic task scheduler
- **postgres**: Database
- **redis**: Cache + Channel layer
- **minio**: S3-compatible storage

### Environment
- Development: `config.settings.development`
- Production: `config.settings.production`

## Next Steps

1. Run migrations: `docker-compose exec web python manage.py migrate`
2. Create superuser: `docker-compose exec web python manage.py createsuperuser`
3. Access API docs: http://localhost:8000/api/docs/
4. Test WebSocket: Use Postman or wscat
5. Upload menu images via admin or API
6. Generate QR codes for tables
7. Test order flow end-to-end
