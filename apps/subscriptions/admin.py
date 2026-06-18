"""Subscription admin."""
from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'amount', 'paid_at', 'expires_at']
    list_filter = ['plan', 'payment_method']
    search_fields = ['organization__name']
