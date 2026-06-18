"""Table admin."""
from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'organization', 'assigned_waiter', 'is_active']
    list_filter = ['is_active', 'organization']
    search_fields = ['table_number']
    readonly_fields = ['qr_code_id', 'qr_code_image']
