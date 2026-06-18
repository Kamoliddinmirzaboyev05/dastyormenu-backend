"""Menu URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menu', MenuViewSet, basename='menu')

urlpatterns = [
    path('', include(router.urls)),
]
