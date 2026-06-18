"""Notification admin."""
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['type', 'recipient', 'message', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'organization']
    search_fields = ['message', 'recipient__full_name']
