"""Main URL configuration."""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.menu.public_views import public_menu

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation - Root URL
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Public endpoints (no auth)
    path('api/public/menu/', public_menu, name='public-menu'),
    
    # Auth endpoints
    path('api/', include('apps.users.urls')),
    
    # Protected endpoints
    path('api/organizations/', include('apps.organizations.urls')),
    path('api/', include('apps.menu.urls')),
    path('api/tables/', include('apps.tables.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Serve media files in production (Railway)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
