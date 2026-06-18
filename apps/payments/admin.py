"""Payment admin."""
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['payment_method', 'payment_status', 'organization']
    search_fields = ['id', 'transaction_id', 'order__id']
