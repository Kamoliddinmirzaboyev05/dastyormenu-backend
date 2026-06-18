#!/bin/bash

echo "🚀 Setting up Dastyor Backend..."

# Wait for postgres
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready!"

# Wait for redis
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "✅ Redis is ready!"

# Run migrations
echo "📦 Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo "👤 Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dastyor.uz', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
END

echo "✅ Setup complete!"
