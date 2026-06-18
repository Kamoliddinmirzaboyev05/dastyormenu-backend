# Dastyor - Restaurant SaaS Backend

Multi-tenant restaurant management system with real-time order tracking, QR code menu access, and comprehensive staff management.

## Tech Stack

- **Backend**: Django 5.x + Django REST Framework
- **WebSocket**: Django Channels + Daphne
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **Storage**: ImgBB (Free Image Hosting) / MinIO (S3-compatible)
- **Containerization**: Docker + Docker Compose

## Features

- 🏢 Multi-tenant organization management
- 👥 Role-based access control (Super Admin, Manager, Chef, Waiter)
- 📱 QR code table access for customers
- 🍽️ Menu management with categories
- 📋 Real-time order tracking via WebSocket
- 💳 Payment processing (Cash, Click, Payme, Card)
- 🔔 Real-time notifications
- 📊 Subscription management
- 📈 Dashboard analytics

## Project Structure

```
DastyorMenuBackend/
├── config/                 # Project configuration
│   ├── settings/          # Split settings (base, dev, prod)
│   ├── asgi.py           # ASGI config for WebSocket
│   ├── celery.py         # Celery configuration
│   ├── routing.py        # WebSocket routing
│   └── urls.py           # Main URL configuration
├── apps/
│   ├── organizations/    # Tenant management
│   ├── users/           # Authentication & profiles
│   ├── menu/            # Menu & categories
│   ├── tables/          # Table & QR codes
│   ├── orders/          # Order management
│   ├── payments/        # Payment processing
│   ├── notifications/   # Notification system
│   └── subscriptions/   # Billing & subscriptions
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd DastyorMenuBackend
cp .env.example .env
```

### 2. Setup ImgBB (Image Storage) 🖼️

**MUHIM:** Rasmlar uchun ImgBB allaqachon sozlangan!

ImgBB API key `.env` faylida mavjud:
```bash
IMGBB_API_KEY=your-imgbb-api-key
```

✅ Uzbekistonda ishlaydi
✅ Bepul va cheklovsiz
✅ Tez va oson

📖 **Batafsil qo'llanma:** `IMGBB_SETUP.md`

### 3. Start with Docker

```bash
docker-compose up -d
```

### 3. Run Migrations

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 4. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Access Services

- **API**: http://localhost:8000/api/
- **Swagger Docs**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/
- **MinIO Console**: http://localhost:9001/

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Email/password login
- `POST /api/auth/pin-login/` - PIN login (chef/waiter)
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - Logout

### Public (No Auth)
- `GET /api/public/menu/?qr={qr_code_id}` - Get menu via QR
- `POST /api/public/orders/` - Create order (customer)
- `GET /api/public/orders/{id}/status/` - Check order status

### Organizations
- `GET/POST /api/organizations/`
- `GET/PUT/DELETE /api/organizations/{id}/`

### Users
- `GET/POST /api/users/`
- `GET/PUT/DELETE /api/users/{id}/`
- `POST /api/users/{id}/set-pin/`

### Menu
- `GET/POST /api/categories/`
- `GET/POST /api/menu/`
- `POST /api/menu/{id}/toggle-availability/`

### Tables
- `GET/POST /api/tables/`
- `GET /api/tables/{id}/qr-code/` - Download QR
- `POST /api/tables/{id}/regenerate-qr/`

### Orders
- `GET/POST /api/orders/`
- `POST /api/orders/{id}/update-status/`
- `GET /api/orders/active/` - Active orders (kitchen)
- `GET /api/orders/my-tables/` - Waiter's orders

### Payments
- `GET/POST /api/payments/`
- `POST /api/payments/{id}/confirm/`

### Notifications
- `GET /api/notifications/`
- `POST /api/notifications/{id}/mark-read/`
- `POST /api/notifications/mark-all-read/`

### Subscriptions
- `GET /api/subscriptions/current/`
- `GET /api/subscriptions/history/`

## WebSocket Endpoints

### Orders (Kitchen)
```
ws://localhost:8000/ws/orders/?token={access_token}
```

### Notifications
```
ws://localhost:8000/ws/notifications/?token={access_token}
```

## Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb dastyor_db

# Run migrations
python manage.py migrate

# Start Redis (required for Channels & Celery)
redis-server

# Start Celery worker (in separate terminal)
celery -A config worker -l info

# Start Celery beat (in separate terminal)
celery -A config beat -l info

# Run development server
python manage.py runserver
```

### Run Tests

```bash
python manage.py test
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database credentials
- `REDIS_HOST`, `REDIS_PORT` - Redis connection
- `IMGBB_API_KEY` - ImgBB image hosting API key (already configured)
- `AWS_*` - S3/MinIO storage configuration (alternative)

## Deployment

### Production Settings

1. Set `DJANGO_SETTINGS_MODULE=config.settings.production`
2. Configure environment variables
3. Set `DEBUG=False`
4. Configure proper `ALLOWED_HOSTS`
5. Use production-grade database
6. Setup SSL certificates
7. Configure CDN for static/media files

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## License

Proprietary - All rights reserved

## Support

For support, contact: support@dastyor.uz
