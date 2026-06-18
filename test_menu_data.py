"""Create test menu data."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.organizations.models import Organization
from apps.menu.models import Category, Menu

# Get or create organization
org, _ = Organization.objects.get_or_create(
    name='Test Restaurant',
    defaults={
        'phone': '+998901234567',
        'address': 'Toshkent, Amir Temur ko\'chasi',
        'subscription_plan': 'trial',
        'subscription_status': True,
    }
)

# Create categories
cat1, _ = Category.objects.get_or_create(
    organization=org,
    name='Asosiy taomlar',
    defaults={'icon': '🍽️', 'sort_order': 1}
)

cat2, _ = Category.objects.get_or_create(
    organization=org,
    name='Salatlar',
    defaults={'icon': '🥗', 'sort_order': 2}
)

# Create menu items
menu1, created = Menu.objects.get_or_create(
    organization=org,
    name='Osh',
    defaults={
        'category': cat1,
        'description': 'O\'zbek milliy taomi, guruch va go\'sht bilan',
        'ingredients': 'Guruch, go\'sht, sabzi, piyoz, zira',
        'price': 2500000,  # 25000 UZS in tiyin
        'cook_time_minutes': 15,
        'is_available': True,
        'sort_order': 1,
    }
)

menu2, created = Menu.objects.get_or_create(
    organization=org,
    name='Lag\'mon',
    defaults={
        'category': cat1,
        'description': 'Qo\'l bilan cho\'zilgan xamir va go\'sht',
        'ingredients': 'Xamir, go\'sht, sabzavotlar, sous',
        'price': 3000000,  # 30000 UZS in tiyin
        'cook_time_minutes': 20,
        'is_available': True,
        'sort_order': 2,
    }
)

menu3, created = Menu.objects.get_or_create(
    organization=org,
    name='Achichuk salat',
    defaults={
        'category': cat2,
        'description': 'Yangi pomidor va piyoz salati',
        'ingredients': 'Pomidor, piyoz, ko\'katlar, zaytun moyi',
        'price': 800000,  # 8000 UZS in tiyin
        'cook_time_minutes': 5,
        'is_available': True,
        'sort_order': 1,
    }
)

print(f"✅ Organization: {org.name}")
print(f"✅ Categories: {Category.objects.filter(organization=org).count()}")
print(f"✅ Menu items: {Menu.objects.filter(organization=org).count()}")
print("\n📋 Menu items:")
for item in Menu.objects.filter(organization=org):
    print(f"  - {item.name}: {item.description[:50]}... ({item.price_uzs} UZS)")
