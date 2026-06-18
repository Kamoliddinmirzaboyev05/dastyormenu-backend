"""Order admin."""
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['menu_name', 'menu_price', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'organization', 'created_at']
    search_fields = ['id', 'table__table_number']
    inlines = [OrderItemInline]
    readonly_fields = ['total_with_tip']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_name', 'quantity', 'menu_price', 'item_status']
    list_filter = ['item_status']
