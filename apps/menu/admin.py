"""Menu admin."""
from django.contrib import admin
from .models import Category, Menu


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'sort_order', 'is_active']
    list_filter = ['is_active', 'organization']
    search_fields = ['name']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'organization']
    list_filter = ['is_available', 'category', 'organization']
    search_fields = ['name', 'description']
