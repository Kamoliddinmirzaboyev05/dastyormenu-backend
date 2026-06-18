"""Organization admin."""
from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'subscription_plan', 'subscription_status', 'created_at']
    list_filter = ['subscription_plan', 'subscription_status']
    search_fields = ['name', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at']
